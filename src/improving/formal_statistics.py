"""Paired formal comparisons for training seeds crossed with benchmark tasks.

Inputs are complete ``metrics.summarize_records`` outputs. A bootstrap draw
resamples seeds and task IDs independently, then uses their Cartesian product.
All sampled seeds see the same sampled task IDs, preserving task correlations
across seeds. Completion pools are not independently bootstrapped.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
from numbers import Integral, Real
from typing import Any

import numpy as np


def _integer(value: Any, name: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _seed_map(runs: Mapping[str | int, Any], name: str) -> dict[str, Mapping[str, Any]]:
    if not isinstance(runs, Mapping) or not runs:
        raise ValueError(f"{name} must contain nonempty seed runs")
    normalized = {}
    for key, value in runs.items():
        if isinstance(key, bool) or not isinstance(key, (str, Integral)) or not str(key).strip():
            raise ValueError("seed IDs must be nonempty strings or integers")
        key = str(key)
        if key in normalized:
            raise ValueError("seed IDs collide after string normalization")
        if not isinstance(value, Mapping):
            raise ValueError(f"missing summary for {name} seed {key!r}")
        normalized[key] = value
    return normalized


def _validate(previous, current, correct_budgets):
    previous, current = _seed_map(previous, "previous"), _seed_map(current, "current")
    seeds = sorted(previous)
    if seeds != sorted(current):
        raise ValueError("comparisons require identical seed IDs")
    reference = previous[seeds[0]]
    protocol = reference.get("protocol")
    if not isinstance(protocol, Mapping):
        raise ValueError("missing metric protocol")
    if not isinstance(protocol.get("evaluation"), Mapping) or not protocol["evaluation"]:
        raise ValueError("formal inference requires explicit evaluation provenance")
    tasks_map = reference.get("per_task")
    if not isinstance(tasks_map, Mapping) or not tasks_map:
        raise ValueError("cannot compare empty task summaries")
    if any(not isinstance(task, str) or not task.strip() for task in tasks_map):
        raise ValueError("task IDs must be nonempty strings")
    tasks = sorted(tasks_map)
    harnesses = protocol.get("evaluation_task_harnesses")
    if (not isinstance(harnesses, Mapping) or set(harnesses) != set(tasks)
            or any(not isinstance(value, str) or not value for value in harnesses.values())):
        raise ValueError("formal inference requires complete per-task evaluation provenance")
    fields = ("ks", "correct_budget", "correct_budgets", "proxy_version", "metric_versions",
              "sampling", "evaluation", "evaluation_task_harnesses")
    if any(field not in protocol for field in fields):
        raise ValueError("incomplete metric protocol")
    available_budgets = protocol["correct_budgets"]
    if not isinstance(available_budgets, Sequence) or not set(correct_budgets) <= set(available_budgets):
        raise ValueError("summaries lack requested correct-sample budgets")
    ks = protocol["ks"]
    if not isinstance(ks, Sequence) or not ks or len(set(ks)) != len(ks):
        raise ValueError("metric protocol requires nonempty unique ks")
    ks = [_integer(k, "metric protocol k", 1) for k in ks]
    reference_counts = {task: _integer(tasks_map[task].get("sample_count"), "sample count", 1)
                        for task in tasks}
    for side in (previous, current):
        for run_seed in seeds:
            value = side[run_seed]
            run_protocol = value.get("protocol")
            if not isinstance(run_protocol, Mapping):
                raise ValueError(f"missing metric protocol at seed {run_seed}")
            for field in fields:
                if run_protocol.get(field) != protocol[field]:
                    raise ValueError(f"summaries have different metric/evaluation protocol: {field}")
            per_task = value.get("per_task")
            if not isinstance(per_task, Mapping) or set(per_task) != set(tasks):
                raise ValueError("all seeds and methods must contain identical nonempty task IDs")
            expected = run_protocol.get("expected_samples")
            if isinstance(expected, Mapping) and set(expected) != set(tasks):
                raise ValueError("expected sample budget has different task IDs")
            for task in tasks:
                count = _integer(per_task[task].get("sample_count"), "sample count", 1)
                if count != reference_counts[task]:
                    raise ValueError(f"different sample budgets for task {task!r}")
                if expected is not None:
                    expected_count = expected.get(task) if isinstance(expected, Mapping) else expected
                    if _integer(expected_count, "expected sample count", 1) != count:
                        raise ValueError(f"incomplete sample budget for task {task!r}")
    return previous, current, seeds, tasks, ks, protocol


def _value(row: Mapping[str, Any], path: tuple[str, ...]) -> float | None:
    value = row
    try:
        for key in path:
            value = value[key]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"summary is missing metric {'.'.join(path)}") from exc
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError(f"metric {'.'.join(path)} must be finite or null")
    return float(value)


def compare_seed_summaries(
    previous: Mapping[str | int, Mapping[str, Any]],
    current: Mapping[str | int, Mapping[str, Any]],
    *, correctness_margin: float = .01,
    correct_budgets: Sequence[int] = (4, 8, 16),
    bootstrap_samples: int = 2000, seed: int = 42, family_size: int = 4,
) -> dict[str, Any]:
    """Current-minus-previous seed means of paired task effects.

    Correct-sample coverage is conditional on BOTH methods having enough
    correct, fully labeled samples on the same task in the same seed. Each
    seed receives equal weight after averaging its eligible paired tasks.
    If any observed seed lacks eligible tasks, the overall effect and CI are
    null rather than silently dropping that seed. Eligibility is recomputed
    within every bootstrap draw; null draws are counted, not replaced by zero.

    ``ci95_family`` uses two-sided percentile bounds alpha/(2*family_size).
    With family_size=4 the registered family is two primary endpoints across
    two method comparisons. Other metrics are exploratory; these intervals
    do not simultaneously cover every metric or every round in the output.
    The percentile bootstrap is approximate, especially with few seeds.

    Decoding/prompt/config identity and completeness of the planned seed set
    cannot be inferred from summaries and MUST be checked by the caller.
    """
    if (isinstance(correctness_margin, bool) or not isinstance(correctness_margin, Real)
            or not math.isfinite(correctness_margin) or not 0 <= correctness_margin <= 1):
        raise ValueError("correctness_margin must be finite and between 0 and 1")
    bootstrap_samples = _integer(bootstrap_samples, "bootstrap_samples")
    seed = _integer(seed, "seed")
    family_size = _integer(family_size, "family_size", 1)
    correct_budgets = [_integer(budget, "correct budget", 1) for budget in correct_budgets]
    if 4 not in correct_budgets or len(set(correct_budgets)) != len(correct_budgets):
        raise ValueError("correct_budgets must be unique and include the primary budget 4")
    previous, current, seeds, tasks, ks, protocol = _validate(previous, current, correct_budgets)
    seed_count, task_count = len(seeds), len(tasks)
    rng = np.random.default_rng(seed)
    seed_indices = rng.integers(seed_count, size=(bootstrap_samples, seed_count))
    # One task-index row per replicate, shared by every seed in that draw.
    task_indices = rng.integers(task_count, size=(bootstrap_samples, task_count))

    def delta(path):
        old = np.asarray([[_value(previous[s]["per_task"][task], path)
                           for task in tasks] for s in seeds], dtype=float)
        new = np.asarray([[_value(current[s]["per_task"][task], path)
                           for task in tasks] for s in seeds], dtype=float)
        differences = new - old
        available = np.isfinite(differences)
        per_seed = {}
        means = []
        for index, run_seed in enumerate(seeds):
            mask = available[index]
            count = int(mask.sum())
            mean = float(differences[index, mask].mean()) if count else None
            per_seed[run_seed] = {
                "mean": mean,
                "previous_mean": float(old[index, mask].mean()) if count else None,
                "current_mean": float(new[index, mask].mean()) if count else None,
                "eligible_tasks": count, "total_tasks": task_count,
                "unavailable_tasks": [task for task, good in zip(tasks, mask) if not good],
            }
            if mean is not None:
                means.append(mean)
        point = float(np.mean(means)) if len(means) == seed_count else None
        valid_draws = np.empty(0, dtype=float)
        if bootstrap_samples:
            draws = differences[seed_indices[:, :, None], task_indices[:, None, :]]
            counts = np.isfinite(draws).sum(axis=2)
            per_seed_draws = np.divide(np.nansum(draws, axis=2), counts,
                                       out=np.zeros_like(counts, dtype=float), where=counts > 0)
            valid = np.all(counts > 0, axis=1)
            valid_draws = per_seed_draws[valid].mean(axis=1)
        ci = family_ci = standard_error = None
        if point is not None and len(valid_draws):
            ci = [float(value) for value in np.quantile(valid_draws, [.025, .975])]
            tail = .05 / (2 * family_size)
            family_ci = [float(value) for value in np.quantile(valid_draws, [tail, 1 - tail])]
            if len(valid_draws) > 1:
                standard_error = float(np.std(valid_draws, ddof=1))
        return {
            "mean": point, "ci95": ci, "ci95_family": family_ci,
            "per_seed": per_seed, "eligible_seeds": len(means), "total_seeds": seed_count,
            "paired_eligible_tasks_all_seeds": int(np.all(available, axis=0).sum()),
            "eligible_task_seed_pairs": int(available.sum()),
            "total_task_seed_pairs": seed_count * task_count,
            "bootstrap_valid_replicates": int(len(valid_draws)),
            "bootstrap_null_replicates": bootstrap_samples - int(len(valid_draws)),
            "bootstrap_standard_error": standard_error,
            "population": "equal_seed_means_of_tasks_available_in_both_methods_within_each_seed",
        }

    correctness = delta(("correct_fraction",))
    noninferior = None
    if (correctness["ci95_family"] is not None
            and correctness["eligible_task_seed_pairs"] == seed_count * task_count):
        noninferior = correctness["ci95_family"][0] >= -float(correctness_margin)
    result = {
        "schema_version": 1, "direction": "current_minus_previous",
        "seed_ids": seeds, "seed_count": seed_count, "task_ids": tasks, "task_count": task_count,
        "correctness": {"metric": "task_macro_correct_fraction", "margin": float(correctness_margin),
                        "delta": correctness, "noninferior": noninferior},
        "pass_at_k": {str(k): delta(("pass_at_k", str(k))) for k in ks},
        "bootstrap": {
            "samples": bootstrap_samples, "seed": seed,
            "unit": "crossed_paired_seeds_and_shared_task_ids", "family_size": family_size,
            "pointwise_coverage": .95, "family_coverage": .95,
            "family_interval_tail_probability": .05 / (2 * family_size),
            "simultaneous_family": "registered primary endpoints and comparisons only",
            "method": "approximate percentile product bootstrap; no completion resampling",
        },
        "protocol": {key: protocol[key] for key in (
            "ks", "correct_budgets", "metric_versions", "sampling",
            "evaluation", "evaluation_task_harnesses")},
    }
    for label in ("implementation_proxy", "exact_program", "control_flow_proxy", "strategy"):
        result[label] = {
            "coverage_at_k": {str(k): delta((label, "coverage_at_k", str(k))) for k in ks},
            "correct_matched_coverage_at_budgets": {
                str(budget): delta((label, "correct_matched_coverage_at_budgets", str(budget)))
                for budget in correct_budgets},
            **{field: delta((label, field)) for field in (
                "unique_fraction", "simpson_diversity", "correct_label_entropy", "effective_label_count")},
        }
    result["lexical"] = {"pairwise_token_jaccard_distance": delta(
        ("lexical", "pairwise_token_jaccard_distance"))}
    primary = result["implementation_proxy"]["correct_matched_coverage_at_budgets"]["4"]
    superior = primary["ci95_family"][0] > 0 if primary["ci95_family"] is not None else None
    success = None
    if seed_count >= 2 and superior is not None and noninferior is not None:
        success = bool(superior and noninferior)
    result["decision"] = {
        "primary_correct_budget": 4, "primary_diversity_metric": "implementation_proxy_correct_matched_coverage",
        "diversity_superior": superior, "correctness_noninferior": noninferior,
        "success": success,
        "evidence_status": "single_seed_exploratory" if seed_count < 2 else "multiple_seed_comparison",
        "requires_caller_check": "complete preregistered seed set, primary comparisons, and identical decoding/configuration",
        "interpretation": "paired eligible-task AST proxy diversity, not proven algorithm diversity or whole-task coverage",
    }
    result["caveats"] = [
        "Prompt, decoding, model, intervention, annotation identity, and planned seed completeness are caller checks.",
        "Eligibility can differ by seed; conditional diversity does not measure gains on unsolved tasks.",
        "The same seed/task indices are used for all endpoints; multiplicity coverage applies only to the declared family.",
        "A crossed bootstrap is approximate and few seeds limit inference about training variation.",
        "Intervals exclude verifier errors, annotation errors, data contamination, and unobserved completion-pool uncertainty.",
    ]
    return result
