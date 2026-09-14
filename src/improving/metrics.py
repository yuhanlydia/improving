"""Finite-sample evaluation of correct coding completions.

The AST fingerprint is an *implementation proxy*, never an algorithm label.
Semantic coverage requires independently supplied, complete ``strategy_id``
annotations for the correct samples of each task. No function selects training
examples or mutates completion records.
"""

from __future__ import annotations

import ast
from collections import Counter
from collections.abc import Iterable, Mapping
import hashlib
import io
import json
import math
from numbers import Integral, Real
import tokenize
from typing import Any

import numpy as np


PROXY_VERSION = "python-ast-conservative-locals-v1"
CONTROL_FLOW_PROXY_VERSION = "python-ast-control-flow-v1"
EXACT_PROGRAM_VERSION = "stripped-source-sha256-v1"
LEXICAL_VERSION = "python-token-set-jaccard-v1"
METRIC_VERSIONS = {
    "implementation_proxy": PROXY_VERSION,
    "exact_program": EXACT_PROGRAM_VERSION,
    "control_flow_proxy": CONTROL_FLOW_PROXY_VERSION,
    "lexical": LEXICAL_VERSION,
}


def _integer(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return int(value)


def pass_at_k(n: int, c: int, k: int) -> float:
    """Estimate pass@k by 1 - C(n-c,k)/C(n,k), without replacement.

    This is the usual unbiased estimator of independent-draw pass@k when the
    observed n completions are IID. Its finite-pool interpretation is exact.
    k=0 returns zero; k>n raises instead of silently changing the budget.
    """
    n, c, k = _integer(n, "n"), _integer(c, "c"), _integer(k, "k")
    if c > n or k > n:
        raise ValueError("c and k must not exceed n")
    if c == 0 or k == 0:
        return 0.0
    if k > n - c:
        return 1.0
    # Symmetry lets us use the shorter product. log1p/expm1 also avoid
    # cancellation when the success probability is very small.
    short, excluded = min(c, k), max(c, k)
    def log_factor(i: int) -> float:
        fraction = excluded / (n - i)
        # A ratio strictly below one can round to one for large integers.
        # Its success probability already rounds to one at float precision.
        return -math.inf if fraction == 1.0 else math.log1p(-fraction)
    log_miss = math.fsum(log_factor(i) for i in range(short))
    return -math.expm1(log_miss)


def coverage_at_k(counts: Mapping[Any, int] | Iterable[int], total: int, k: int) -> float:
    """Expected distinct correct labels in k draws from *all* total samples.

    counts holds the frequencies of mutually exclusive correct labels; wrong
    draws remain in total. Returns sum_j [1 - C(total-n_j,k)/C(total,k)].
    Use total=sum(counts) only for an explicitly correct-count-matched metric.
    """
    total, k = _integer(total, "total"), _integer(k, "k")
    if k > total:
        raise ValueError("k must not exceed total")
    values = counts.values() if isinstance(counts, Mapping) else counts
    values = [_integer(value, "label count") for value in values]
    if sum(values) > total:
        raise ValueError("sum of label counts must not exceed total")
    return math.fsum(pass_at_k(total, count, k) for count in values)


class _RenameLocals(ast.NodeTransformer):
    def __init__(self, names: dict[str, str]):
        self.names = names

    def visit_Name(self, node: ast.Name) -> ast.Name:
        node.id = self.names.get(node.id, node.id)
        return node

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> ast.ExceptHandler:
        if node.name is not None:
            node.name = self.names.get(node.name, node.name)
        return self.generic_visit(node)


class _ConservativeCanonicalizer(ast.NodeTransformer):
    """Normalize only simple lexical function scopes; preserve uncertain ones.

    Nested scopes, imports, global/nonlocal declarations, comprehensions,
    pattern matching, and dynamic namespace access disable renaming for that
    function. External names, attributes, constants, and operators survive.
    This deliberately misses some equivalent programs rather than guessing
    about their binding structure. It is not a semantic-equivalence test.
    """

    @staticmethod
    def _strip_docstring(node: Any) -> None:
        body = getattr(node, "body", None)
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            if isinstance(body[0].value.value, str):
                del body[0]

    def visit_Module(self, node: ast.Module) -> ast.Module:
        self._strip_docstring(node)
        return self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        self._strip_docstring(node)
        # Class bodies can have unusual namespace semantics; preserve names.
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        self._strip_docstring(node)
        nodes = [child for statement in node.body for child in ast.walk(statement)]
        unsafe = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda,
                  ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp,
                  ast.Global, ast.Nonlocal, ast.Import, ast.ImportFrom, ast.Match)
        if any(isinstance(child, unsafe) for child in nodes):
            return node
        if any(isinstance(child, ast.Name) and child.id in {"locals", "globals", "eval", "exec", "vars"}
               for child in nodes):
            return node
        arguments = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
        if node.args.vararg:
            arguments.append(node.args.vararg)
        if node.args.kwarg:
            arguments.append(node.args.kwarg)
        ordered = [arg.arg for arg in arguments]
        for child in nodes:
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                ordered.append(child.id)
            elif isinstance(child, ast.ExceptHandler) and child.name:
                ordered.append(child.name)
        # Invalid source identifiers cannot collide with the canonical tokens.
        names = {name: f"<local:{index}>" for index, name in enumerate(dict.fromkeys(ordered))}
        for arg in arguments:
            arg.arg = names[arg.arg]
        renamer = _RenameLocals(names)
        node.body = [renamer.visit(statement) for statement in node.body]
        return node

    visit_AsyncFunctionDef = visit_FunctionDef


def implementation_proxy(code: str) -> str | None:
    """Hash conservatively normalized Python syntax, or None if unparseable.

    Formatting and docstrings are ignored; simple local names are normalized.
    Function names, external identifiers, and uncertain scopes are retained.
    An AST collision is not evidence of a shared true algorithm, and distinct
    fingerprints are not evidence of different algorithms.
    """
    if not isinstance(code, str):
        return None
    try:
        tree = ast.parse(code)
        tree = _ConservativeCanonicalizer().visit(tree)
        canonical = ast.dump(tree, annotate_fields=True, include_attributes=False)
    except (SyntaxError, ValueError, TypeError, RecursionError):
        return None
    return hashlib.sha256((PROXY_VERSION + "\n" + canonical).encode("utf-8")).hexdigest()


def control_flow_proxy(code: str) -> str | None:
    """Hash the ordered control-flow node skeleton of valid Python source."""
    if not isinstance(code, str):
        return None
    control_nodes = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With,
                     ast.AsyncWith, ast.ListComp, ast.SetComp, ast.DictComp,
                     ast.GeneratorExp, ast.BoolOp, ast.Match)
    try:
        skeleton = [type(node).__name__ for node in ast.walk(ast.parse(code))
                    if isinstance(node, control_nodes)]
    except (SyntaxError, ValueError, TypeError, RecursionError):
        return None
    return hashlib.sha256((CONTROL_FLOW_PROXY_VERSION + "\n" + json.dumps(skeleton)).encode()).hexdigest()


def _token_set(code: str) -> set[str] | None:
    try:
        ignored = {tokenize.ENCODING, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
                   tokenize.DEDENT, tokenize.COMMENT, tokenize.ENDMARKER}
        return {token.string for token in tokenize.generate_tokens(io.StringIO(code).readline)
                if token.type not in ignored}
    except (IndentationError, SyntaxError, tokenize.TokenError):
        return None


def _pairwise_token_jaccard(codes: list[str]) -> float | None:
    sets = [_token_set(code) for code in codes]
    if len(sets) < 2 or any(tokens is None for tokens in sets):
        return None
    distances = []
    for index, left in enumerate(sets):
        for right in sets[index + 1:]:
            union = left | right
            distances.append(1 - len(left & right) / len(union) if union else 0.0)
    return math.fsum(distances) / len(distances)


def _label_metrics(counts: Counter[str], correct_count: int, sample_count: int,
                   ks: list[int], correct_budget: int, correct_budgets: list[int]) -> dict[str, Any]:
    labeled = sum(counts.values())
    complete = labeled == correct_count
    status = "no_correct" if correct_count == 0 else ("complete" if complete else "incomplete")
    entropy = (-math.fsum((v / correct_count) * math.log(v / correct_count)
                          for v in counts.values()) if complete and correct_count else None)
    return {
        "status": status,
        "counts": dict(sorted(counts.items())),
        "labeled_correct_count": labeled,
        "unique_label_count": len(counts) if complete else None,
        "unique_fraction": len(counts) / correct_count if complete and correct_count else None,
        "effective_label_count": math.exp(entropy) if entropy is not None else None,
        "simpson_diversity": (1 - math.fsum(v * (v - 1) for v in counts.values()) /
                              (correct_count * (correct_count - 1)))
                             if complete and correct_count >= 2 else None,
        "coverage_at_k": {str(k): coverage_at_k(counts, sample_count, k)
                           if complete and k <= sample_count else None for k in ks},
        "correct_matched_coverage": coverage_at_k(counts, correct_count, correct_budget)
                                    if complete and correct_budget <= correct_count else None,
        "correct_matched_coverage_at_budgets": {
            str(budget): coverage_at_k(counts, correct_count, budget)
            if complete and budget <= correct_count else None for budget in correct_budgets},
        "correct_label_entropy": entropy,
    }


def _bootstrap_indices(task_count: int, samples: int, seed: int) -> np.ndarray:
    samples, seed = _integer(samples, "bootstrap_samples"), _integer(seed, "seed")
    return np.random.default_rng(seed).integers(task_count, size=(samples, task_count))


def _macro(values: Mapping[str, float | None], indices: np.ndarray,
           population: str = "tasks_with_available_estimates") -> dict[str, Any]:
    task_ids = sorted(values)
    array = np.asarray([np.nan if values[task] is None else values[task] for task in task_ids], dtype=float)
    valid = ~np.isnan(array)
    eligible = int(valid.sum())
    mean = float(array[valid].mean()) if eligible else None
    ci = None
    valid_replicates = 0
    if eligible and indices.shape[0]:
        draws = array[indices]
        counts = np.sum(~np.isnan(draws), axis=1)
        available = counts > 0
        replicates = np.nansum(draws[available], axis=1) / counts[available]
        valid_replicates = len(replicates)
        if valid_replicates:
            ci = [float(x) for x in np.quantile(replicates, [0.025, 0.975])]
    return {
        "mean": mean,
        "all_task_mean": mean if eligible == len(task_ids) else None,
        "ci95": ci,
        "eligible_tasks": eligible,
        "total_tasks": len(task_ids),
        "unavailable_tasks": [task for task in task_ids if values[task] is None],
        "population": population,
        "bootstrap_valid_replicates": valid_replicates,
    }


def summarize_records(records: Iterable[Mapping[str, Any]], ks: Iterable[int] = (1, 8, 32, 64),
                      correct_budget: int = 8, bootstrap_samples: int = 1000,
                      seed: int = 42, expected_samples: int | Mapping[str, int] | None = None,
                      correct_budgets: Iterable[int] | None = None) -> dict[str, Any]:
    """Summarize one run; records must have unique (task_id, sample_id) keys.

    ``correct`` must be an actual bool, not a truthy string/integer. Every task
    contributes, including zero-correct tasks. A requested k>n is unavailable.
    A partial annotation set never becomes a semantic coverage estimate.

    expected_samples=int validates each observed task's count. A mapping also
    validates the complete task universe, detecting wholly absent tasks. Without
    a mapping, unseen tasks cannot be detected. The default makes no claim that
    observed sample groups are complete. A mapping may explicitly include a
    zero-sample task (expected count 0), whose positive-budget metrics are null.

    Macro means over available task estimates always report eligibility; use
    all_task_mean when an estimate covering the whole task universe is needed.
    Entropy and correct-count-matched metrics are explicitly conditional on
    correct samples. CIs are percentile task-bootstrap intervals, not sample
    bootstrap intervals or uncertainty over verifier/annotation errors.
    """
    ks = [_integer(k, "k") for k in ks]
    if not ks or len(set(ks)) != len(ks):
        raise ValueError("ks must be nonempty and contain no duplicates")
    ks.sort()
    correct_budget = _integer(correct_budget, "correct_budget")
    correct_budgets = [2, 4, 8] if correct_budgets is None else [
        _integer(value, "correct budget") for value in correct_budgets]
    correct_budgets = sorted(set([*correct_budgets, correct_budget]))
    groups: dict[str, list[Mapping[str, Any]]] = {}
    seen = set()
    evaluation_protocols: list[str | None] = []
    for record in records:
        task = record.get("task_id")
        if not isinstance(task, str) or not task.strip():
            raise ValueError("task_id must be a nonempty string")
        sample = _integer(record.get("sample_id"), "sample_id")
        if type(record.get("correct")) is not bool:
            raise ValueError("correct must be an actual bool")
        if (task, sample) in seen:
            raise ValueError(f"duplicate completion key: {(task, sample)!r}")
        seen.add((task, sample))
        strategy = record.get("strategy_id")
        if strategy is not None and not isinstance(strategy, str):
            raise ValueError("strategy_id must be a string or null")
        provenance = record.get("evaluation_provenance")
        if provenance is not None and not isinstance(provenance, Mapping):
            raise ValueError("evaluation provenance must be a mapping")
        evaluation_protocols.append(None if provenance is None else json.dumps(
            provenance, sort_keys=True, ensure_ascii=False, allow_nan=False))
        groups.setdefault(task, []).append(record)
    explicit_protocols = {value for value in evaluation_protocols if value is not None}
    if explicit_protocols and (len(explicit_protocols) != 1 or None in evaluation_protocols):
        raise ValueError("records have missing or mixed evaluation provenance")
    expected: int | dict[str, int] | None = None
    if isinstance(expected_samples, Mapping):
        expected = {}
        for task, count in expected_samples.items():
            if not isinstance(task, str) or not task.strip():
                raise ValueError("expected task_id must be a nonempty string")
            expected[task] = _integer(count, "expected sample count")
        if set(groups) - set(expected):
            raise ValueError("observed tasks absent from expected_samples")
        for task, count in expected.items():
            groups.setdefault(task, [])
            if len(groups[task]) != count:
                raise ValueError(f"task {task!r}: expected {count} samples, got {len(groups[task])}")
    elif expected_samples is not None:
        expected = _integer(expected_samples, "expected_samples")
        for task, rows in groups.items():
            if len(rows) != expected:
                raise ValueError(f"task {task!r}: expected {expected} samples, got {len(rows)}")
    if not groups:
        raise ValueError("no tasks to summarize")
    per_task = {}
    for task in sorted(groups):
        rows = groups[task]
        correct = [row for row in rows if row["correct"]]
        n, c = len(rows), len(correct)
        proxies: Counter[str] = Counter()
        exact_programs: Counter[str] = Counter()
        control_flows: Counter[str] = Counter()
        strategies: Counter[str] = Counter()
        for row in correct:
            code = row.get("code", row.get("completion"))
            proxy = implementation_proxy(code)
            if proxy is not None:
                proxies[proxy] += 1
            if isinstance(code, str):
                exact_programs[hashlib.sha256(code.strip().encode()).hexdigest()] += 1
            control = control_flow_proxy(code)
            if control is not None:
                control_flows[control] += 1
            strategy = row.get("strategy_id")
            if strategy is not None and strategy.strip():
                strategies[strategy] += 1
        per_task[task] = {
            "sample_count": n,
            "correct_count": c,
            "correct_fraction": c / n if n else None,
            "pass_at_k": {str(k): pass_at_k(n, c, k) if k <= n else None for k in ks},
            "implementation_proxy": _label_metrics(proxies, c, n, ks, correct_budget, correct_budgets),
            "exact_program": _label_metrics(exact_programs, c, n, ks, correct_budget, correct_budgets),
            "control_flow_proxy": _label_metrics(control_flows, c, n, ks, correct_budget, correct_budgets),
            "strategy": _label_metrics(strategies, c, n, ks, correct_budget, correct_budgets),
            "lexical": {"pairwise_token_jaccard_distance": _pairwise_token_jaccard(
                [row.get("code", row.get("completion")) for row in correct])},
        }
    indices = _bootstrap_indices(len(per_task), bootstrap_samples, seed)
    def macro(getter, population="tasks_with_available_estimates"):
        return _macro({task: getter(data) for task, data in per_task.items()}, indices, population)
    aggregate = {
        "task_count": len(per_task),
        "sample_count": sum(data["sample_count"] for data in per_task.values()),
        "correct_count": sum(data["correct_count"] for data in per_task.values()),
        "correct_fraction": macro(lambda data: data["correct_fraction"]),
        "pass_at_k": {str(k): macro(lambda data, k=k: data["pass_at_k"][str(k)]) for k in ks},
    }
    for label in ("implementation_proxy", "exact_program", "control_flow_proxy", "strategy"):
        aggregate[label] = {
            "coverage_at_k": {str(k): macro(lambda data, k=k: data[label]["coverage_at_k"][str(k)]) for k in ks},
            "correct_matched_coverage": macro(lambda data: data[label]["correct_matched_coverage"],
                                               "tasks_with_complete_labels_and_at_least_correct_budget_correct_samples"),
            "correct_label_entropy": macro(lambda data: data[label]["correct_label_entropy"],
                                           "tasks_with_complete_labels_and_positive_correct_count"),
            "unique_fraction": macro(lambda data: data[label]["unique_fraction"],
                                     "tasks_with_complete_labels_and_positive_correct_count"),
            "effective_label_count": macro(lambda data: data[label]["effective_label_count"],
                                           "tasks_with_complete_labels_and_positive_correct_count"),
            "simpson_diversity": macro(lambda data: data[label]["simpson_diversity"],
                                       "tasks_with_complete_labels_and_at_least_two_correct_samples"),
            "correct_matched_coverage_at_budgets": {
                str(budget): macro(lambda data, budget=budget:
                                   data[label]["correct_matched_coverage_at_budgets"][str(budget)],
                                   f"tasks_with_complete_labels_and_at_least_{budget}_correct_samples")
                for budget in correct_budgets},
        }
    aggregate["lexical"] = {"pairwise_token_jaccard_distance": macro(
        lambda data: data["lexical"]["pairwise_token_jaccard_distance"],
        "tasks_with_at_least_two_correct_tokenizable_samples")}
    protocol = {"ks": ks, "correct_budget": correct_budget, "correct_budgets": correct_budgets,
                "expected_samples": expected,
                "proxy_version": PROXY_VERSION, "metric_versions": METRIC_VERSIONS,
                "sampling": "without_replacement",
                "bootstrap_samples": int(bootstrap_samples), "seed": int(seed)}
    if explicit_protocols:
        protocol["evaluation"] = json.loads(next(iter(explicit_protocols)))
    return {
        "schema_version": 1,
        "protocol": protocol,
        "per_task": per_task,
        "aggregate": aggregate,
        "definitions": {
            "pass_at_k": "1 - C(n-c,k)/C(n,k); n includes all completions, c is correct count.",
            "coverage_at_k": "Sum over correct labels of 1 - C(n-n_j,k)/C(n,k); incorrect draws remain in n.",
            "implementation_proxy": "Conservative normalized Python AST hash; neither algorithm identity nor semantic equivalence.",
            "exact_program": "SHA-256 of stripped executable source; formatting differences remain distinct.",
            "control_flow_proxy": "Ordered Python AST control-flow node skeleton; an exploratory structural proxy, not an algorithm identity.",
            "effective_label_count": "exp(Shannon entropy) of correct-label frequencies.",
            "simpson_diversity": "Probability that two distinct correct samples drawn without replacement have different labels.",
            "pairwise_token_jaccard_distance": "Mean pairwise Jaccard distance between Python token sets of correct samples.",
            "strategy": "Externally supplied strategy_id labels; a task is unavailable unless every correct sample has a label. Zero-correct coverage is zero.",
            "correct_matched_coverage": "Expected distinct labels in correct_budget draws without replacement from the correct samples only; eligible-task population reported.",
            "correct_label_entropy": "Natural-log Shannon entropy of correct-label frequencies; null for zero correct samples or incomplete labels.",
            "macro": "Equal task weights, including zero-correct tasks. mean is conditional on availability; all_task_mean is null if any task is unavailable. Never compare eligibility-changing means as whole-task gains.",
            "ci95": "Pointwise 95% percentile bootstrap over tasks; eligibility is recomputed in each resample, empty eligible resamples omitted and counted. No multiple-comparison correction.",
            "expected_samples": "A mapping validates the complete task universe; an integer only validates observed task counts. Missing whole tasks cannot be detected without the mapping.",
        },
    }


def _same_tasks(previous: Mapping[str, Any], current: Mapping[str, Any]) -> list[str]:
    tasks = sorted(previous["per_task"])
    if tasks != sorted(current["per_task"]):
        raise ValueError("summaries must contain identical task IDs")
    if not tasks:
        raise ValueError("cannot compare empty summaries")
    return tasks


def compare_summaries(previous: Mapping[str, Any], current: Mapping[str, Any],
                      correctness_margin: float = 0.0, bootstrap_samples: int = 1000,
                      seed: int = 42) -> dict[str, Any]:
    """Paired task-bootstrap current-minus-previous differences.

    Requires identical task IDs, per-task sampling budgets and metric protocol.
    Correctness noninferiority uses the lower endpoint of a two-sided 95% CI
    for the task-macro correct fraction and the supplied absolute margin. Null
    means unavailable, including disabled bootstrap or any empty task. Shared
    seeds/completion pairing are not required; the resampling unit is the task.
    This cannot verify that generation or evaluation protocols were identical.
    """
    if (isinstance(correctness_margin, bool) or not isinstance(correctness_margin, Real)
            or not math.isfinite(correctness_margin) or not 0 <= correctness_margin <= 1):
        raise ValueError("correctness_margin must be finite and between 0 and 1")
    tasks = _same_tasks(previous, current)
    for field in ("ks", "correct_budget", "correct_budgets", "proxy_version",
                  "metric_versions", "sampling"):
        if previous["protocol"].get(field) != current["protocol"].get(field):
            raise ValueError(f"summaries have different metric protocol: {field}")
    for task in tasks:
        if previous["per_task"][task]["sample_count"] != current["per_task"][task]["sample_count"]:
            raise ValueError(f"task {task!r} has different sampling budgets")
    indices = _bootstrap_indices(len(tasks), bootstrap_samples, seed)
    def delta(getter):
        values = {}
        for task in tasks:
            old = getter(previous["per_task"][task])
            new = getter(current["per_task"][task])
            values[task] = None if old is None or new is None else new - old
        return _macro(values, indices, "tasks_with_estimates_available_in_both_runs")
    correctness = delta(lambda data: data["correct_fraction"])
    noninferior = None
    if correctness["eligible_tasks"] == len(tasks) and correctness["ci95"] is not None:
        noninferior = bool(correctness["ci95"][0] >= -correctness_margin)
    ks = previous["protocol"]["ks"]
    result = {
        "direction": "current_minus_previous",
        "task_count": len(tasks),
        "correctness": {"metric": "task_macro_correct_fraction", "margin": float(correctness_margin),
                        "delta": correctness, "noninferior": noninferior},
        "pass_at_k": {str(k): delta(lambda data, k=k: data["pass_at_k"][str(k)]) for k in ks},
        "bootstrap": {"samples": int(bootstrap_samples), "seed": int(seed), "unit": "paired_tasks"},
        "caveat": "Metric and sampling budgets were checked. Identical prompts, verifier, decoding protocol, and stable strategy annotation identities remain caller responsibilities. Partial-eligibility differences describe only the reported paired subset; these pointwise CIs do not establish an overall diversity gain.",
    }
    for label in ("implementation_proxy", "exact_program", "control_flow_proxy", "strategy"):
        result[label] = {
            "coverage_at_k": {str(k): delta(lambda data, k=k: data[label]["coverage_at_k"][str(k)]) for k in ks},
            "correct_matched_coverage": delta(lambda data: data[label]["correct_matched_coverage"]),
            "correct_label_entropy": delta(lambda data: data[label]["correct_label_entropy"]),
            "unique_fraction": delta(lambda data: data[label]["unique_fraction"]),
            "effective_label_count": delta(lambda data: data[label]["effective_label_count"]),
            "simpson_diversity": delta(lambda data: data[label]["simpson_diversity"]),
            "correct_matched_coverage_at_budgets": {
                str(budget): delta(lambda data, budget=budget:
                                   data[label]["correct_matched_coverage_at_budgets"][str(budget)])
                for budget in previous["protocol"]["correct_budgets"]},
        }
    result["lexical"] = {"pairwise_token_jaccard_distance": delta(
        lambda data: data["lexical"]["pairwise_token_jaccard_distance"])}
    return result


def strategy_retention(previous: Mapping[str, Any], current: Mapping[str, Any]) -> dict[str, Any]:
    """Observed cross-round retention using stable supplied strategy IDs only.

    Same labels must refer to the same independently annotated strategy across
    rounds. AST proxies never substitute for unavailable semantic annotations.
    Tasks must match; budgets may differ and are reported explicitly.
    """
    tasks = _same_tasks(previous, current)
    per_task = {}
    for task in tasks:
        before = previous["per_task"][task]
        after = current["per_task"][task]
        complete = before["strategy"]["status"] != "incomplete" and after["strategy"]["status"] != "incomplete"
        old = set(before["strategy"]["counts"])
        new = set(after["strategy"]["counts"])
        per_task[task] = {
            "status": "incomplete" if not complete else ("no_previous_correct" if not old else "complete"),
            "previous_sample_count": before["sample_count"],
            "current_sample_count": after["sample_count"],
            "retained_labels": sorted(old & new) if complete else None,
            "unobserved_previous_labels": sorted(old - new) if complete else None,
            "newly_observed_labels": sorted(new - old) if complete else None,
            "retention_fraction": len(old & new) / len(old) if complete and old else None,
        }
    values = {task: data["retention_fraction"] for task, data in per_task.items()}
    return {
        "per_task": per_task,
        "aggregate": _macro(values, np.empty((0, len(tasks)), dtype=int),
                            "tasks_with_complete_annotations_and_previous_correct_strategies"),
        "label_identity_assumption": "A supplied strategy_id denotes the same independently annotated strategy in both rounds.",
        "caveat": "Finite-sample absence is not proof of strategy eradication. Retention reflects observed supplied labels and depends on sample budget and correctness; AST fingerprints are not used.",
    }
