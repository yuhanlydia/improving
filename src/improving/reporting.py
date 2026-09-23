"""Auditable experiment overviews and independent strategy-annotation joins.

This module has no model-loading or generated-code execution side effects.
Missing measurements stay pending; structural proxies never become semantic
strategy labels. Report comparisons require explicit evaluation provenance.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import json
from pathlib import Path
import re
from typing import Any

from .metrics import compare_summaries


def _key(row: Mapping[str, Any]) -> tuple[str, int]:
    task, sample = row.get("task_id"), row.get("sample_id")
    if not isinstance(task, str) or not task.strip():
        raise ValueError("task_id must be a nonempty string")
    if type(sample) is not int or sample < 0:
        raise ValueError("sample_id must be a nonnegative integer")
    return task, sample


def annotate_records(records: Iterable[Mapping[str, Any]],
                     annotations: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Strictly join independent annotations onto copies of verified records.

    The supplied annotation collection is authoritative: correct records with
    no supplied label receive strategy_id=null, even if the input has an old
    label. A conflicting explicit new label raises. Missing annotations are
    allowed and explicitly marked; summaries will expose incomplete tasks.
    Wrong records may have a null annotation but cannot receive a positive
    label. No records are filtered and raw completion text remains unchanged.
    """
    rows: dict[tuple[str, int], Mapping[str, Any]] = {}
    for row in records:
        key = _key(row)
        if key in rows:
            raise ValueError(f"duplicate completion key: {key!r}")
        if type(row.get("correct")) is not bool:
            raise ValueError("correct must be an actual bool")
        if not row["correct"] and row.get("strategy_id") not in (None, ""):
            raise ValueError(f"incorrect completion already has a strategy label: {key!r}")
        rows[key] = row
    joined: dict[tuple[str, int], str | None] = {}
    for annotation in annotations:
        key = _key(annotation)
        if key in joined:
            raise ValueError(f"duplicate annotation key: {key!r}")
        if key not in rows:
            raise ValueError(f"annotation refers to unknown completion: {key!r}")
        if "strategy_id" not in annotation:
            raise ValueError("each annotation must supply strategy_id (string or null)")
        label = annotation["strategy_id"]
        if label is not None and (not isinstance(label, str) or not label.strip()):
            raise ValueError("strategy_id must be a nonempty string or null")
        if label is not None and not rows[key]["correct"]:
            raise ValueError(f"incorrect completion cannot receive a strategy label: {key!r}")
        old_label = rows[key].get("strategy_id")
        if label is not None and old_label not in (None, "", label):
            raise ValueError(f"annotation conflicts with existing strategy label: {key!r}")
        joined[key] = label
    output = []
    for key, row in rows.items():
        label = joined.get(key)
        output.append({**row, "strategy_id": label,
                       "strategy_annotation_status": "not_applicable" if not row["correct"]
                       else ("annotated" if label is not None else "missing")})
    return output


def _read_optional(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"invalid JSON in {path}") from exc
    if not isinstance(result, dict):
        raise ValueError(f"expected JSON object in {path}")
    return result


def _first_optional(*paths: Path) -> dict[str, Any] | None:
    for path in paths:
        value = _read_optional(path)
        if value is not None:
            return value
    return None


def _estimate(metric: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if metric is None:
        return None
    eligible, total = metric["eligible_tasks"], metric["total_tasks"]
    return {**metric, "eligible_fraction": eligible / total if total else None,
            "coverage_status": "unavailable" if not eligible else ("full" if eligible == total else "partial")}


def _overview(summary: Mapping[str, Any]) -> dict[str, Any]:
    aggregate = summary["aggregate"]
    output = {
        "task_count": aggregate["task_count"],
        "sample_count": aggregate["sample_count"],
        "correct_count": aggregate["correct_count"],
        "pass_at_1": _estimate(aggregate["pass_at_k"].get("1", aggregate["correct_fraction"])),
        "pass_at_k": {k: _estimate(value) for k, value in aggregate["pass_at_k"].items()},
        "correct_budget": summary["protocol"]["correct_budget"],
    }
    for source, name in (("implementation_proxy", "implementation"),
                         ("exact_program", "exact_program"),
                         ("control_flow_proxy", "control_flow"),
                         ("strategy", "strategy")):
        output[f"{name}_coverage_at_k"] = {k: _estimate(value) for k, value in aggregate[source]["coverage_at_k"].items()}
        output[f"{name}_correct_matched_coverage"] = _estimate(aggregate[source]["correct_matched_coverage"])
        output[f"{name}_correct_label_entropy"] = _estimate(aggregate[source]["correct_label_entropy"])
        output[f"{name}_unique_fraction"] = _estimate(aggregate[source]["unique_fraction"])
        output[f"{name}_effective_label_count"] = _estimate(aggregate[source]["effective_label_count"])
        output[f"{name}_simpson_diversity"] = _estimate(aggregate[source]["simpson_diversity"])
        output[f"{name}_correct_matched_coverage_at_budgets"] = {
            budget: _estimate(value) for budget, value in
            aggregate[source]["correct_matched_coverage_at_budgets"].items()}
    output["lexical_pairwise_token_jaccard_distance"] = _estimate(
        aggregate["lexical"]["pairwise_token_jaccard_distance"])
    output["strategy_annotation_status"] = {
        status: sorted(task for task, data in summary["per_task"].items() if data["strategy"]["status"] == status)
        for status in ("complete", "incomplete", "no_correct")
    }
    return output


def _stage(root: Path, method: str, round_index: int, stage: str,
           requested: bool = True, *, include_existing: bool = True) -> tuple[dict[str, Any], dict[str, Any] | None]:
    relative = "base" if method == "base" else f"{method}/round_{round_index}"
    directory = root / relative
    path = directory / f"{stage}.metrics.json"
    summary = _read_optional(path) if include_existing else None
    budget = (_first_optional(directory / f"{stage}.jsonl.budget.json", directory / f"{stage}.budget.json")
              if include_existing else None)
    if summary is None:
        status = "pending_metrics" if requested else "not_requested"
    elif "aggregate" not in summary or "per_task" not in summary:
        status = summary.get("status", "pending_metrics")
        if status not in {"pending_metrics", "pending_verification"}:
            raise ValueError(f"unrecognized metric summary in {path}")
    else:
        status = "available"
    protocol = summary.get("protocol", {}) if summary else {}
    evaluation = protocol.get("evaluation", summary.get("evaluation_protocol") if summary else None)
    sampling = budget.get("protocol") if budget else None
    row = {
        "id": f"{relative}/{stage}", "method": method, "round": round_index, "stage": stage,
        "status": status, "metrics_path": str(path),
        "metrics": _overview(summary) if status == "available" else None,
        "budget": budget,
        "resources": ({item.name: _read_optional(item) for item in sorted(directory.glob('*.resources.json'))}
                      if include_existing else {}),
        "raw_records_path": str(directory / f'{stage}.jsonl'),
        "verified_records_path": str(directory / f'{stage}.verified.jsonl'),
        "per_task_metrics_retained": bool(summary and summary.get('per_task')),
        "protocol": {"metrics": protocol, "sampling": sampling, "evaluation": evaluation,
                     "evaluation_provenance": "explicit" if evaluation else "unavailable"},
        "provenance_issues": [],
    }
    if status == "available" and budget:
        for key, metric in (("samples", "sample_count"), ("tasks", "task_count")):
            if key in budget and budget[key] != row["metrics"][metric]:
                row["provenance_issues"].append(f"budget {key} does not match summarized {metric}")
    return row, summary if status == "available" else None


def _sampling_signature(protocol: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(protocol, Mapping) or "settings" not in protocol or "prompts" not in protocol:
        return None
    # These identify the intervention/checkpoint, not the matched sampling
    # procedure. Preserve them in the report even though they must differ.
    return {key: value for key, value in protocol.items() if key not in {"model_identity", "method", "round"}}


def _comparison(candidate: Mapping[str, Any], reference: Mapping[str, Any] | None,
                reference_id: str, summaries: Mapping[str, Any],
                margin: float, samples: int, seed: int) -> dict[str, Any]:
    result = {"candidate": candidate["id"], "reference": reference_id,
              "status": "pending", "reason": None, "result": None}
    if candidate["status"] != "available":
        result["reason"] = "candidate metrics are pending"
        return result
    if reference is None or reference["status"] != "available":
        result["reason"] = "reference metrics are pending"
        return result
    issues = [*candidate["provenance_issues"], *reference["provenance_issues"]]
    if issues:
        result.update(status="incomparable", reason="; ".join(issues))
        return result
    for kind in ("evaluation", "sampling"):
        candidate_protocol = candidate["protocol"][kind]
        reference_protocol = reference["protocol"][kind]
        if kind == "sampling":
            candidate_protocol = _sampling_signature(candidate_protocol)
            reference_protocol = _sampling_signature(reference_protocol)
        if not candidate_protocol or not reference_protocol:
            result.update(status="incomparable", reason=f"explicit {kind} protocol is unavailable")
            return result
        if candidate_protocol != reference_protocol:
            result.update(status="incomparable", reason=f"{kind} protocols differ")
            return result
    try:
        paired = compare_summaries(summaries[reference_id], summaries[candidate["id"]],
                                   correctness_margin=margin, bootstrap_samples=samples, seed=seed)
    except ValueError as exc:
        result.update(status="incomparable", reason=str(exc))
        return result
    result.update(status="available", result=paired)
    return result


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _formatted(metric: Mapping[str, Any] | None) -> str:
    if metric is None:
        return "pending"
    eligible = f"{metric['eligible_tasks']}/{metric['total_tasks']} tasks"
    if metric["mean"] is None:
        return f"unavailable ({eligible})"
    ci = metric.get("ci95")
    interval = f" [{ci[0]:.3f}, {ci[1]:.3f}]" if ci is not None else " [CI unavailable]"
    return f"{metric['mean']:.3f}{interval}; {eligible}, {metric.get('coverage_status', 'paired')}"


def _markdown(report: Mapping[str, Any]) -> str:
    lines = ["# Coding self-distillation report", "", f"Result status: **{report['status']}**.", "",
             "Numbers show task means with pointwise 95% task-bootstrap intervals and explicit eligible-task denominators. Partial means describe the eligible subset; they do not establish gains across all tasks. Pending measurements are not zeros.", "",
             "## Correctness and evaluation stages", "", "| Method | Round | Stage | Status | Pass@16 | Pass@64 | Samples |", "| --- | ---: | --- | --- | --- | --- | ---: |"]
    for stage in report["stages"]:
        metrics = stage["metrics"]
        lines.append("| " + " | ".join(map(_cell, [stage["method"], stage["round"], stage["stage"], stage["status"],
                     *[_formatted(metrics["pass_at_k"].get(k) if metrics else None) for k in ("16", "64")],
                     metrics["sample_count"] if metrics else "pending"])) + " |")
    lines += ["", "## Correct implementation richness and annotated strategy coverage", "",
              "Implementation coverage uses conservative Python AST fingerprints. These are implementation proxies, not algorithm identities. Strategy coverage uses supplied independent labels only; incomplete annotations remain unavailable. Wrong completions remain in the draw population.", "",
              "| Stage | Draw budget K | Correct AST richness @K | Annotated strategy coverage |", "| --- | ---: | --- | --- |"]
    for stage in report["stages"]:
        metrics = stage["metrics"]
        for k in ("16", "64"):
            implementation = metrics["implementation_coverage_at_k"].get(k) if metrics else None
            strategy = metrics["strategy_coverage_at_k"].get(k) if metrics else None
            lines.append(f"| {_cell(stage['id'])} | {k} | {_formatted(implementation)} | {_formatted(strategy)} |")
    lines += ["", "## Coverage at a fixed correct-sample budget", "",
              "These conditional estimates use only correct samples and require at least the displayed number of correct samples per task. Different eligible-task populations must not be interpreted as whole-task improvements.", "",
              "| Stage | Correct-sample budget b | Correct-conditioned AST richness @b | Annotated strategy coverage |", "| --- | ---: | --- | --- |"]
    for stage in report["stages"]:
        metrics = stage["metrics"]
        budgets = sorted(metrics["implementation_correct_matched_coverage_at_budgets"], key=int) if metrics else ["pending"]
        for budget in budgets:
            lines.append("| " + " | ".join(map(_cell, [stage["id"], budget,
                         _formatted(metrics["implementation_correct_matched_coverage_at_budgets"].get(budget) if metrics else None),
                         _formatted(metrics["strategy_correct_matched_coverage_at_budgets"].get(budget) if metrics else None)])) + " |")
    lines += ["", "## Paired comparisons", "",
              "Deltas are candidate minus reference at draw budgets 16 and 64. Missing budgets remain pending. These descriptive estimates do not establish algorithm diversity or an automatic research conclusion.", "",
              "| Candidate | Reference | Status | ΔPass@16 | ΔPass@64 | Reason |", "| --- | --- | --- | --- | --- | --- |"]
    for comparison in report["comparisons"]:
        paired = comparison["result"]
        lines.append("| " + " | ".join(map(_cell, [comparison["candidate"], comparison["reference"], comparison["status"],
                     *[_formatted(paired["pass_at_k"].get(k) if paired else None) for k in ("16", "64")],
                     comparison["reason"] or "—"])) + " |")
    lines += ["", "Coverage and entropy deltas, including their intervals and paired eligibility, are included in the JSON report. Comparisons require matching explicit sampling and evaluation protocols, task IDs, metric budgets, and per-task sample counts.", "",
              "## Budgets and training", "", "| Stage | Generated samples | Generation tokens | Prompt tokens |", "| --- | ---: | ---: | ---: |"]
    for stage in report["stages"]:
        budget = stage["budget"] or {}
        lines.append("| " + " | ".join(map(_cell, [stage["id"], *[budget.get(key, "unavailable") for key in ("samples", "generation_tokens", "prompt_tokens")]])) + " |")
    for round_id, data in report["rounds"].items():
        lines += ["", f"**{_cell(round_id)}**", "", "Training statistics: " +
                  ("unavailable" if data["training_stats"] is None else "`" + json.dumps(data["training_stats"], sort_keys=True).replace("`", "'") + "`"),
                  "", "Training generation budget: " + ("unavailable" if data["training_budget"] is None else
                  "`" + json.dumps({k: v for k, v in data["training_budget"].items() if k != "protocol"}, sort_keys=True).replace("`", "'") + "`")]
    lines += ["", "## Wall time and memory", "",
              "Elapsed time includes recorded attempts. CUDA peaks are recorded per stage; stage peaks must not be added as if they occurred simultaneously. Unrecorded costs remain unavailable.", "",
              "| Run stage | Operation | Elapsed seconds | Peak allocated bytes | Peak reserved bytes |", "| --- | --- | ---: | ---: | ---: |"]
    seen = set()
    for stage in report['stages']:
        for filename, resource in stage['resources'].items():
            key = (stage['method'], stage['round'], filename)
            if key in seen:
                continue
            seen.add(key)
            lines.append('| ' + ' | '.join(map(_cell, [f"{stage['method']}/round_{stage['round']}",
                         resource.get('stage', filename), resource.get('elapsed_seconds', 'unavailable'),
                         resource.get('cuda_peak_allocated_bytes', 'unavailable'),
                         resource.get('cuda_peak_reserved_bytes', 'unavailable')])) + ' |')
    lines += ["", "## Appendix: Pass@1 and correctness noninferiority", "",
              "Pass@1 and the original correctness criterion are retained as supplementary diagnostics. They do not determine the main Pass@16/Pass@64 and diversity conclusions.", "",
              "| Stage | Pass@1 |", "| --- | --- |"]
    for stage in report["stages"]:
        metrics = stage["metrics"]
        lines.append(f"| {_cell(stage['id'])} | {_formatted(metrics['pass_at_1'] if metrics else None)} |")
    lines += ["", f"Correctness noninferiority uses the task-macro correct fraction (Pass@1), an absolute margin of {report['comparison_settings']['correctness_margin']:.3f}, and the lower endpoint of a two-sided 95% paired task-bootstrap interval. It requires all tasks.", "",
              "| Candidate | Reference | Status | Pass@1 delta | Noninferiority | Reason |", "| --- | --- | --- | --- | --- | --- |"]
    for comparison in report["comparisons"]:
        paired = comparison["result"]
        check = paired["correctness"]["noninferior"] if paired else None
        label = "unavailable" if check is None else ("criterion met" if check else "criterion not met")
        lines.append("| " + " | ".join(map(_cell, [comparison["candidate"], comparison["reference"], comparison["status"],
                     _formatted(paired["correctness"]["delta"] if paired else None), label, comparison["reason"] or "—"])) + " |")
    lines += ["", "The JSON report preserves all metric budgets, Pass@1 and correctness comparisons, generation budgets, training statistics, full sampling metadata, evaluation provenance, and eligibility details. Sampling budget and correctness can change observed diversity; no model-performance claim follows from a report being complete.", ""]
    return "\n".join(lines)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def _saved_checkpoint_scope(manifest: Mapping[str, Any] | None) -> set[tuple[str, int]] | None:
    """Use the actual evaluation request, not its inherited training schedule."""
    if not manifest or manifest.get("purpose") != "saved_checkpoint_evaluation_without_training":
        return None
    protocol = manifest.get("protocol")
    if not isinstance(protocol, Mapping):
        raise ValueError("invalid saved-checkpoint report scope: protocol must be an object")
    methods, rounds = protocol.get("methods"), protocol.get("rounds")
    if not isinstance(methods, list) or any(
            not isinstance(method, str) or not method.strip() or method != method.strip()
            or method in {"base", ".", ".."} or "/" in method or "\\" in method
            for method in methods):
        raise ValueError("invalid saved-checkpoint report scope: methods must be method directory names")
    if (not isinstance(rounds, list) or not rounds
            or any(type(index) is not int or index < 1 for index in rounds)
            or len(set(methods)) != len(methods) or len(set(rounds)) != len(rounds)):
        raise ValueError("invalid saved-checkpoint report scope: methods and positive integer rounds must be unique")
    return {(method, index) for method in methods for index in rounds}


def build_report(run_dir: str | Path, output_path: str | Path | None = None) -> dict[str, Any]:
    """Write an overview JSON and Markdown pair, and return its JSON contents.

    Defaults to run_dir/report.json and report.md. output_path may name either
    a .json or .md file; the other format uses the same stem. A suffixless path
    is treated as a filename stem. Configured missing stages are pending;
    existing method/round directories are also discovered for training runs or
    without a manifest. Saved-checkpoint evaluations use only protocol.methods
    and protocol.rounds; generation-policy diagnostics are not requested.

    evaluation.correctness_margin (default 0), evaluation.bootstrap_samples
    (default 1000), and config.seed determine paired comparisons. Explicit
    summary.protocol.evaluation is required; a run manifest's intended verifier
    configuration is not treated as evidence that a result used that verifier.
    """
    root = Path(run_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"run directory does not exist: {root}")
    manifest = _read_optional(root / "manifest.json")
    config = manifest.get("config", {}) if manifest else {}
    saved_scope = _saved_checkpoint_scope(manifest)
    stage_rows: list[dict[str, Any]] = []
    summaries = {}
    rounds: dict[str, Any] = {}
    base, summary = _stage(root, "base", 0, "evaluation")
    stage_rows.append(base)
    if summary is not None:
        summaries[base["id"]] = summary
    planned = saved_scope
    if planned is None:
        planned = {(method, round_index) for method in config.get("methods", [])
                   for round_index in range(1, config.get("rounds", 1) + 1)}
        for directory in root.iterdir():
            if directory.is_dir() and directory.name != "base":
                for child in directory.iterdir():
                    match = re.fullmatch(r"round_([1-9][0-9]*)", child.name)
                    if child.is_dir() and match:
                        planned.add((directory.name, int(match.group(1))))
    for method, round_index in sorted(planned):
        relative = f"{method}/round_{round_index}"
        directory = root / relative
        rounds[relative] = {
            "training_stats": _first_optional(directory / "model" / "training_stats.json", directory / "training_stats.json"),
            "training_budget": _first_optional(directory / "train.jsonl.budget.json", directory / "train.budget.json"),
            "calibration_provenance": _read_optional(directory / 'calibration_provenance.json'),
        }
        for stage in ("generation_policy", "evaluation"):
            evaluation_only = saved_scope is not None and stage == "generation_policy"
            requested = stage == "evaluation" or (
                not evaluation_only and config.get("diagnostics", {}).get("evaluate_generation_policy", True))
            row, summary = _stage(root, method, round_index, stage, requested,
                                  include_existing=not evaluation_only)
            stage_rows.append(row)
            if summary is not None:
                summaries[row["id"]] = summary
    evaluation = config.get("evaluation", {})
    margin = evaluation.get("correctness_margin", 0.0)
    bootstrap = evaluation.get("bootstrap_samples", 1000)
    seed = config.get("seed", 42)
    by_id = {row["id"]: row for row in stage_rows}
    comparisons = []
    for row in stage_rows:
        if row["method"] == "base" or row["status"] == "not_requested":
            continue
        references = ["base/evaluation"]
        for method in config.get('reporting', {}).get('reference_methods', ['plain', 'ssd', 'spd_hard']):
            if row['method'] != method:
                reference = f"{method}/round_{row['round']}/{row['stage']}"
                if reference in by_id:
                    references.append(reference)
        for reference in references:
            comparisons.append(_comparison(row, by_id.get(reference), reference, summaries, margin, bootstrap, seed))
    output = Path(output_path) if output_path is not None else root / "report.json"
    if output.suffix.lower() not in {"", ".json", ".md"}:
        raise ValueError("output_path must end in .json or .md, or have no suffix")
    json_path, markdown_path = output.with_suffix(".json"), output.with_suffix(".md")
    report = {
        "schema_version": 1,
        "run_dir": str(root),
        "status": "complete" if all(row["status"] in {"available", "not_requested"} for row in stage_rows) else "pending",
        "stages": stage_rows,
        "rounds": rounds,
        "comparisons": comparisons,
        "comparison_settings": {"correctness_margin": margin, "bootstrap_samples": bootstrap, "seed": seed,
                                "confidence": .95, "unit": "paired_tasks"},
        "manifest": manifest,
        "outputs": {"json": str(json_path), "markdown": str(markdown_path)},
        "limitations": [
            "Implementation proxy fingerprints are not algorithm identities; semantic coverage requires complete independent labels per task.",
            "Partial eligible-task means and correct-count-matched means describe conditional populations, with explicit denominators.",
            "Missing metrics remain pending, and missing evaluation provenance prevents comparison.",
            "Confidence intervals are pointwise task-bootstrap intervals; no multiple-comparison correction or automatic research claim is made.",
        ],
    }
    json_text = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    markdown = _markdown(report)
    _write(json_path, json_text)
    _write(markdown_path, markdown)
    return report
