"""Frozen MBPP-checkpoint transfer to the complete official HumanEval+ set.

Generation runs natively; candidate/reference execution is exclusively delegated
to the bounded, offline EvalPlus wrapper. No held-out reference is used to train,
calibrate, select checkpoints, or select samples.
"""
from __future__ import annotations

from collections import Counter
import gc
import json
import os
from pathlib import Path
import subprocess

from .data import read_jsonl, validate_tasks, write_jsonl, prompt_fingerprint
from .generation import generate_to_file
from .metrics import summarize_records
from .modeling import load_model
from .pipeline import checkpoint_fingerprint, file_sha
from .utils import atomic_json, stable_hash
from .verification import export_evalplus, import_evalplus_results


DATASET = "HumanEvalPlus"
VERSION = "v0.1.10"
TASK_COUNT = 164
METHODS = ("plain", "ssd", "spd_hard", "spectral_soft")
REPO = Path(__file__).resolve().parents[2]
WRAPPER = REPO / "scripts" / "evalplus_docker.sh"


def _json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _image_identity(image):
    result = subprocess.run(["docker", "image", "inspect", image, "--format", "{{.Id}}"],
                            check=True, capture_output=True, text=True)
    identity = result.stdout.strip()
    if not identity.startswith("sha256:"):
        raise ValueError("EvalPlus image has no immutable local image ID")
    return identity


def _wrapper(mode, output, settings, samples=None):
    """Never execute generated Python on the host and never pull/build images."""
    command = ["bash", str(WRAPPER), mode, "humaneval"]
    if samples is not None:
        command.append(str(Path(samples).resolve()))
    command.append(str(Path(output).resolve()))
    environment = dict(os.environ)
    # Explicit defaults keep inherited shell settings from silently changing
    # timing/resource settings between arms. The wrapper forwards only its
    # allowlisted settings to the execution container.
    values = {"IMAGE": settings["image_identity"], "PARALLEL": settings.get("parallel", 2),
              "CPUS": settings.get("cpus", 2), "MEMORY_MB": settings.get("memory_mb", 4096),
              "PIDS": settings.get("pids", 256), "WALLTIME": settings.get("walltime", 7200),
              "SAMPLE_MB": settings.get("sample_memory_mb", 2048)}
    environment.update({"IMPROVING_EVALPLUS_" + name: str(value) for name, value in values.items()})
    subprocess.run(command, check=True, env=environment)


def _attempt(directory):
    """Allocate a fresh output; interrupted/failed attempts remain untouched."""
    directory.mkdir(parents=True, exist_ok=True)
    index = 1
    while (directory / f"attempt_{index:04d}").exists():
        index += 1
    output = directory / f"attempt_{index:04d}"
    output.mkdir()
    return output


def _validate_dataset(tasks, metadata):
    validate_tasks(tasks)
    release = metadata.get("datasets", {}).get(DATASET, {})
    if (metadata.get("evalplus_version") != "0.3.1" or release.get("version") != VERSION
            or release.get("task_count") != TASK_COUNT or len(tasks) != TASK_COUNT
            or not isinstance(release.get("sha256"), str) or len(release["sha256"]) != 64):
        raise ValueError("Require the complete pinned official HumanEval+ v0.1.10 snapshot (164 tasks)")
    if {task["task_id"] for task in tasks} != {f"HumanEval/{i}" for i in range(TASK_COUNT)}:
        raise ValueError("HumanEval+ task IDs do not exactly cover the official dataset")
    for task in tasks:
        if (task.get("source") != "evalplus/HumanEvalPlus" or task.get("split") != "eval"
                or task.get("revision") != VERSION or task.get("dataset_sha256") != release["sha256"]
                or task.get("completion_mode") != "continuation"
                or task.get("code_prefix") != task["prompt"]
                or task.get("prompt_protocol") != "evalplus-original-0.3.1"):
            raise ValueError(f"Unexpected HumanEval+ task provenance/interface: {task['task_id']}")
    return release


def _tasks(settings, root):
    path = Path(settings.get("tasks", "data/humanevalplus/tasks.jsonl"))
    metadata_path = path.parent / "dataset_metadata.json"
    if not path.exists():
        output = _attempt(root / "task_prepare")
        _wrapper("prepare", output, settings)
        tasks, metadata = read_jsonl(output / "tasks.jsonl"), _json(output / "dataset_metadata.json")
        _validate_dataset(tasks, metadata)
        if metadata_path.exists() and _json(metadata_path) != metadata:
            raise ValueError("Existing dataset metadata differs from the prepared official snapshot")
        atomic_json(metadata_path, metadata)
        write_jsonl(path, tasks)
    if not metadata_path.exists():
        raise ValueError("HumanEval+ tasks require adjacent dataset_metadata.json from the isolated prepare command")
    tasks, metadata = read_jsonl(path), _json(metadata_path)
    release = _validate_dataset(tasks, metadata)
    return tasks, {"tasks_sha256": file_sha(path), "metadata_sha256": file_sha(metadata_path),
                   "release": release, "tasks_path": str(path.resolve())}


def _nonoverlap(tasks, jobs):
    heldout_ids = {task["task_id"] for task in tasks}
    heldout_prompts = {prompt_fingerprint(task[key]) for task in tasks
                       for key in ("prompt", "original_prompt") if key in task}
    inputs = {}
    for job in jobs:
        # Check complete source files, including questions excluded by data_limits.
        for name in ("train", "calibration", "validation"):
            path = Path(job["config"]["data"][name])
            for task in read_jsonl(path):
                if (task["task_id"] in heldout_ids or any(prompt_fingerprint(task[key]) in heldout_prompts
                        for key in ("prompt", "original_prompt") if key in task)):
                    raise ValueError(f"HumanEval+ overlaps source {name}: {task['task_id']}")
            inputs[str(path.resolve())] = file_sha(path)
    return inputs


def _source_trials(jobs, requested):
    trials = {}
    for job in jobs:
        config, seed = job["config"], int(job["seed"])
        directory = Path(config["output_dir"])
        manifest_path, base_marker = directory / "manifest.json", directory / "base/complete.json"
        if not manifest_path.exists() or not base_marker.exists():
            raise ValueError(f"Source run is not initialized/base-complete: {directory}")
        manifest, base = _json(manifest_path), _json(base_marker)
        if stable_hash(manifest.get("config")) != stable_hash(config) or int(config.get("seed", 42)) != seed:
            raise ValueError("Source job config/seed differs from its saved experiment manifest")
        base_samples = directory / "base/evaluation.jsonl"
        if not base_samples.exists() or file_sha(base_samples) != base.get("evaluation_sha"):
            raise ValueError("Source base evaluation integrity failure")
        model_settings = dict(config["model"])
        local = Path(model_settings["name"])
        local_fingerprint = checkpoint_fingerprint(local) if local.is_dir() else None
        if local_fingerprint != manifest.get("local_base_fingerprint"):
            raise ValueError("Source local base model integrity failure")
        revision = base.get("resolved_revision")
        if not local.is_dir() and not revision:
            raise ValueError("Source remote base has no resolved immutable revision")
        expected_base = stable_hash([config["model"], revision, local_fingerprint])
        if expected_base != base.get("model_identity"):
            raise ValueError("Source base model identity mismatch")
        if revision:
            model_settings["revision"] = revision
        base_trial = {"seed": seed, "method": "base", "round": 0, "checkpoint": None,
                      "model": model_settings, "model_identity": expected_base,
                      "source_marker_sha256": file_sha(base_marker),
                      "source_manifest_sha256": file_sha(manifest_path)}
        key = (seed, "base")
        if key in trials and (trials[key]["model_identity"] != expected_base or trials[key]["model"] != model_settings):
            raise ValueError("Multiple incompatible base models for one transfer seed")
        trials.setdefault(key, base_trial)
        for method in requested:
            if method not in config["methods"]:
                continue
            folder = directory / method / "round_1"
            marker, checkpoint = folder / "complete.json", folder / "model"
            if not marker.exists():
                raise ValueError(f"Transfer requires completed source round 1: {folder}")
            state = _json(marker)
            if state.get("status") != "completed" or not state.get("files"):
                raise ValueError(f"Invalid source completion marker: {marker}")
            for name, digest in state["files"].items():
                asset = folder / name
                if not asset.resolve().is_relative_to(folder.resolve()) or not asset.is_file() or file_sha(asset) != digest:
                    raise ValueError(f"Source completed round integrity failure: {asset}")
            fingerprint = checkpoint_fingerprint(checkpoint)
            identity = stable_hash([expected_base, method, 1, fingerprint])
            if state.get("model_identity") != identity:
                raise ValueError(f"Source checkpoint identity mismatch: {checkpoint}")
            trial = {"seed": seed, "method": method, "round": 1, "checkpoint": str(checkpoint.resolve()),
                     "model": model_settings, "model_identity": identity,
                     "checkpoint_fingerprint": fingerprint, "source_marker_sha256": file_sha(marker),
                     "source_manifest_sha256": file_sha(manifest_path)}
            key = (seed, method)
            if key in trials and trials[key] != trial:
                raise ValueError(f"Ambiguous duplicate transfer source: {key}")
            trials[key] = trial
    for seed in {job["seed"] for job in jobs}:
        if any((int(seed), method) not in trials for method in requested):
            raise ValueError(f"Missing requested completed transfer method for seed {seed}")
    return [trials[key] for key in sorted(trials)]


def _intact(marker, identity):
    if not marker.exists():
        return False
    state = _json(marker)
    if state.get("identity") != identity or state.get("status") != "completed" or not state.get("files"):
        raise ValueError(f"Completed transfer identity mismatch: {marker}")
    for name, digest in state["files"].items():
        path = marker.parent / name
        if not path.resolve().is_relative_to(marker.parent.resolve()) or not path.is_file() or file_sha(path) != digest:
            raise ValueError(f"Completed transfer output integrity failure: {path}")
    return True


def _evaluate_output(output, samples, dataset, count, sample_count):
    if not (output / "environment.txt").is_file():
        raise ValueError("Official EvalPlus output must retain its evaluation environment")
    metadata = _json(output / "evaluation_metadata.json")
    saved_dataset = _json(output / "dataset_metadata.json")
    payload = _json(output / "samples_eval_results.json")
    if (metadata.get("evalplus_version") != "0.3.1" or metadata.get("dataset") != "humaneval"
            or metadata.get("dataset_release") != dataset["release"]
            or saved_dataset.get("datasets", {}).get(DATASET) != dataset["release"]
            or metadata.get("samples_sha256") != file_sha(samples)
            or metadata.get("task_count") != count or metadata.get("sample_count") != sample_count
            or metadata.get("protocol") != "official-base-and-plus-tests-no-sanitization"
            or not payload.get("hash") or metadata.get("dataset_hash") != payload["hash"]):
        raise ValueError("Official EvalPlus output provenance does not match exported samples/dataset")
    return metadata


def run_transfer(config: dict, source_jobs: list[dict], *, resume=True) -> dict:
    """Evaluate confirmation round-1 checkpoints on every HumanEval+ task.

    ``source_jobs`` are formal-suite pipeline jobs. Only phase ``confirm`` is
    eligible. A changed config, source checkpoint, model revision, dataset,
    implementation, image ID, or previously completed output fails closed.
    """
    settings = dict(config.get("transfer", {}))
    if settings.get("enabled", True) is False:
        return {"status": "disabled", "trials": []}
    requested = settings.get("methods", list(METHODS))
    if not requested or len(set(requested)) != len(requested) or any(method not in METHODS for method in requested):
        raise ValueError("Transfer methods must be unique confirmed main-comparison methods")
    samples = settings.get("samples", 64)
    if type(samples) is not int or samples < 1:
        raise ValueError("transfer.samples must be a positive integer")
    bootstrap = settings.get("bootstrap_samples", 2000)
    if type(bootstrap) is not int or bootstrap < 1:
        raise ValueError("transfer.bootstrap_samples must be a positive integer")
    if config.get("evaluation", {}).get("code_extraction", "first_fence") not in {"first_fence", "strict"}:
        raise ValueError("Unsupported transfer code extraction protocol")
    jobs = [job for job in source_jobs if job.get("phase") == "confirm"]
    if not jobs:
        raise ValueError("HumanEval+ transfer requires completed confirmation jobs")
    settings["image_identity"] = _image_identity(settings.get("image", "improving-evalplus:0.3.1"))
    sources = _source_trials(jobs, requested)
    root = Path(config["output_dir"]) / "transfer" / "humanevalplus"
    tasks, dataset = _tasks(settings, root)
    training_inputs = _nonoverlap(tasks, jobs)
    implementation = {path.name: file_sha(path) for path in Path(__file__).parent.glob("*.py")}
    implementation["scripts/evalplus_docker.sh"] = file_sha(WRAPPER)
    implementation["docker/EvalPlus.Dockerfile"] = file_sha(REPO / "docker/EvalPlus.Dockerfile")
    identity = stable_hash({"config": config, "settings": settings, "sources": sources,
                            "dataset": dataset, "training_inputs": training_inputs,
                            "implementation": implementation})
    manifest_path = root / "manifest.json"
    if manifest_path.exists():
        if not resume:
            raise FileExistsError("Transfer exists; use resume or a new suite output directory")
        if _json(manifest_path).get("identity") != identity:
            raise ValueError("Transfer configuration/source/data/implementation/image changed; use a new output directory")
    else:
        if any((root / f"seed_{trial['seed']}").exists() for trial in sources):
            raise ValueError("Transfer outputs exist without a matching manifest")
        atomic_json(manifest_path, {"identity": identity, "config": config, "settings": settings,
                    "sources": sources, "dataset": dataset, "training_inputs": training_inputs,
                    "implementation": implementation, "protocol": "native-frozen-mbpp-round1-to-full-humanevalplus-v1"})
    generation = {key: value for key, value in config.get("generation", {}).items()
                  if key not in {"train_samples", "eval_samples"}}
    generation["samples"] = samples
    evaluation = config.get("evaluation", {})
    code_extraction = evaluation.get("code_extraction", "first_fence")
    output_trials = []
    for source in sources:
        folder = root / f"seed_{source['seed']}" / source["method"]
        marker = folder / "complete.json"
        trial_identity = stable_hash([identity, source, generation, code_extraction])
        raw, exported = folder / "raw.jsonl", folder / "evalplus_samples.jsonl"
        verified_path, metrics_path = folder / "verified.jsonl", folder / "metrics.json"
        if not _intact(marker, trial_identity):
            model, tokenizer = load_model(source["model"], source["checkpoint"])
            try:
                if (source["checkpoint"] is None and not Path(source["model"]["name"]).is_dir()
                        and getattr(model.config, "_commit_hash", None) != source["model"]["revision"]):
                    raise ValueError("Loaded transfer base differs from its source resolved revision")
                records = generate_to_file(model, tokenizer, tasks, raw, generation,
                    seed=source["seed"], model_identity=source["model_identity"], method=source["method"],
                    round_index=source["round"], stage="humanevalplus_transfer", resume=resume)
            finally:
                del model, tokenizer
                gc.collect()
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            counts = Counter(row["task_id"] for row in records)
            if counts != Counter({task["task_id"]: samples for task in tasks}):
                raise ValueError("Transfer generation must preserve the entire task/sample universe")
            export_manifest = export_evalplus(tasks, records, exported, code_extraction=code_extraction)
            output = _attempt(folder / "official")
            try:
                _wrapper("evaluate", output, settings, exported)
                official = _evaluate_output(output, exported, dataset, len(tasks), len(records))
                verified = import_evalplus_results(records, output / "samples_eval_results.json",
                                                    tasks=tasks, require_plus=True, manifest_path=export_manifest)
                write_jsonl(verified_path, verified)
                summary = summarize_records(verified, ks=evaluation.get("ks", [1, 8, 32, 64]),
                    correct_budget=evaluation.get("correct_budget", 4),
                    correct_budgets=evaluation.get("correct_budgets", [2, 4, 8, 16]),
                    bootstrap_samples=settings.get("bootstrap_samples", 2000), seed=source["seed"],
                    expected_samples={task["task_id"]: samples for task in tasks})
                summary["evaluation"] = {**official, "image_identity": settings["image_identity"],
                                          "code_extraction": code_extraction}
                atomic_json(metrics_path, summary)
            except BaseException as error:
                atomic_json(folder / f"{output.name}.failed.json", {"status": "failed", "type": type(error).__name__,
                            "message": str(error), "output": str(output.resolve())})
                raise
            # Seal raw bytes, all generation chunks, exported mapping and the
            # successful official output. Failed attempt contents remain evidence.
            files = [raw, raw.with_suffix(".jsonl.budget.json"), exported, export_manifest,
                     verified_path, metrics_path, *raw.with_suffix(".jsonl.parts").rglob("*"), *output.rglob("*")]
            atomic_json(marker, {"status": "completed", "identity": trial_identity,
                        "files": {str(path.relative_to(folder)): file_sha(path) for path in files if path.is_file()},
                        "official_output": str(output.relative_to(folder))})
        output_trials.append({"seed": source["seed"], "method": source["method"], "round": source["round"],
                              "metrics_path": str(metrics_path.resolve()), "verified_path": str(verified_path.resolve()),
                              "raw_path": str(raw.resolve()), "complete_path": str(marker.resolve())})
    result = {"status": "completed", "identity": identity, "dataset": dataset, "trials": output_trials,
              "protocol": "native-frozen-mbpp-round1-to-full-humanevalplus-v1", "task_count": len(tasks),
              "samples_per_task": samples, "training_on_humanevalplus": False}
    atomic_json(root / "results.json", result)
    return result
