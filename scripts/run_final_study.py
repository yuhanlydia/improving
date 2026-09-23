#!/usr/bin/env python3
"""Freeze, inspect, and explicitly execute the finite final self-distillation study.

Planning and status use only the standard library, without model imports,
downloads, candidate execution, or GPU access. Planning requires prepared data.
Execution is sequential and resumes the native pipeline; it never selects a
configuration from evaluation outcomes or expands this fixed experiment matrix.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import unicodedata


REPO = Path(__file__).resolve().parents[1]
STUDY = "final_study_v1"
REVISION = "2e1fd397ee46e1388853d2af2c993145b0f1098a"
SEEDS = (43, 44, 45)
METHODS = ("plain", "ssd", "spectral_soft")
BENCHMARKS = ("humanevalplus", "apps_intro")
COUNTS = {"train": 291, "calibration": 50, "validation": 30, "eval": 500}
DEFAULT_MANIFEST = "runs/final_study_v1/plan/manifest.json"

# Import the existing stdlib-only planner by its known file path. In particular,
# do not import improving.pipeline merely to construct or inspect a plan.
_spec = importlib.util.spec_from_file_location("_final_native_planner", REPO / "scripts/run_iclr2027.py")
if _spec is None or _spec.loader is None:
    raise ImportError("Cannot load scripts/run_iclr2027.py")
_native = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_native)
native_config = _native.native_config
preflight = _native.preflight
digest = _native.digest
immutable_json = _native.immutable_json


def read_json(path):
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)


def file_sha(path):
    checksum = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def resolved(path):
    path = Path(path).expanduser()
    return (path if path.is_absolute() else REPO / path).resolve()


def contained(path, root):
    path, root = resolved(path), resolved(root)
    if path == root or not path.is_relative_to(root):
        raise ValueError(f"Path must be contained within {root}: {path}")
    return path


def jsonl(path):
    rows = []
    with Path(path).open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if line.strip():
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError(f"{path}:{line_number}: expected a JSON object")
                rows.append(row)
    return rows


def snapshot_file(path, *, count=None):
    path = resolved(path)
    result = {"path": str(path), "sha256": file_sha(path), "bytes": path.stat().st_size}
    if count is not None:
        result["count"] = count
    return result


def prompt_key(value):
    return " ".join(unicodedata.normalize("NFKC", value).split())


def task_keys(rows, split, *, references=False):
    ids, prompts = set(), set()
    for row in rows:
        task_id, prompt = row.get("task_id"), row.get("prompt")
        if (not isinstance(task_id, str) or not task_id or task_id in ids or
                not isinstance(prompt, str) or not prompt.strip() or row.get("split") != split):
            raise ValueError(f"Invalid/duplicate task or split in prepared {split} snapshot")
        if references and not row.get("reference"):
            raise ValueError(f"Calibration reference is missing: {task_id}")
        ids.add(task_id)
        for key in ("prompt", "original_prompt"):
            if row.get(key):
                prompts.add(prompt_key(row[key]))
    return ids, prompts


def prepared_snapshots(data_root, benchmark_root):
    """Pin the actual local snapshots; neither preparation nor downloads occur."""
    snapshots, split_keys = {}, {}
    for split, expected in COUNTS.items():
        path = data_root / f"{split}.jsonl"
        if not path.is_file():
            raise FileNotFoundError(f"Prepare MBPP before planning; missing {path}. "
                                   "Use python -m improving prepare --dataset mbpp --output-dir "
                                   f"{shlex.quote(str(data_root))} --seed 42")
        rows = jsonl(path)
        if len(rows) != expected:
            raise ValueError(f"Frozen MBPP protocol requires {expected} {split} tasks; got {len(rows)}")
        split_keys[split] = task_keys(rows, split, references=split == "calibration")
        snapshots[f"mbpp/{split}.jsonl"] = snapshot_file(path, count=len(rows))
    names = list(COUNTS)
    for index, name in enumerate(names):
        for other in names[index + 1:]:
            if any(left & right for left, right in zip(split_keys[name], split_keys[other])):
                raise ValueError(f"Prepared MBPP splits overlap: {name} and {other}")
    for filename in ("preparation_manifest.jsonl", "manifest.json"):
        path = data_root / filename
        if path.is_file():
            snapshots[f"mbpp/{filename}"] = snapshot_file(path)
    preparation_path = data_root / "preparation_manifest.jsonl"
    if preparation_path.is_file():
        metadata = jsonl(preparation_path)
        if (len(metadata) != 1 or metadata[0].get("split_seed") != 42 or
                metadata[0].get("output_counts") != COUNTS):
            raise ValueError("MBPP preparation metadata must match seed 42 and the frozen split counts")
    fit_ids = set().union(*(split_keys[name][0] for name in ("train", "calibration", "validation")))
    fit_prompts = set().union(*(split_keys[name][1] for name in ("train", "calibration", "validation")))
    transfer_counts = {}
    for benchmark in BENCHMARKS:
        directory = benchmark_root / benchmark
        manifest_path, task_path = directory / "manifest.json", directory / "eval.jsonl"
        if not manifest_path.is_file() or not task_path.is_file():
            raise FileNotFoundError(f"Prepare {benchmark} before planning: expected {manifest_path} "
                "and eval.jsonl. Use scripts/prepare_iclr_benchmarks.py with --datasets "
                "humanevalplus apps_intro and --exclude-training pointing to MBPP "
                "train.jsonl calibration.jsonl validation.jsonl. Planning never downloads data.")
        manifest = read_json(manifest_path)
        outputs = manifest.get("output_files", {})
        if manifest.get("name") != benchmark or not isinstance(outputs, dict) or "eval.jsonl" not in outputs:
            raise ValueError(f"Invalid prepared benchmark manifest: {manifest_path}")
        for filename, declared in outputs.items():
            path = contained(directory / filename, directory)
            if not path.is_file() or file_sha(path) != declared.get("sha256"):
                raise ValueError(f"Prepared benchmark is missing or changed: {path}")
            snapshots[f"{benchmark}/{filename}"] = snapshot_file(path, count=declared.get("count"))
        snapshots[f"{benchmark}/manifest.json"] = snapshot_file(manifest_path)
        rows = jsonl(task_path)
        if not rows or len(rows) != outputs["eval.jsonl"].get("count"):
            raise ValueError(f"Prepared task count differs from its manifest: {task_path}")
        ids, prompts = task_keys(rows, "eval")
        if ids & fit_ids or prompts & fit_prompts:
            raise ValueError(f"Prepared {benchmark} overlaps MBPP fitting data")
        if benchmark == "humanevalplus" and (len(rows) != 164 or
                manifest.get("evaluation_backend") != "evalplus" or
                "dataset_metadata.json" not in outputs or
                not (directory / "dataset_metadata.json").is_file() or
                any(row.get("evaluation_backend") != "evalplus" for row in rows)):
            raise ValueError("HumanEval+ must contain all 164 official EvalPlus tasks and dataset metadata")
        if benchmark == "apps_intro" and len(rows) != 200:
            raise ValueError("The frozen APPS introductory protocol requires exactly 200 prepared tasks")
        transfer_counts[benchmark] = len(rows)
    return snapshots, transfer_counts


def source_snapshot():
    # The native pipeline also binds all improving modules to its resume identity.
    paths = set((REPO / "src/improving").rglob("*.py"))
    paths.update(REPO / name for name in (
        "scripts/run_final_study.py", "scripts/run_iclr2027.py",
        "scripts/export_longitudinal.py", "scripts/report_final_study.py",
        "scripts/evalplus_docker.sh",
        "experiments/iclr2027/transfer.py"))
    return {str(path.relative_to(REPO)): file_sha(path) for path in sorted(paths)}


def training_config(args, job_id, methods, rounds, *, tau=1.0, loss_scope="all", seed=43):
    config = native_config(args, "qwen1.5b", seed)
    config.update(label=job_id, methods=list(methods), rounds=rounds,
                  output_dir=str(contained(args.run_root / "jobs" / job_id, args.run_root)))
    config["model"]["revision"] = REVISION
    config["calibration"]["tau"] = tau
    config["train"]["loss_scope"] = loss_scope
    config["diagnostics"]["evaluate_generation_policy"] = True
    return config


def training_job(args, job_id, block, config):
    path = contained(args.run_root / "plan/configs" / f"{job_id}.json", args.run_root)
    return {"job_id": job_id, "kind": "training", "block": block,
            "config": str(path), "config_sha256": digest(config),
            "output_dir": config["output_dir"], "rounds": config["rounds"],
            "methods": config["methods"], "seed": config["seed"],
            "command": ["python", "-m", "improving", "run", "--config", str(path), "--resume"],
            "after": ["python", "scripts/export_longitudinal.py", "export", "--run-dir",
                      config["output_dir"], "--output-dir", str(Path(config["output_dir"]) / "longitudinal"),
                      "--bootstrap-samples", "2000", "--reference-methods", "plain,ssd"],
            "depends_on": []}


def transfer_job(args, source, benchmark, snapshot):
    job_id = f"transfer-{benchmark}-s{source['seed']}"
    output = str(contained(args.run_root / "jobs" / job_id, args.run_root))
    batch = 8 if args.profile == "24gb" else 32
    command = ["python", "experiments/iclr2027/transfer.py", "--run-dir", source["output_dir"],
               "--benchmark", benchmark, "--benchmark-root", str(args.benchmark_root),
               "--output-dir", output, "--round", "5", "--methods", ",".join(METHODS),
               "--samples", "16", "--bootstrap-samples", "2000", "--max-prompt-tokens", "4096",
               "--max-new-tokens", "1024", "--sequence-batch-size", str(batch),
               "--timeout", "30", "--backend", args.backend, "--resume"]
    if args.allow_unsafe_local:
        command.append("--allow-unsafe-local")
    return {"job_id": job_id, "kind": "transfer", "block": "transfer", "config": None,
            "output_dir": output, "rounds": 1, "student_round": 5, "methods": list(METHODS),
            "seed": source["seed"], "source_run": source["output_dir"], "benchmark": benchmark,
            "samples_per_task": 16, "task_count": snapshot["count"], "task_sha256": snapshot["sha256"],
            "command": command, "after": [],
            "depends_on": [source["job_id"]]}


def candidate_budget(transfer_counts):
    train = 49 * 291 * 16
    students, bases, teachers = 49 * 500 * 64, 6 * 500 * 64, 49 * 128 * 16
    transfer = {name: {"tasks": count, "students": 3 * 3 * count * 16,
                       "bases": 3 * count * 16, "total": 3 * 4 * count * 16}
                for name, count in transfer_counts.items()}
    transfer_total = sum(value["total"] for value in transfer.values())
    return {"method_seed_rounds": 49, "training_candidates": train,
            "native_student_evaluation_candidates": students, "native_base_evaluation_candidates": bases,
            "native_evaluation_candidates": students + bases,
            "teacher_diagnostic_candidates": teachers,
            "teacher_diagnostic_tasks_per_stage": 128, "teacher_diagnostic_samples_per_task": 16,
            "transfer": transfer, "transfer_candidates": transfer_total,
            "total_candidates": train + students + bases + teachers + transfer_total,
            "calibration_generated_candidates": 0,
            "definition": "Fresh-run candidate counts; calibration uses 50 fixed references. "
                "Transfer includes one base evaluation per source seed and benchmark. "
                "Retries may consume additional compute; candidate caps do not match tokens or FLOPs."}


def build_plan(args):
    if args.backend == "local" and not args.allow_unsafe_local:
        raise ValueError("Local candidate execution requires --allow-unsafe-local; Docker is the default")
    if args.workers < 1:
        raise ValueError("workers must be positive")
    args.run_root, args.data_root, args.benchmark_root = map(resolved,
        (args.run_root, args.data_root, args.benchmark_root))
    snapshots, transfer_counts = prepared_snapshots(args.data_root, args.benchmark_root)
    configs, jobs = {}, []
    for seed in SEEDS:
        job_id = f"core-s{seed}"
        config = training_config(args, job_id, METHODS, 5, seed=seed)
        configs[job_id] = config
        jobs.append(training_job(args, job_id, "core", config))
    for job_id, methods, tau, loss_scope in (
        ("weak-s43", ("spectral_soft",), 0.5, "all"),
        ("isotropic-s43", ("isotropic_soft",), 1.0, "all"),
        ("completion-s43", ("plain", "spectral_soft"), 1.0, "completion")):
        config = training_config(args, job_id, methods, 1, tau=tau, loss_scope=loss_scope)
        configs[job_id] = config
        jobs.append(training_job(args, job_id, "diagnostic", config))
    for source in jobs[:3]:
        jobs.extend(transfer_job(args, source, benchmark, snapshots[f"{benchmark}/eval.jsonl"])
                    for benchmark in BENCHMARKS)
    budget = candidate_budget(transfer_counts)
    value = {"schema_version": 1, "study": STUDY, "run_root": str(args.run_root),
             "protocol": {"training_dataset": "MBPP", "data_seed": 42, "seeds": list(SEEDS),
                "model": "Qwen/Qwen2.5-Coder-1.5B-Instruct", "model_revision": REVISION,
                "core_rounds": 5, "diagnostic_rounds": 1, "training_samples_per_task": 16,
                "evaluation_samples_per_task": 64, "mbpp_counts": COUNTS,
                "calibration": "50 fixed training-split references; geometry re-estimated each round",
                "teacher_diagnostics": {"enabled": True, "task_limit": 128, "samples_per_task": 16},
                "checkpoint_retention": "all", "task_bootstrap_resamples": 2000,
                "uncertainty_unit": "paired evaluation tasks within each seed; three seeds reported separately",
                "selection": "finite predeclared suite; publish negative and inconclusive results; no automatic selection",
                "candidate_budgets_matched": True, "token_or_FLOP_budgets_matched": False,
                "profile": args.profile, "backend": args.backend, "allow_unsafe_local": args.allow_unsafe_local,
                "workers": args.workers, "data_root": str(args.data_root),
                "benchmark_root": str(args.benchmark_root), "python_transport": "current sys.executable at execution",
                "transfer": {"benchmarks": list(BENCHMARKS), "student_round": 5, "samples_per_task": 16,
                    "max_prompt_tokens": 4096, "max_new_tokens": 1024, "timeout": 30,
                    "training_on_target": False, "calibration_on_target": False,
                    "humanevalplus_evaluator": "official_evalplus_base_and_plus"},
                "candidate_budget": budget, "dataset_snapshots": snapshots,
                "implementation_sha256": source_snapshot()}, "jobs": jobs}
    value["manifest_sha256"] = digest(value)
    path = contained(args.run_root / "plan/manifest.json", args.run_root)
    # Check all existing values before writing anything, so a conflicting plan
    # cannot leave a mixture of configurations from two proposed protocols.
    writes = [(Path(job["config"]), configs[job["job_id"]]) for job in jobs if job["kind"] == "training"]
    writes.append((path, value))
    for target, document in writes:
        if target.exists() and read_json(target) != document:
            raise ValueError(f"Refusing to overwrite a different plan/configuration: {target}; use a new --run-root")
    for target, document in writes:
        immutable_json(target, document)
    print(f"Manifest: {path}\nSix training jobs and six transfer jobs; no experiments executed.")
    print(f"Method-seed-rounds: 49; train-only candidates: {budget['training_candidates']:,}")
    print(f"Native student evaluation: {budget['native_student_evaluation_candidates']:,}; "
          f"native base evaluation: {budget['native_base_evaluation_candidates']:,}")
    print(f"Teacher diagnostics: {budget['teacher_diagnostic_candidates']:,} (128 tasks x 16 samples x 49 stages)")
    for name, counts in budget["transfer"].items():
        print(f"Transfer {name}: {counts['total']:,} ({counts['tasks']} tasks; students {counts['students']:,}, bases {counts['bases']:,})")
    print(f"Total fresh-run candidates: {budget['total_candidates']:,}; calibration generates zero candidates.")
    print("Inspect with: python scripts/run_final_study.py status --manifest " + shlex.quote(str(path)))
    print("Run an explicit block with: python scripts/run_final_study.py run --manifest " +
          shlex.quote(str(path)) + " --block core")
    return 0


def load_manifest(path, verify_inputs=False):
    path = resolved(path)
    manifest = read_json(path)
    if manifest.get("study") != STUDY or manifest.get("schema_version") != 1:
        raise ValueError("Expected a final_study_v1 manifest with schema_version=1")
    if digest({key: value for key, value in manifest.items() if key != "manifest_sha256"}) != manifest.get("manifest_sha256"):
        raise ValueError("Study manifest changed since planning; create a new plan")
    root = resolved(manifest["run_root"])
    if path != contained(root / "plan/manifest.json", root):
        raise ValueError("Manifest must remain at its planned run-root/plan/manifest.json path")
    expected = {f"core-s{seed}" for seed in SEEDS} | {"weak-s43", "isotropic-s43", "completion-s43"}
    expected |= {f"transfer-{benchmark}-s{seed}" for seed in SEEDS for benchmark in BENCHMARKS}
    jobs = manifest.get("jobs", [])
    if len(jobs) != 12 or {job["job_id"] for job in jobs} != expected:
        raise ValueError("Manifest must contain exactly the frozen six training and six transfer jobs")
    for job in jobs:
        if resolved(job["output_dir"]) != contained(root / "jobs" / job["job_id"], root):
            raise ValueError(f"Output path differs from the frozen job path: {job['job_id']}")
        if job["kind"] == "training":
            if resolved(job["config"]) != contained(root / "plan/configs" / (job["job_id"] + ".json"), root):
                raise ValueError("Configuration path is outside the immutable plan")
            config = read_json(job["config"])
            if digest(config) != job["config_sha256"]:
                raise ValueError(f"Configuration changed since planning: {job['job_id']}")
            if (config["output_dir"] != job["output_dir"] or config["rounds"] != job["rounds"] or
                    config["methods"] != job["methods"] or config["seed"] != job["seed"]):
                raise ValueError(f"Job/configuration mismatch: {job['job_id']}")
    if verify_inputs:
        verify_plan_inputs(manifest)
    return manifest


def verify_plan_inputs(manifest):
    for name, snapshot in manifest["protocol"]["dataset_snapshots"].items():
        path = Path(snapshot["path"])
        if not path.is_file() or file_sha(path) != snapshot["sha256"]:
            raise ValueError(f"Dataset snapshot changed or is missing since planning: {name}: {path}")
    if source_snapshot() != manifest["protocol"]["implementation_sha256"]:
        raise ValueError("Relevant implementation changed since planning; create a new plan in a new run root")


def verify_marker(directory, *, base=False, transfer_fingerprint=None, verify_hashes=False):
    """Validate completion metadata and artifacts, not merely marker existence.

    Status checks metadata and file existence. Before a dependency is consumed,
    hash all artifacts including retained model shards without loading a model.
    """
    marker = directory / "complete.json"
    if not marker.is_file():
        return False, "completion marker missing"
    try:
        state = read_json(marker)
        if not state.get("model_identity"):
            return False, "model identity missing"
        if transfer_fingerprint is not None:
            if state.get("status") != "completed" or state.get("protocol_fingerprint") != transfer_fingerprint:
                return False, "transfer completion protocol/status mismatch"
        elif base:
            if state.get("integrity_schema") != 2 or state.get("resolved_revision") != REVISION:
                return False, "base completion integrity/revision mismatch"
        elif state.get("status") != "completed" or state.get("checkpoint_status") == "pruned":
            return False, "round is incomplete or checkpoint was pruned"
        files = state.get("files")
        required = {"evaluation.jsonl", "evaluation.verified.jsonl", "evaluation.metrics.json"}
        if not base and transfer_fingerprint is None:
            required |= {"train.jsonl", "training_stats.json", "model/config.json",
                         "generation_policy.jsonl", "generation_policy.verified.jsonl", "generation_policy.metrics.json"}
        if not isinstance(files, dict) or not required <= files.keys():
            return False, "completion marker omits required artifacts"
        if not base and transfer_fingerprint is None and not any(
                name.startswith("model/") and name.endswith((".bin", ".safetensors")) for name in files):
            return False, "completion marker omits retained model weights"
        for name, expected in files.items():
            path = contained(directory / name, directory)
            if not isinstance(expected, str) or len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
                return False, f"invalid artifact checksum metadata: {name}"
            if not path.is_file():
                return False, f"missing artifact: {name}"
            if verify_hashes and file_sha(path) != expected:
                return False, f"artifact checksum mismatch: {name}"
        if base and transfer_fingerprint is None and state.get("evaluation_sha") != files["evaluation.jsonl"]:
            return False, "base evaluation checksum metadata mismatch"
    except (OSError, ValueError, TypeError, KeyError) as error:
        return False, str(error)
    return True, None


def job_status(job, verify_hashes=False):
    root = Path(job["output_dir"])
    stages = ["base"] + [f"{method}/round_{index}" for method in job["methods"]
                           for index in (range(1, job["rounds"] + 1) if job["kind"] == "training" else [5])]
    result = {"job_id": job["job_id"], "block": job["block"], "status": "pending",
              "completed_stages": 0, "expected_stages": len(stages), "issues": [], "output_dir": str(root)}
    if not root.exists():
        return result
    result["status"] = "partial"
    try:
        stored = read_json(root / "manifest.json")
        if job["kind"] == "training":
            if digest(stored.get("config")) != job["config_sha256"]:
                raise ValueError("Output manifest configuration differs from the planned job")
            fingerprint = None
        else:
            protocol = stored.get("protocol", {})
            if (protocol.get("source_run") != job["source_run"] or protocol.get("methods") != job["methods"] or
                    protocol.get("rounds") != [5] or protocol.get("seed") != job["seed"] or
                    protocol.get("generation", {}).get("samples") != 16 or
                    protocol.get("task_sha256") != job["task_sha256"] or
                    len(protocol.get("task_ids", [])) != job["task_count"]):
                raise ValueError("Transfer output protocol differs from the planned job")
            fingerprint = stored.get("fingerprint")
            if not fingerprint:
                raise ValueError("Transfer output has no protocol fingerprint")
        for stage in stages:
            ok, reason = verify_marker(root / stage, base=stage == "base",
                                       transfer_fingerprint=fingerprint, verify_hashes=verify_hashes)
            result["completed_stages"] += int(ok)
            if not ok:
                result["issues"].append(f"{stage}: {reason}")
        if job["kind"] == "transfer":
            marker = read_json(root / "transfer_complete.json")
            if (marker.get("status") != "completed" or marker.get("benchmark") != job["benchmark"] or
                    marker.get("source_run") != job["source_run"] or marker.get("student_round") != 5 or
                    marker.get("samples_per_task") != 16 or marker.get("task_count") != job["task_count"] or
                    marker.get("training_on_target") is not False or
                    marker.get("calibration_on_target") is not False or
                    set(marker.get("results", {}).get("completed", [])) != set(stages)):
                raise ValueError("Transfer completion marker differs from the planned job")
            if job["benchmark"] == "humanevalplus" and marker.get("evaluation_protocol") != "official_evalplus_base_and_plus":
                raise ValueError("HumanEval+ completion lacks the official EvalPlus protocol")
        else:
            run_state = read_json(root / "run_status.json")
            if (run_state.get("status") != "completed" or run_state.get("verification") != "completed" or
                    run_state.get("rounds") != job["rounds"] or run_state.get("methods") != job["methods"]):
                raise ValueError("Native run status is incomplete or differs from the planned job")
    except (OSError, ValueError, TypeError, KeyError) as error:
        result["issues"].append(str(error))
    if not result["issues"] and result["completed_stages"] == len(stages):
        result["status"] = "completed"
    return result


@contextmanager
def job_lock(root, job_id):
    """A lock lives outside native output directories, which must start empty."""
    path = contained(root / "locks" / f"{job_id}.lock", root)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import fcntl
    except ImportError as error:
        raise RuntimeError("Safe execution requires fcntl job locking; use a supported Unix platform") from error
    with path.open("a+", encoding="utf-8") as stream:
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError(f"Job is already locked by another runner: {job_id}") from error
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def execute(command):
    if not command or command[0] != "python":
        raise ValueError("Expected a frozen Python command")
    subprocess.run([sys.executable, *command[1:]], check=True, cwd=REPO)


def report(args):
    manifest = load_manifest(args.manifest)
    with job_lock(Path(manifest["run_root"]), "paper-report"):
        execute(["python", "scripts/report_final_study.py", "--manifest", str(resolved(args.manifest))])
    return 0


def run(args):
    manifest = load_manifest(args.manifest)
    if not args.block and not args.job:
        raise ValueError("Select --block core|diagnostic|transfer|all or --job JOB_ID explicitly")
    jobs = manifest["jobs"]
    selected = [job for job in jobs if (not args.job or job["job_id"] == args.job) and
                (not args.block or args.block == "all" or job["block"] == args.block)]
    if not selected:
        raise ValueError("No planned job matches the requested --job/--block selection")
    by_id = {job["job_id"]: job for job in jobs}
    verified_dependencies = set()
    verify_plan_inputs(manifest)
    for job in selected:
        with job_lock(Path(manifest["run_root"]), job["job_id"]):
            # Repeat between jobs so edits made during an earlier job fail closed.
            verify_plan_inputs(manifest)
            for dependency in job["depends_on"]:
                source = by_id[dependency]
                state = job_status(source)
                if state["status"] != "completed":
                    raise ValueError(f"{job['job_id']} requires completed dependency {dependency}: {state['issues']}")
                if dependency not in verified_dependencies:
                    # Transfer consumes the base and round-5 students only. Earlier
                    # rounds remain required complete, but need not reread their
                    # multi-gigabyte weights for this evaluation-only dependency.
                    for stage in ["base", *(f"{method}/round_5" for method in source["methods"])]:
                        ok, reason = verify_marker(Path(source["output_dir"]) / stage,
                            base=stage == "base", verify_hashes=True)
                        if not ok:
                            raise ValueError(f"Dependency integrity failure: {dependency}/{stage}: {reason}")
                verified_dependencies.add(dependency)
            preflight(job)
            print("Running/resuming " + job["job_id"], flush=True)
            execute(job["command"])
            state = job_status(job)
            if state["status"] != "completed":
                raise RuntimeError(f"Job exited without valid completion: {job['job_id']}: {state['issues']}")
            if job["after"]:
                execute(job["after"])
    # The combined report performs task bootstraps. Build it once for the full
    # sequential suite; independent GPU jobs must not race to rewrite it.
    if args.block == "all" and not args.job:
        report(args)
    else:
        print("Selection complete. Build the combined CPU report when ready:\n  "
              "python scripts/run_final_study.py report --manifest " + shlex.quote(str(resolved(args.manifest))))
    return 0


def status(args):
    manifest = load_manifest(args.manifest)
    print(json.dumps([job_status(job) for job in manifest["jobs"]], indent=2))
    return 0


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="Freeze the finite suite from prepared snapshots; no GPU/downloads")
    plan.add_argument("--run-root", default="runs/final_study_v1")
    plan.add_argument("--profile", choices=("24gb", "80gb"), default="24gb")
    plan.add_argument("--backend", choices=("docker", "local"), default="docker")
    plan.add_argument("--allow-unsafe-local", action="store_true")
    plan.add_argument("--workers", type=int, default=4)
    plan.add_argument("--data-root", default="data/mbpp")
    plan.add_argument("--benchmark-root", default="data/iclr2027")
    execute_parser = commands.add_parser("run", help="Run/resume an explicitly selected block or job sequentially")
    execute_parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    execute_parser.add_argument("--block", choices=("core", "diagnostic", "transfer", "all"))
    execute_parser.add_argument("--job")
    for name, help_text in (("status", "Inspect completion metadata and artifact existence without loading models"),
                            ("report", "Rebuild the combined CPU report from stored artifacts")):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--manifest", default=DEFAULT_MANIFEST)
    return root


def main():
    args = parser().parse_args()
    os.chdir(REPO)
    try:
        return {"plan": build_plan, "run": run, "status": status, "report": report}[args.command](args)
    except (OSError, ValueError, KeyError, TypeError, ImportError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
