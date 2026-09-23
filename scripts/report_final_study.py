#!/usr/bin/env python3
"""Read sealed final-study artifacts and write CPU-only paper evidence tables.

This command never trains, loads model weights, executes generated code, or
changes source runs. Dependencies are imported only when reporting existing
metrics. Missing cells are x; completion is independent of observed outcomes.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import statistics
import sys
import tempfile


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
SEEDS = (43, 44, 45)
METHODS = ("plain", "ssd", "spectral_soft")
BOOTSTRAPS = 2000


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _path(value):
    path = Path(value)
    return path.resolve() if path.is_absolute() else (REPO / path).resolve()


def _rows(path):
    with Path(path).open(encoding="utf-8") as stream:
        for index, line in enumerate(stream, 1):
            if line.strip():
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError(f"Nonobject record at {path}:{index}")
                yield row


def _write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.name}.", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _csv(path, rows):
    fields = list(dict.fromkeys(key for row in rows for key in row)) or ["status", "reason"]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fields)
    writer.writeheader()
    for row in rows:
        writer.writerow({key: "x" if value is None else json.dumps(value, sort_keys=True)
                         if isinstance(value, (dict, list, tuple)) else value
                         for key, value in row.items()})
    _write(path, stream.getvalue())


def _rounds(job):
    if job["kind"] == "transfer":
        return [job["student_round"]]
    rounds = job["rounds"]
    if type(rounds) is int:
        return [rounds] if job["kind"] == "transfer" else list(range(1, rounds + 1))
    if not isinstance(rounds, list) or not rounds or any(type(n) is not int or n < 1 for n in rounds):
        raise ValueError("Job rounds must be a positive integer or a nonempty integer list")
    if len(set(rounds)) != len(rounds):
        raise ValueError("Duplicate requested rounds")
    return sorted(rounds)


def _dataset(job):
    return job.get("benchmark", job.get("dataset", "mbpp")) if job["kind"] == "transfer" else "mbpp"


def _validate_manifest(manifest):
    jobs = manifest.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        raise ValueError("Final-study manifest must contain planned jobs")
    ids = [job.get("job_id") for job in jobs]
    if any(not isinstance(value, str) or not value for value in ids) or len(set(ids)) != len(ids):
        raise ValueError("Job IDs must be present and unique")
    for job in jobs:
        if job.get("kind") not in {"training", "transfer"} or job.get("block") not in {"core", "diagnostic", "transfer"}:
            raise ValueError(f"Unrecognized planned job: {job['job_id']}")
        if not job.get("output_dir") or type(job.get("seed")) is not int:
            raise ValueError("Jobs require output_dir and integer seed")
        methods = job.get("methods")
        if not isinstance(methods, list) or not methods or len(set(methods)) != len(methods):
            raise ValueError("Jobs require unique methods")
        _rounds(job)
    core = [job for job in jobs if job["block"] == "core"]
    if sorted(job["seed"] for job in core) != list(SEEDS) or any(
        job["kind"] != "training" or set(job["methods"]) != set(METHODS) or _rounds(job) != [1, 2, 3, 4, 5]
        for job in core
    ):
        raise ValueError("The fixed core requires seeds 43/44/45, three methods, five rounds")
    diagnostic = {job["job_id"]: job for job in jobs if job["block"] == "diagnostic"}
    expected = {"weak-s43": ["spectral_soft"], "isotropic-s43": ["isotropic_soft"],
                "completion-s43": ["plain", "spectral_soft"]}
    if set(diagnostic) != set(expected) or any(
        diagnostic[key]["kind"] != "training" or diagnostic[key]["seed"] != 43
        or _rounds(diagnostic[key]) != [1] or set(diagnostic[key]["methods"]) != set(methods)
        for key, methods in expected.items()
    ):
        raise ValueError("The fixed four diagnostic arm-rounds are missing or changed")
    transfer = [job for job in jobs if job["kind"] == "transfer"]
    if len(transfer) != 6 or {(_dataset(job), job["seed"]) for job in transfer} != {
        (dataset, seed) for dataset in ("humanevalplus", "apps_intro") for seed in SEEDS
    } or any(set(job["methods"]) != set(METHODS) or _rounds(job) != [5] for job in transfer):
        raise ValueError("The fixed transfer block requires both datasets for all three seeds and methods")
    return jobs


def _seal(directory, filenames):
    marker = directory / "complete.json"
    if not marker.is_file():
        raise FileNotFoundError(f"Unsealed stage: {marker}")
    state = _read(marker)
    if state.get("status", "completed") != "completed":
        raise ValueError(f"Stage marker is not completed: {marker}")
    hashes = state.get("files", {})
    if not isinstance(hashes, dict):
        raise ValueError("Invalid completion-marker file hashes")
    for filename in filenames:
        path = directory / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing sealed artifact: {path}")
        if filename not in hashes:
            raise ValueError(f"Artifact is not sealed by the completion marker: {path}")
        digest = hashes[filename]
        if isinstance(digest, dict):
            digest = digest.get("sha256")
        if _sha(path) != digest:
            raise ValueError(f"Completion hash mismatch: {path}")
    return {"marker": str(marker), "marker_sha256": _sha(marker),
            "hashes": "checked"}


def _output_identity(job):
    """Gate even partial-run evidence on the actual run's planned identity."""
    from run_final_study import digest
    stored = _read(_path(job["output_dir"]) / "manifest.json")
    if job["kind"] == "training":
        if digest(stored.get("config")) != job["config_sha256"]:
            raise ValueError("Output manifest configuration differs from the planned job")
    else:
        protocol = stored.get("protocol", {})
        if (protocol.get("source_run") != job["source_run"] or protocol.get("methods") != job["methods"]
                or protocol.get("rounds") != [job["student_round"]] or protocol.get("seed") != job["seed"]
                or protocol.get("generation", {}).get("samples") != job["samples_per_task"]
                or protocol.get("task_sha256") != job["task_sha256"]
                or len(protocol.get("task_ids", [])) != job["task_count"] or not stored.get("fingerprint")):
            raise ValueError("Transfer output protocol differs from the planned job")
    return stored


def _metric_names(samples):
    return [f"pass@{k}" for k in (1, 8, 16, 32, 64) if k <= samples] + [f"C{samples}", "D4"]


def _values(summary, metric):
    def value(row):
        if metric.startswith("pass@"):
            return row["pass_at_k"].get(metric[5:])
        proxy = row["implementation_proxy"]
        if metric.startswith("C"):
            return proxy["coverage_at_k"].get(metric[1:])
        return proxy["correct_matched_coverage_at_budgets"].get("4")
    return {task: value(row) for task, row in summary["per_task"].items()}


def _estimate(values, seed):
    # Same task-bootstrap implementation and eligibility schema as the existing
    # longitudinal exporter; importing that module does not import torch.
    from improving.longitudinal import _estimate as estimate
    return estimate(values, BOOTSTRAPS, seed)


def _flat(estimate):
    interval = estimate.get("ci95")
    return {"mean": estimate.get("mean"), "ci95_low": interval[0] if interval else None,
            "ci95_high": interval[1] if interval else None,
            "eligible_tasks": estimate.get("eligible_tasks"), "total_tasks": estimate.get("total_tasks"),
            "bootstrap_valid_replicates": estimate.get("bootstrap_valid_replicates"),
            "eligible_task_ids": estimate.get("eligible_task_ids")}


def _meta(stage):
    return {key: stage[key] for key in ("job_id", "block", "dataset", "seed", "method", "round", "stage")}


def _scan(stage):
    """Validate retained rows, retain fingerprints/counts, never run code."""
    summary = stage["summary"]
    samples = stage["samples_per_task"]
    seen, correct, prompts, errors = defaultdict(set), Counter(), {}, Counter()
    for row in _rows(stage["records_path"]):
        task, sample = row.get("task_id"), row.get("sample_id")
        if task not in summary["per_task"] or type(sample) is not int or not 0 <= sample < samples:
            raise ValueError("Retained records have an unexpected task or sample ID")
        if sample in seen[task] or type(row.get("correct")) is not bool:
            raise ValueError("Retained records have duplicate keys or invalid correctness")
        seen[task].add(sample)
        correct[task] += row["correct"]
        fingerprint = row.get("prompt_sha256")
        if not isinstance(fingerprint, str) or len(fingerprint) != 64:
            raise ValueError("Retained records lack a rendered-prompt fingerprint")
        if task in prompts and prompts[task] != fingerprint:
            raise ValueError("A task has inconsistent rendered prompts")
        prompts[task] = fingerprint
        detail = row.get("verification_error") or {}
        if not isinstance(detail, dict):
            detail = {}
        errors[(str(row.get("status", "unknown")), str(row.get("finish_reason", "unknown")),
                str(detail.get("phase") or "unavailable"), str(detail.get("exception_type") or "unavailable"))] += 1
    for task, data in summary["per_task"].items():
        if len(seen[task]) != samples or correct[task] != data["correct_count"]:
            raise ValueError("Retained sample counts/correctness differ from sealed metrics")
    return prompts, [{**_meta(stage), "status": "available", "verification_status": key[0],
        "finish_reason": key[1], "failure_phase": key[2], "exception_type": key[3], "count": count,
        "fraction": count / (samples * len(summary["per_task"]))} for key, count in sorted(errors.items())]


def _load_stage(job, method, round_index, stage_kind="evaluation", config_error=None):
    directory = _path(job["output_dir"]) / ("base" if method == "base" else f"{method}/round_{round_index}")
    dataset = _dataset(job)
    samples = 16 if job["kind"] == "transfer" or stage_kind == "generation_policy" else 64
    count = 128 if stage_kind == "generation_policy" else {"mbpp": 500, "humanevalplus": 164, "apps_intro": 200}[dataset]
    stage = {"job_id": job["job_id"], "block": job["block"], "dataset": dataset, "seed": job["seed"],
             "method": method, "round": round_index, "stage": stage_kind, "directory": str(directory),
             "samples_per_task": samples, "planned_tasks": count, "status": "pending", "reason": ""}
    filenames = [f"{stage_kind}.metrics.json", f"{stage_kind}.jsonl.budget.json", f"{stage_kind}.verified.jsonl"]
    try:
        if config_error:
            raise config_error
        run_manifest = _output_identity(job)
        stage["integrity"] = _seal(directory, filenames)
        if job["kind"] == "transfer" and _read(directory / "complete.json").get("protocol_fingerprint") != run_manifest["fingerprint"]:
            raise ValueError("Transfer stage protocol differs from its output manifest")
        summary = _read(directory / filenames[0])
        per_task = summary.get("per_task", {})
        if len(per_task) != count or any(row.get("sample_count") != samples for row in per_task.values()):
            raise ValueError("Sealed metric task/sample counts differ from the fixed plan")
        task_file = _path(job["output_dir"]) / "tasks" / ("generation_diagnostic.jsonl" if stage_kind == "generation_policy" else "eval.jsonl")
        expected_tasks = list(_rows(task_file))
        if len(expected_tasks) != count or {row["task_id"] for row in expected_tasks} != set(per_task):
            raise ValueError("Saved task snapshot differs from the evaluated task universe")
        if stage_kind == "generation_policy":
            if set(run_manifest.get("generation_diagnostic_task_ids", [])) != set(per_task):
                raise ValueError("Teacher tasks differ from the declared fixed diagnostic subset")
        if not summary.get("protocol", {}).get("evaluation"):
            raise ValueError("Missing declared evaluator identity")
        budget = _read(directory / filenames[1])
        protocol = budget.get("protocol", {})
        if not protocol.get("prompts") or not isinstance(protocol.get("settings"), dict):
            raise ValueError("Missing generation prompt/decoding protocol")
        if protocol["settings"].get("samples") != samples or budget.get("tasks") != count or budget.get("samples") != count * samples:
            raise ValueError("Generation budget differs from the fixed plan")
        stage.update(summary=summary, budget=budget, records_path=str(directory / filenames[2]),
                     metrics_sha256=_sha(directory / filenames[0]))
        stage["prompts"], stage["error_rows"] = _scan(stage)
        stage["status"] = "available"
    except (OSError, ValueError, KeyError, TypeError) as error:
        stage["status"] = "pending" if isinstance(error, FileNotFoundError) else "invalid"
        stage["reason"] = str(error)
        stage.pop("summary", None)
    return stage


def _signature(stage, aligned=False):
    protocol = stage["budget"]["protocol"]
    settings = dict(protocol["settings"])
    if aligned:
        settings.pop("samples", None)
    return {"settings": settings, "prompts": stage["prompts"],
            "format": protocol.get("format"), "seed": protocol.get("seed")}


def _pair(reference, candidate, kind, *, aligned=False, same_decoder=True):
    from improving.metrics import compare_summaries
    samples = candidate["samples_per_task"]
    common = {"reference_job": reference["job_id"], "candidate_job": candidate["job_id"],
        "reference": f"{reference['method']}/round_{reference['round']}/{reference['stage']}",
        "candidate": f"{candidate['method']}/round_{candidate['round']}/{candidate['stage']}",
        "dataset": candidate["dataset"], "seed": candidate["seed"], "round": candidate["round"],
        "kind": kind, "same_decoder": same_decoder}
    try:
        if reference["status"] != "available" or candidate["status"] != "available":
            raise FileNotFoundError("Missing/invalid sealed comparison stage")
        if not same_decoder:
            raise ValueError("SSD teacher uses a different decoder; no causal teacher/student paired inference")
        if _signature(reference, aligned) != _signature(candidate, aligned):
            raise ValueError("Task/prompt fingerprints or generation settings differ")
        # Validate even a cached export; cached CIs are usable only when their
        # source metric hashes, bootstrap count and seed still match.
        compare_summaries(reference["summary"], candidate["summary"], bootstrap_samples=0)
        comparison = _cached_comparison(reference, candidate, kind) if not aligned else None
        if comparison is None:
            comparison = compare_summaries(reference["summary"], candidate["summary"],
                                           bootstrap_samples=BOOTSTRAPS, seed=candidate["seed"])
        output = []
        for metric in _metric_names(samples):
            if metric.startswith("pass@"):
                estimate = comparison["pass_at_k"].get(metric[5:])
            elif metric.startswith("C"):
                estimate = comparison["implementation_proxy"]["coverage_at_k"].get(metric[1:])
            else:
                estimate = comparison["implementation_proxy"]["correct_matched_coverage_at_budgets"].get("4")
            if estimate is None:
                raise ValueError(f"Missing metric protocol: {metric}")
            # D4's paired population is the intersection, never the difference
            # between two marginal means with different eligible populations.
            left, right = _values(reference["summary"], metric), _values(candidate["summary"], metric)
            ids = sorted(task for task in left if left[task] is not None and right.get(task) is not None)
            estimate = {**estimate, "eligible_task_ids": ids}
            output.append({**common, "metric": metric, "status": "available", "reason": "", **_flat(estimate)})
        return output
    except (OSError, ValueError, KeyError, TypeError) as error:
        return [{**common, "metric": metric, "status": "pending" if isinstance(error, FileNotFoundError) else "incomparable",
                 "reason": str(error), "mean": None, "ci95_low": None, "ci95_high": None,
                 "eligible_tasks": None, "total_tasks": candidate["planned_tasks"]}
                for metric in _metric_names(samples)]


def _estimates(stage):
    rows = []
    for metric in _metric_names(stage["samples_per_task"]):
        row = {**_meta(stage), "metric": metric, "status": stage["status"], "reason": stage["reason"]}
        if stage["status"] == "available":
            summary = stage["summary"]
            protocol = summary["protocol"]
            values = _values(summary, metric)
            estimate = None
            if protocol.get("bootstrap_samples") == BOOTSTRAPS and protocol.get("seed") == stage["seed"]:
                aggregate = summary["aggregate"]
                if metric.startswith("pass@"):
                    estimate = aggregate["pass_at_k"].get(metric[5:])
                elif metric.startswith("C"):
                    estimate = aggregate["implementation_proxy"]["coverage_at_k"].get(metric[1:])
                else:
                    estimate = aggregate["implementation_proxy"]["correct_matched_coverage_at_budgets"].get("4")
            estimate = dict(estimate) if estimate is not None else _estimate(values, stage["seed"])
            estimate["eligible_task_ids"] = sorted(task for task, value in values.items() if value is not None)
            row.update(_flat(estimate))
            if row["mean"] is None:
                row.update(status="unavailable", reason="No eligible tasks for this metric")
        else:
            row.update(mean=None, ci95_low=None, ci95_high=None, eligible_tasks=None, total_tasks=stage["planned_tasks"])
        rows.append(row)
    return rows


def _aligned(stage, tasks):
    from improving.metrics import summarize_records
    if stage["status"] != "available":
        raise ValueError("Alignment requires sealed available source stages")
    rows = [row for row in _rows(stage["records_path"]) if row["task_id"] in tasks and row["sample_id"] < 16]
    # Expected mapping checks missing whole tasks as well as every sample count.
    summary = summarize_records(rows, ks=[1, 8, 16], correct_budget=4, correct_budgets=[4],
                                expected_samples={task: 16 for task in tasks},
                                bootstrap_samples=BOOTSTRAPS, seed=stage["seed"])
    return {**stage, "summary": summary, "samples_per_task": 16, "planned_tasks": len(tasks),
            "prompts": {task: stage["prompts"][task] for task in tasks}}


def _teacher_rows(previous, teacher, student):
    context = {"job_id": teacher["job_id"], "method": teacher["method"], "round": teacher["round"],
               "seed": teacher["seed"], "dataset": "mbpp", "sampling": "fixed 128 tasks; sample IDs 0..15"}
    try:
        if any(stage["status"] != "available" for stage in (previous, teacher, student)):
            raise ValueError("Previous native, teacher, or student sealed artifacts are unavailable")
        tasks = set(teacher["summary"]["per_task"])
        if len(tasks) != 128:
            raise ValueError("Teacher task set differs from the fixed 128-task diagnostic")
        aligned = [_aligned(stage, tasks) for stage in (previous, teacher, student)]
        if not aligned[0]["prompts"] == aligned[1]["prompts"] == aligned[2]["prompts"]:
            raise ValueError("Teacher/native subset rendered prompts differ")
        output = []
        for role, stage in zip(("previous_native", "teacher_policy", "student_native"), aligned):
            for row in _estimates(stage):
                output.append({**row, **context, "kind": "level", "role": role,
                               "source_method": stage["method"], "source_round": stage["round"],
                               "same_decoder": teacher["method"] != "ssd" or role != "teacher_policy"})
        for left, right, kind in ((0, 1, "teacher_minus_previous"), (1, 2, "student_minus_teacher"),
                                  (0, 2, "student_minus_previous")):
            same = teacher["method"] != "ssd" or (left, right) == (0, 2)
            for row in _pair(aligned[left], aligned[right], kind, aligned=True, same_decoder=same):
                output.append({**row, **context, "role": "paired_change"})
        return output
    except (OSError, ValueError, KeyError, TypeError) as error:
        return [{**context, "kind": "alignment", "role": "all_three", "status": "pending",
                 "reason": str(error), "mean": None, "eligible_tasks": None}]


def _cross_seed_signature(stage):
    signature = _signature(stage)
    signature.pop("seed", None)
    protocol = stage["summary"]["protocol"]
    signature["metrics"] = {key: protocol.get(key) for key in (
        "ks", "correct_budget", "correct_budgets", "proxy_version", "metric_versions", "sampling",
        "evaluation", "evaluation_task_harnesses")}
    return signature


def _seed_rows(endpoints, pairs, stage_map):
    groups = defaultdict(dict)
    identities = defaultdict(dict)
    for row in endpoints:
        if row["block"] not in {"core", "transfer"}:
            continue
        for metric in _metric_names(64 if row["dataset"] == "mbpp" else 16) + ["richness_retention"]:
            key = ("endpoint", row["dataset"], row["method"], "", metric)
            groups[key][row["seed"]] = row.get(metric) if row["status"] == "available" else None
            stage = stage_map[(row["job_id"], row["method"], row["round"])]
            if stage["status"] == "available":
                identities[key][row["seed"]] = _cross_seed_signature(stage)
    for row in pairs:
        if row["kind"] != "same_round_method" or row["round"] != 5:
            continue
        key = ("paired_effect", row["dataset"], row["candidate"].split("/")[0], row["reference"].split("/")[0], row["metric"])
        groups[key][row["seed"]] = row["mean"] if row["status"] == "available" else None
        if row["status"] == "available":
            stages = [stage_map[(row[f"{side}_job"], row[side].split("/")[0], row["round"])]
                      for side in ("reference", "candidate")]
            identities[key][row["seed"]] = [_cross_seed_signature(stage) for stage in stages]
    output = []
    for (kind, dataset, method, reference, metric), values in sorted(groups.items()):
        complete = all(seed in values and values[seed] is not None for seed in SEEDS)
        comparable = complete and all(identities[(kind, dataset, method, reference, metric)].get(seed) ==
                                     identities[(kind, dataset, method, reference, metric)].get(SEEDS[0]) for seed in SEEDS)
        observed = [values[seed] for seed in SEEDS if values.get(seed) is not None]
        output.append({"kind": kind, "dataset": dataset, "method": method, "reference": reference,
            "metric": metric, "status": "available" if comparable else "incomparable_protocols" if complete else "incomplete_seed_set",
            "planned_seeds": list(SEEDS), "available_seeds": [seed for seed in SEEDS if values.get(seed) is not None],
            "seed_values": {str(seed): values.get(seed) for seed in SEEDS},
            "mean": statistics.mean(observed) if comparable else None,
            "sample_sd": statistics.stdev(observed) if comparable else None,
            "n_seeds": len(observed), "uncertainty": "between-seed sample SD; no pooled samples or task CI"})
    return output


def _cached_comparison(reference, candidate, kind):
    cache = candidate.get("longitudinal")
    if reference["job_id"] != candidate["job_id"] or not cache:
        return None
    bootstrap = cache.get("bootstrap", {})
    if bootstrap.get("samples") != BOOTSTRAPS or bootstrap.get("seed") != candidate["seed"]:
        return None
    def stage_id(stage):
        return "base" if stage["method"] == "base" else f"{stage['method']}/round_{stage['round']}"
    before, after = stage_id(reference), stage_id(candidate)
    exported = {row["id"]: row for row in cache.get("stages", [])}
    if any(exported.get(stage_id(stage), {}).get("metrics_sha256") != stage.get("metrics_sha256")
           for stage in (reference, candidate)):
        return None
    for comparison in cache.get("comparisons", []):
        if (comparison.get("reference"), comparison.get("candidate"), comparison.get("kind"), comparison.get("status")) == (before, after, kind, "available"):
            return comparison.get("result")
    return None


def _markdown(report):
    text = ["# Final fixed SPECTRUM study", "", f"Study status: **{report['status']}**.", "",
        "Completion means the fixed planned jobs and retained diagnostic artifacts are complete, regardless of effect sign. "
        "There is no automatic success gate, winner selection, extra seed, or adaptive tuning. Missing cells are `x`.", "",
        "C64/C16 denote correct Python AST richness at the stated total draw budget; D4 conditions on four correct samples. "
        "AST hashes are implementation proxies, not algorithm identities. D4 paired effects use the common eligible task cohort.", "",
        "Per-seed intervals use 2,000 paired/task bootstrap draws. They do not measure training-seed variation. "
        "The seed table gives mean and sample SD only when all seeds 43, 44, and 45 are present; samples are never pooled.", "",
        "## Planned endpoints", "",
        "| Job | Method | Round | Status | pass@1 | pass@16 | pass@64 | C64 / C16 | D4 | D4 eligible | Richness / own base |",
        "|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|"]
    def value(item):
        return "x" if item is None else f"{item:.4f}" if isinstance(item, (float, int)) else str(item)
    for row in report["endpoints"]:
        cells = [row["job_id"], row["method"], row["round"], row["status"], row.get("pass@1"), row.get("pass@16"),
                 row.get("pass@64"), row.get("C64", row.get("C16")), row.get("D4"), row.get("D4_eligible_tasks"), row.get("richness_retention")]
        text.append("| " + " | ".join(value(cell) for cell in cells) + " |")
    text += ["", "Intervals and all requested pass@1/8/16/32/64 values are retained in `endpoints.csv` and `trajectories.csv`. "
             "Negative and inconclusive effects remain in `paired_differences.csv`; diagnostic ablations remain in `ablations.csv`.", "",
             "## Interpretation boundaries", "",
             "- HumanEval+ requires official base and plus tests. APPS uses the recorded adapted functional/stdin verifier, not an official leaderboard protocol.",
             "- Teacher diagnostics align exactly 128 tasks and sample IDs 0–15 before intervention, under the generating policy, and after SFT. "
             "They compare sampled task distributions, not paired individual completions.",
             "- SSD teacher sampling differs from native sampling. Its levels are reported, while teacher/native causal paired effects are marked incomparable.",
             "- Fixed-correct richness uses an eligible subset; a positive D4 change cannot erase a negative all-task correctness or richness change.",
             "- Richness retention is a ratio of task-macro counts versus the same run's initial model, not identity retention of algorithms.",
             "- Error phase/type counts describe emitted diagnostics; missing details remain unavailable and are not inferred from exception text.", "",
             "- Operator tables retain average scaling and nonscalar directionality separately; neither is evidence of semantic diversity. "
             "Base resource metadata not covered by completion hashes is explicitly marked recorded_unsealed.", "",
             "## Job and artifact status", "", "| Job | Status | Reason |", "|---|---|---|"]
    for row in report["jobs"]:
        text.append(f"| {row['job_id']} | {row['status']} | {row.get('reason', '').replace('|', '/')} |")
    text += ["", "Source runs were read only. Reporting did not load weights, train models, or execute generated programs.", ""]
    return "\n".join(text)


def build_report(manifest_path, output_dir=None):
    from run_final_study import digest, job_status, load_manifest
    manifest_path = Path(manifest_path).resolve()
    manifest = load_manifest(manifest_path, verify_inputs=False)
    jobs = _validate_manifest(manifest)
    run_root = manifest.get("run_root") or manifest.get("output_dir") or manifest_path.parent
    output = _path(output_dir) if output_dir else _path(run_root) / "paper_report"
    if any(output.is_relative_to(_path(job["output_dir"])) for job in jobs):
        raise ValueError("Report output must not be inside a source job directory")
    stages, stage_map, teachers, statuses, resource_rows, error_rows, operator_rows = [], {}, [], [], [], [], []
    for job in jobs:
        root = _path(job["output_dir"])
        config_error = None
        if job["kind"] == "training":
            try:
                if not job.get("config_sha256") or digest(_read(_path(job["config"]))) != job["config_sha256"]:
                    raise ValueError("Planned training configuration hash changed or is missing")
            except (OSError, ValueError, KeyError) as error:
                config_error = error
        requested = [("base", 0)] + [(method, index) for index in _rounds(job) for method in job["methods"]]
        local = []
        for method, index in requested:
            stage = _load_stage(job, method, index, config_error=config_error)
            stages.append(stage)
            local.append(stage)
            stage_map[(job["job_id"], method, index)] = stage
            if job["kind"] == "training" and method != "base":
                teacher = _load_stage(job, method, index, "generation_policy", config_error)
                teachers.append(teacher)
                local.append(teacher)
        cache = root / "longitudinal" / "longitudinal.json"
        if cache.is_file():
            try:
                cached = _read(cache)
                for stage in local:
                    if stage["stage"] == "evaluation":
                        stage["longitudinal"] = cached
            except (OSError, ValueError):
                pass  # Derived cache is optional; sealed source metrics remain authoritative.
        integrity_issues = []
        for stage in local:
            if stage["status"] != "available":
                error_rows.append({**_meta(stage), "status": stage["status"], "reason": stage["reason"], "count": None})
                continue
            error_rows.extend(stage["error_rows"])
            if stage["stage"] != "evaluation":
                continue
            operator_path = Path(stage["directory"]) / "operator_diagnostics.json"
            if job["kind"] == "training" and stage["method"] not in {"plain", "ssd", "base"}:
                try:
                    _seal(Path(stage["directory"]), [operator_path.name])
                    operators = _read(operator_path)
                    for layer, values in sorted(operators.items()):
                        operator_rows.append({**_meta(stage), "layer": layer, "status": "available",
                            **{key: values.get(key) for key in ("dimension", "eigenvalue_min", "eigenvalue_max",
                                "operator_eigenvalues", "mean_eigenvalue", "nonscalar_frobenius_norm",
                                "nonscalar_fraction_of_operator_norm", "operator_frobenius_norm",
                                "frobenius_distance_from_identity", "matching_contract", "matching_absolute_error",
                                "activation_rms_matched", "output_kl_matched", "folded_weight_relative_delta")},
                            "path": str(operator_path)})
                except (OSError, ValueError, TypeError) as error:
                    integrity_issues.append(str(error))
                    operator_rows.append({**_meta(stage), "status": "unavailable", "reason": str(error),
                                          "mean_eigenvalue": None, "nonscalar_frobenius_norm": None})
            for path in sorted(Path(stage["directory"]).glob("*.resources.json")):
                unsealed_base = False
                try:
                    unsealed_base = stage["method"] == "base" and path.name not in _read(
                        Path(stage["directory"]) / "complete.json").get("files", {})
                    if not unsealed_base:
                        _seal(Path(stage["directory"]), [path.name])
                    record = _read(path)
                    resource_rows.append({**_meta(stage), "resource_stage": record.get("stage", path.stem),
                        "status": "recorded_unsealed" if unsealed_base else "available",
                        "execution_status": record.get("status"), "elapsed_seconds": record.get("elapsed_seconds"),
                        "cuda_peak_allocated_bytes": record.get("cuda_peak_allocated_bytes"),
                        "cuda_peak_reserved_bytes": record.get("cuda_peak_reserved_bytes"), "path": str(path)})
                except (OSError, ValueError) as error:
                    if not unsealed_base:
                        integrity_issues.append(str(error))
                    resource_rows.append({**_meta(stage), "status": "invalid", "reason": str(error), "path": str(path)})
            if job["kind"] == "training" and stage["method"] != "base":
                path = Path(stage["directory"]) / "training_stats.json"
                try:
                    _seal(path.parent, [path.name])
                    stats = _read(path)
                    resource_rows.append({**_meta(stage), "resource_stage": "training_stats", "status": "available",
                        **{key: stats.get(key) for key in ("examples", "optimizer_steps", "epochs", "loss_scope",
                            "supervised_tokens_per_epoch", "truncated_examples", "truncated_tokens",
                            "trainable_parameter_count", "mean_loss")}, "path": str(path)})
                except (OSError, ValueError, TypeError) as error:
                    integrity_issues.append(str(error))
                    resource_rows.append({**_meta(stage), "status": "invalid", "reason": str(error), "path": str(path)})
            for filename in ("train.jsonl.budget.json", "generation_policy.jsonl.budget.json", "evaluation.jsonl.budget.json"):
                path = Path(stage["directory"]) / filename
                if path.is_file():
                    try:
                        _seal(Path(stage["directory"]), [filename])
                        budget = _read(path)
                        resource_rows.append({**_meta(stage), "resource_stage": filename, "status": "available",
                            **{key: budget.get(key) for key in ("samples", "generation_tokens", "prompt_tokens", "length_capped_samples")},
                            "path": str(path)})
                    except (OSError, ValueError) as error:
                        integrity_issues.append(str(error))
                        resource_rows.append({**_meta(stage), "status": "invalid", "reason": str(error), "path": str(path)})
        native_status = job_status(job, verify_hashes=False)
        complete = (all(stage["status"] == "available" for stage in local)
                    and native_status["status"] == "completed" and not integrity_issues)
        reason = "; ".join(native_status.get("issues", []) + integrity_issues)
        if not complete and not reason:
            reason = "Planned sealed stages, diagnostics, or completion marker are missing/invalid"
        statuses.append({"job_id": job["job_id"], "status": "completed" if complete else "incomplete", "reason": reason})

    trajectories, endpoints, pairs = [], [], []
    for job in jobs:
        base = stage_map[(job["job_id"], "base", 0)]
        for method, index in [("base", 0)] + [(m, i) for i in _rounds(job) for m in job["methods"]]:
            stage = stage_map[(job["job_id"], method, index)]
            estimates = _estimates(stage)
            trajectories.extend(estimates)
            if index not in {0, max(_rounds(job))}:
                continue
            endpoint = {**_meta(stage), "status": stage["status"], "reason": stage["reason"],
                        "samples_per_task": stage["samples_per_task"], "planned_tasks": stage["planned_tasks"]}
            for estimate in estimates:
                metric = estimate["metric"]
                endpoint.update({metric: estimate["mean"], f"{metric}_ci95_low": estimate["ci95_low"],
                    f"{metric}_ci95_high": estimate["ci95_high"], f"{metric}_eligible_tasks": estimate["eligible_tasks"]})
            endpoint["richness_retention"] = None
            if base["status"] == stage["status"] == "available":
                try:
                    if _signature(base) != _signature(stage):
                        raise ValueError("Own-base prompt or decoding protocol differs")
                    from improving.metrics import compare_summaries
                    from improving.longitudinal import _retention_ratio
                    compare_summaries(base["summary"], stage["summary"], bootstrap_samples=0)
                    metric = f"C{stage['samples_per_task']}"
                    ratio = _retention_ratio(_values(base["summary"], metric), _values(stage["summary"], metric), BOOTSTRAPS, job["seed"])
                    endpoint["richness_retention"] = ratio["mean_ratio"]
                    endpoint["retention_ci95"] = ratio["ci95"]
                except (ValueError, KeyError) as error:
                    endpoint["retention_reason"] = str(error)
            endpoints.append(endpoint)
        for index in _rounds(job):
            for method in job["methods"]:
                candidate = stage_map[(job["job_id"], method, index)]
                pairs.extend(_pair(base, candidate, "initial_model"))
                if index > 1 and (job["job_id"], method, index - 1) in stage_map:
                    pairs.extend(_pair(stage_map[(job["job_id"], method, index - 1)], candidate, "adjacent_round"))
            for reference, candidate in (("plain", "spectral_soft"), ("ssd", "spectral_soft"), ("plain", "ssd")):
                if reference in job["methods"] and candidate in job["methods"]:
                    pairs.extend(_pair(stage_map[(job["job_id"], reference, index)], stage_map[(job["job_id"], candidate, index)], "same_round_method"))

    core43 = next(job for job in jobs if job["block"] == "core" and job["seed"] == 43)["job_id"]
    ablations = []
    for ref_job, ref_method, job_id, method, label in (
        (core43, "spectral_soft", "weak-s43", "spectral_soft", "weaker_tau_0.5_vs_fixed_tau_1"),
        (core43, "spectral_soft", "isotropic-s43", "isotropic_soft", "matched_isotropic_vs_spectrum"),
        ("completion-s43", "plain", "completion-s43", "spectral_soft", "completion_loss_matched_plain_vs_soft"),
        (core43, "spectral_soft", "completion-s43", "spectral_soft", "loss_ablation_completion_vs_all_tokens"),
    ):
        ablations.extend(_pair(stage_map[(ref_job, ref_method, 1)], stage_map[(job_id, method, 1)], label))
    teacher_rows = []
    for teacher in teachers:
        previous = stage_map[(teacher["job_id"], "base" if teacher["round"] == 1 else teacher["method"], teacher["round"] - 1)]
        student = stage_map[(teacher["job_id"], teacher["method"], teacher["round"])]
        teacher_rows.extend(_teacher_rows(previous, teacher, student))
    report = {"schema_version": 1, "study": manifest.get("study"), "manifest_path": str(manifest_path),
        "manifest_sha256": _sha(manifest_path), "protocol": manifest.get("protocol"),
        "status": "completed" if all(row["status"] == "completed" for row in statuses) else "incomplete",
        "bootstrap": {"samples": BOOTSTRAPS, "unit": "tasks", "confidence": 0.95, "training_seed_uncertainty": False},
        "jobs": statuses, "endpoints": endpoints, "trajectories": trajectories, "paired_differences": pairs,
        "seed_summary": _seed_rows(endpoints, pairs, stage_map), "teacher_student": teacher_rows,
        "errors": error_rows, "resources": resource_rows, "operators": operator_rows, "ablations": ablations,
        "stages": [{key: value for key, value in stage.items() if key not in {"summary", "error_rows", "prompts", "longitudinal"}}
                   for stage in stages + teachers]}
    for name in ("endpoints", "trajectories", "paired_differences", "seed_summary", "teacher_student", "errors", "resources", "operators", "ablations"):
        _csv(output / f"{name}.csv", report[name])
    _write(output / "summary.json", json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    _write(output / "REPORT.md", _markdown(report))
    return {"status": report["status"], "output_dir": str(output), "completed_jobs": sum(row["status"] == "completed" for row in statuses), "planned_jobs": len(jobs)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(build_report(args.manifest, args.output_dir), indent=2))
    except (OSError, ValueError, KeyError, TypeError, ImportError) as error:
        parser.exit(2, f"error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
