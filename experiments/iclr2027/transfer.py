#!/usr/bin/env python3
"""Frozen MBPP-student evaluation on the four prepared transfer benchmarks."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
BENCHMARKS = ("humanevalplus", "apps_intro", "codecontests", "livecodebench")


def verify_prepared_benchmark(directory, benchmark):
    """Reject edited or incomplete prepared snapshots before loading any model."""
    directory = Path(directory).resolve()
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest.get("name") != benchmark:
        raise ValueError("Prepared benchmark manifest names a different dataset")
    outputs = manifest.get("output_files", {})
    if not isinstance(outputs, dict) or "eval.jsonl" not in outputs:
        raise ValueError("Prepared benchmark manifest omits its evaluation snapshot")
    for filename, expected in outputs.items():
        path = (directory / filename).resolve()
        if not path.is_relative_to(directory) or not path.is_file():
            raise ValueError(f"Prepared benchmark file is missing or outside its directory: {filename}")
        checksum = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                checksum.update(chunk)
        if checksum.hexdigest() != expected.get("sha256"):
            raise ValueError(f"Prepared benchmark changed after preparation: {path}")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--benchmark", choices=BENCHMARKS, required=True)
    parser.add_argument("--benchmark-root", default="data/iclr2027")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--round", type=int, default=5)
    parser.add_argument("--methods", help="Comma-separated source method keys; default all")
    parser.add_argument("--samples", type=int, default=64)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--max-prompt-tokens", type=int, default=4096)
    parser.add_argument("--max-new-tokens", type=int, default=1024)
    parser.add_argument("--sequence-batch-size", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--memory-mb", type=int, default=1024)
    parser.add_argument("--evalplus-image", default="improving-evalplus:0.3.1")
    parser.add_argument("--backend", choices=["docker", "local"])
    parser.add_argument("--allow-unsafe-local", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    os.chdir(REPO)
    try:
        if min(args.round, args.samples, args.bootstrap_samples, args.max_prompt_tokens,
               args.max_new_tokens, args.sequence_batch_size, args.memory_mb) < 1 or args.timeout <= 0:
            raise ValueError("Round, sampling and generation limits must be positive")
        from improving.data import assert_disjoint_splits, read_jsonl
        from improving.longitudinal import evaluate_checkpoints, export_longitudinal
        from improving.utils import atomic_json

        root = Path(args.run_dir)
        source = json.loads((root / "manifest.json").read_text())
        config = source["config"]
        task_path = Path(args.benchmark_root) / args.benchmark / "eval.jsonl"
        if not task_path.is_file():
            raise FileNotFoundError(f"Prepare {args.benchmark} first: {task_path}")
        prepared = verify_prepared_benchmark(task_path.parent, args.benchmark)
        tasks = read_jsonl(task_path)
        if len(tasks) != prepared["output_files"]["eval.jsonl"]["count"]:
            raise ValueError("Prepared task count differs from its manifest")
        # Check against the actual immutable training/calibration/validation snapshots.
        splits = {name: read_jsonl(root / "tasks" / f"{name}.jsonl")
                  for name in ("train", "calibration", "validation")}
        splits["eval"] = tasks
        assert_disjoint_splits(splits)
        evaluation = dict(config.get("evaluation", {}))
        evaluation.update(timeout=args.timeout, memory_mb=args.memory_mb)
        if args.backend:
            if args.backend == "local" and not args.allow_unsafe_local:
                raise ValueError("Explicit local execution requires --allow-unsafe-local")
            evaluation.update(backend=args.backend, allow_unsafe_local=args.allow_unsafe_local)
        callback, identity = None, None
        if args.benchmark == "humanevalplus":
            from improving.benchmarks import make_humanevalplus_evaluator
            settings = {"backend": evaluation.get("backend", "docker"),
                        "allow_unsafe_local": evaluation.get("allow_unsafe_local", False),
                        "image": args.evalplus_image,
                        "parallel": min(4, evaluation.get("workers", 4))}
            callback, identity = make_humanevalplus_evaluator(task_path, settings=settings)
        elif any(task.get("evaluation_backend") == "evalplus" for task in tasks):
            raise ValueError("An EvalPlus task cannot be evaluated with native tests")
        methods = args.methods.split(",") if args.methods else None
        # Larger problem statements and implementations use one fixed transfer protocol.
        # This is not the 512-token MBPP evaluation setting; all transfer arms share it.
        generation = {"max_prompt_tokens": args.max_prompt_tokens,
                      "max_new_tokens": args.max_new_tokens,
                      "batch_size": args.sequence_batch_size,
                      "sequence_batch_size": args.sequence_batch_size,
                      "task_batch_size": args.sequence_batch_size}
        result = evaluate_checkpoints(root, args.output_dir, samples=args.samples,
            rounds=[args.round], methods=methods, eval_tasks_path=task_path,
            evaluation_overrides=evaluation, generation_overrides=generation,
            bootstrap_samples=args.bootstrap_samples, resume=args.resume,
            evaluator=callback, evaluator_identity=identity)
        if result["status"] != "completed":
            print(json.dumps(result, indent=2))
            return 2
        export_longitudinal(args.output_dir, bootstrap_samples=args.bootstrap_samples)
        atomic_json(Path(args.output_dir) / "transfer_complete.json", {
            "status": "completed", "benchmark": args.benchmark,
            "source_run": str(root.resolve()), "student_round": args.round,
            "task_count": len(tasks), "samples_per_task": args.samples,
            "training_on_target": False, "calibration_on_target": False,
            "generation": generation, "results": result,
            "evaluation_protocol": "official_evalplus_base_and_plus" if callback else
                "recorded_function_or_stdin_adapter_with_benchmark_tests"})
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, FileNotFoundError, ImportError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
