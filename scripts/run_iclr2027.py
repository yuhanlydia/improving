#!/usr/bin/env python3
"""Plan and run the SPECTRUM ICLR experiments; planning uses only Python stdlib.

No command runs a grid implicitly. `plan` writes immutable configurations,
`run --manifest ... --job ...` runs explicitly selected entries and resumes them.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys


REPO = Path(__file__).resolve().parents[1]
MODELS = {
    "qwen1.5b": "Qwen/Qwen2.5-Coder-1.5B-Instruct",
    "qwen3b": "Qwen/Qwen2.5-Coder-3B-Instruct",
    "qwen7b": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "deepseek6.7b": "deepseek-ai/deepseek-coder-6.7b-instruct",
}
LABELS = {"plain": "Plain self-distillation", "ssd": "SSD",
          "spectral_soft": "SPECTRUM", "spd_hard": "Projection design ablation",
          "random_soft": "Random eigenbasis", "isotropic_soft": "Isotropic gain",
          "matched_blend": "Matched residual blend"}
BENCHMARKS = ["humanevalplus", "apps_intro", "codecontests", "livecodebench"]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def immutable_json(path, value):
    path = Path(path)
    if path.exists():
        if json.loads(path.read_text()) != value:
            raise ValueError(f"Refusing to overwrite a different plan/configuration: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    temporary.replace(path)


def csv_ints(value):
    result = [int(x) for x in value.split(",")]
    if not result or len(set(result)) != len(result) or any(x < 0 for x in result):
        raise argparse.ArgumentTypeError("Expected unique nonnegative comma-separated seeds")
    return result


def native_config(args, model_key, seed):
    # BF16 dense parameters are required by covariance extraction and weight folding.
    # These are conservative memory targets, not measured peak-memory guarantees.
    batches = ({"qwen1.5b": 8, "qwen3b": 4, "qwen7b": 1, "deepseek6.7b": 1}
               if args.profile == "24gb" else
               {"qwen1.5b": 32, "qwen3b": 16, "qwen7b": 8, "deepseek6.7b": 8})
    batch = batches[model_key]
    return {
        "seed": seed, "data_seed": 42,
        "model": {"name": MODELS[model_key], "device": "auto", "dtype": "bfloat16",
                  "attn_implementation": "sdpa"},
        "data": {split: str(Path(args.data_root) / f"{split}.jsonl")
                 for split in ("train", "calibration", "validation", "eval")},
        "data_limits": {}, "rounds": 5, "checkpoint_retention": "all",
        "methods": ["plain", "ssd", "spectral_soft"],
        "generation": {"train_samples": 16, "eval_samples": 64, "batch_size": batch,
                       "sequence_batch_size": batch, "task_batch_size": batch,
                       "max_new_tokens": 512, "max_prompt_tokens": 1024,
                       "temperature": 0.8, "top_p": 0.95, "top_k": 0},
        "calibration": {"max_examples": 50, "max_length": 1536, "span_mode": "completion",
                        "layers": None, "rank_fraction": 0.5, "tau": 1.0, "rho": 0.5,
                        "reestimate_each_round": True},
        "train": {"epochs": 1, "batch_size": 1, "gradient_accumulation_steps": 16,
                  "max_length": 1536, "learning_rate": 1e-5, "weight_decay": 0.01,
                  "warmup_ratio": 0.03, "max_grad_norm": 1.0, "lora_rank": 8,
                  "lora_alpha": 8, "lora_dropout": 0.05,
                  "gradient_checkpointing": True, "loss_scope": "all"},
        "evaluation": {"backend": args.backend, "allow_unsafe_local": args.allow_unsafe_local,
                       "docker_image": "python:3.11-slim", "code_extraction": "first_fence",
                       "workers": args.workers, "timeout": 5,
                       "ks": [1, 4, 8, 16, 32, 64], "correct_budget": 4,
                       "correct_budgets": [4, 8, 16], "correctness_margin": 0.01,
                       "bootstrap_samples": 2000},
        "diagnostics": {"evaluate_generation_policy": False,
                        "eval_task_limit": 128, "eval_samples": 16},
    }


def training_job(args, stage, name, config, question):
    identity = digest(config)[:10]
    job_id = f"{stage}-{name}-{args.profile}-{identity}"
    config["output_dir"] = str(Path(args.run_root) / job_id)
    path = Path(args.output_dir) / "configs" / (job_id + ".json")
    immutable_json(path, config)  # JSON is valid YAML for the existing pipeline.
    return {"job_id": job_id, "kind": "training", "stage": stage,
            "question": question, "model": config["model"]["name"], "seed": config["seed"],
            "methods": config["methods"], "method_labels": [LABELS[x] for x in config["methods"]],
            "config": str(path), "config_sha256": digest(config),
            "output_dir": config["output_dir"], "planned_rounds": 5,
            "training_samples_per_task": 16, "evaluation_samples_per_task": 64,
            "command": [sys.executable, "-m", "improving", "run", "--config", str(path), "--resume"],
            "after": [sys.executable, "scripts/export_longitudinal.py", "export", "--run-dir",
                      config["output_dir"], "--bootstrap-samples", "2000"]}


def build_plan(args):
    if args.backend == "local" and not args.allow_unsafe_local:
        raise ValueError("Local candidate execution requires --allow-unsafe-local; Docker is the default")
    jobs = []
    if args.stage == "core":
        for seed in args.seeds:
            config = native_config(args, "qwen1.5b", seed)
            jobs.append(training_job(args, "core", f"qwen1.5b-s{seed}", config,
                "Five-round trajectories and final correct-implementation diversity"))
    elif args.stage == "mechanism":
        for seed in args.seeds:
            config = native_config(args, "qwen1.5b", seed)
            config["methods"] = ["spectral_soft", "spd_hard", "random_soft", "isotropic_soft"]
            if args.include_matched_blend:
                config["methods"].append("matched_blend")
            jobs.append(training_job(args, "mechanism", f"geometry-s{seed}", config,
                "Learned geometry, directional modulation, and projection design ablation"))
            fixed = native_config(args, "qwen1.5b", seed)
            fixed["methods"] = ["spectral_soft"]
            fixed["calibration"]["reestimate_each_round"] = False
            jobs.append(training_job(args, "mechanism", f"fixed-geometry-s{seed}", fixed,
                "Re-estimating geometry each round versus retaining first-round geometry"))
            # Tau=1 is already the spectral_soft arm of the geometry job.
            for tau in (0.25, 0.5, 2.0, 4.0):
                varied = native_config(args, "qwen1.5b", seed)
                varied["methods"] = ["spectral_soft"]
                varied["calibration"]["tau"] = tau
                jobs.append(training_job(args, "mechanism", f"tau{tau:g}-s{seed}", varied,
                    "Modulation-strength sensitivity; report all strengths without test-set selection"))
    elif args.stage == "scale":
        models = args.models.split(",") if args.models else ["qwen3b", "qwen7b", "deepseek6.7b"]
        for model in models:
            if model not in MODELS:
                raise ValueError(f"Unknown model alias: {model}")
            for seed in args.seeds:
                jobs.append(training_job(args, "scale", f"{model}-s{seed}",
                    native_config(args, model, seed),
                    "Model-size and architecture replication on the same MBPP protocol"))
    elif args.stage == "transfer":
        if not args.source_run:
            raise ValueError("Transfer planning requires --source-run pointing to a completed MBPP run")
        source = str(Path(args.source_run))
        for benchmark in (args.benchmarks.split(",") if args.benchmarks else BENCHMARKS):
            if benchmark not in BENCHMARKS:
                raise ValueError(f"Unknown transfer benchmark: {benchmark}")
            job_id = "transfer-" + benchmark + "-" + digest({"source": source,
                "benchmark": benchmark, "round": args.transfer_round,
                "benchmark_root": args.benchmark_root, "samples": 64,
                "backend": args.backend, "allow_unsafe_local": args.allow_unsafe_local})[:10]
            output = str(Path(args.run_root) / job_id)
            command = [sys.executable, "experiments/iclr2027/transfer.py", "--run-dir", source,
                       "--benchmark", benchmark, "--benchmark-root", args.benchmark_root,
                       "--output-dir", output, "--round", str(args.transfer_round), "--samples", "64",
                       "--bootstrap-samples", "2000", "--backend", args.backend, "--resume"]
            if args.allow_unsafe_local:
                command.append("--allow-unsafe-local")
            jobs.append({"job_id": job_id, "kind": "transfer", "stage": "transfer",
                         "question": "Frozen MBPP-trained student transfer; no target-benchmark training",
                         "source_run": source, "benchmark": benchmark, "output_dir": output,
                         "command": command, "evaluation_samples_per_task": 64})
    value = {"schema_version": 1, "study": "SPECTRUM ICLR 2027", "stage": args.stage,
             "protocol": {"training_dataset": "MBPP", "data_seed": 42, "rounds": 5,
                          "task_bootstrap_resamples": 2000,
                          "uncertainty_unit": "evaluation tasks, not training seeds",
                          "model_uncertainty": "Report independent training-seed results separately",
                          "checkpoint_retention": "all", "quantization": "unsupported",
                          "candidate_budgets_matched": True, "token_or_FLOP_budgets_matched": False},
             "jobs": jobs}
    path = Path(args.output_dir) / (f"{args.stage}-" + digest(value)[:10] + ".manifest.json")
    immutable_json(path, value)
    print(f"Manifest: {path}\nJobs: {len(jobs)} (nothing has been executed)")
    for job in jobs:
        print(job["job_id"] + "\n  " + shlex.join(job["command"]))
    print("Run one selected job:\n  " + shlex.join([sys.executable, "scripts/run_iclr2027.py",
        "run", "--manifest", str(path), "--job", jobs[0]["job_id"]]))
    return 0


def preflight(job):
    if job["kind"] != "training":
        return
    config = json.loads(Path(job["config"]).read_text())
    if digest(config) != job["config_sha256"]:
        raise ValueError("Configuration changed since planning; create a new plan")
    missing = [value for value in config["data"].values() if not Path(value).is_file()]
    if missing:
        raise FileNotFoundError("Prepare MBPP first; missing: " + ", ".join(missing))
    packages = [name for name in ("torch", "transformers", "peft", "datasets")
                if importlib.util.find_spec(name) is None]
    if packages:
        raise ImportError("Install project training dependencies: " + ", ".join(packages))
    if config["evaluation"]["backend"] == "docker":
        if shutil.which("docker") is None:
            raise RuntimeError("Docker is not installed; see README for the explicit local alternative")
        subprocess.run(["docker", "info"], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["docker", "image", "inspect", config["evaluation"]["docker_image"]],
                       check=True, stdout=subprocess.DEVNULL)


def selected_jobs(args):
    manifest = json.loads(Path(args.manifest).read_text())
    jobs = manifest["jobs"]
    if not args.all and not args.job:
        raise ValueError("Select --job JOB_ID or explicitly request --all")
    if args.all and args.job:
        raise ValueError("Choose --job or --all")
    if args.job:
        selected = [job for job in jobs if job["job_id"] == args.job]
        if not selected:
            raise ValueError(f"Job is not in this manifest: {args.job}")
        return selected
    return jobs


def run(args):
    for job in selected_jobs(args):
        preflight(job)
        print("Running " + job["job_id"], flush=True)
        subprocess.run(job["command"], check=True, cwd=REPO)
        if job.get("after"):
            subprocess.run(job["after"], check=True, cwd=REPO)
    return 0


def status(args):
    manifest = json.loads(Path(args.manifest).read_text())
    rows = []
    for job in manifest["jobs"]:
        root = Path(job["output_dir"])
        if job["kind"] == "training":
            expected = [root / method / "round_5" / "complete.json" for method in job["methods"]]
            completed = sum(path.exists() for path in expected)
            label = "completed" if completed == len(expected) else "partial" if root.exists() else "pending"
        else:
            label = "completed" if (root / "transfer_complete.json").exists() else "partial" if root.exists() else "pending"
            completed = None
        rows.append({"job_id": job["job_id"], "status": label, "completed_arms": completed,
                     "output_dir": str(root), "unmeasured_value": "x" if label != "completed" else None})
    print(json.dumps(rows, indent=2))
    return 0


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="Write an immutable study manifest; no GPU imports/downloads")
    plan.add_argument("--stage", choices=["core", "mechanism", "transfer", "scale"], default="core")
    plan.add_argument("--seeds", type=csv_ints, default=[43], help="Default 43; confirmation: 42,43,44")
    plan.add_argument("--profile", choices=["24gb", "80gb"], default="24gb")
    plan.add_argument("--backend", choices=["docker", "local"], default="docker")
    plan.add_argument("--allow-unsafe-local", action="store_true")
    plan.add_argument("--workers", type=int, default=4)
    plan.add_argument("--data-root", default="data/mbpp")
    plan.add_argument("--benchmark-root", default="data/iclr2027")
    plan.add_argument("--output-dir", default="runs/iclr2027/plans")
    plan.add_argument("--run-root", default="runs/iclr2027")
    plan.add_argument("--include-matched-blend", action="store_true")
    plan.add_argument("--models", help="Scale aliases: qwen3b,qwen7b,deepseek6.7b")
    plan.add_argument("--source-run", help="Completed MBPP run for frozen transfer")
    plan.add_argument("--benchmarks", help="Comma-separated transfer benchmark keys")
    plan.add_argument("--transfer-round", type=int, default=5)
    execute = commands.add_parser("run", help="Run only explicitly selected manifest entries")
    execute.add_argument("--manifest", required=True)
    execute.add_argument("--job")
    execute.add_argument("--all", action="store_true")
    inspect = commands.add_parser("status", help="Inspect artifact completion without loading models")
    inspect.add_argument("--manifest", required=True)
    return root


def main():
    args = parser().parse_args()
    # Paths in manifests and the existing pipeline always use the repository root.
    import os
    os.chdir(REPO)
    try:
        if args.command == "plan":
            if args.workers < 1 or args.transfer_round < 1:
                raise ValueError("workers and transfer-round must be positive")
            return build_plan(args)
        return run(args) if args.command == "run" else status(args)
    except (ValueError, FileNotFoundError, ImportError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
