#!/usr/bin/env python3
"""Prepare the five pinned coding benchmarks; never train or execute programs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from improving.benchmarks import BENCHMARKS, prepare_benchmark
from improving.utils import atomic_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datasets", nargs="+", choices=BENCHMARKS, default=list(BENCHMARKS))
    parser.add_argument("--output-dir", type=Path, default=Path("data/iclr2027"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--calibration-size", type=int, default=50)
    parser.add_argument("--validation-size", type=int, default=30)
    parser.add_argument("--limit", type=int, default=200,
                        help="Seeded task limit for APPS, CodeContests and LiveCodeBench; 0 means all")
    parser.add_argument("--lcb-release", default="release_v5", choices=[f"release_v{i}" for i in range(1, 7)])
    parser.add_argument("--revisions", type=Path,
                        help="JSON object mapping dataset names to pinned HF commits (HumanEval+ uses v0.1.10)")
    parser.add_argument("--exclude-training", type=Path, nargs="*", default=[],
                        help="Additional train/calibration/validation JSONL files checked for exact prompt overlap")
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("--limit must be zero (all tasks) or positive")
    if len(args.datasets) != len(set(args.datasets)):
        parser.error("--datasets contains a duplicate")
    revisions = json.loads(args.revisions.read_text()) if args.revisions else {}
    if not isinstance(revisions, dict) or set(revisions) - set(BENCHMARKS):
        parser.error("--revisions must be an object with benchmark-name keys")
    registry_path = args.output_dir / "benchmark_registry.json"
    registry = json.loads(registry_path.read_text()) if registry_path.is_file() else {
        "protocol": "spectrum-five-benchmarks-v1", "training_dataset": "mbpp", "benchmarks": {}}
    # MBPP first means its training pools are available to decontaminate every
    # transfer target independently of the order passed at the command line.
    order = sorted(args.datasets, key=lambda name: (name != "mbpp", BENCHMARKS.index(name)))
    for name in order:
        exclusions = list(args.exclude_training)
        if name != "mbpp":
            for split in ("train", "calibration", "validation"):
                path = args.output_dir / "mbpp" / f"{split}.jsonl"
                if path.is_file():
                    exclusions.append(path)
            if not exclusions:
                parser.error("Prepare MBPP first or provide --exclude-training; transfer must check training overlap")
        manifest = prepare_benchmark(name, args.output_dir / name, revision=revisions.get(name),
            seed=args.seed, calibration_size=args.calibration_size, validation_size=args.validation_size,
            limit=None if name in {"mbpp", "humanevalplus"} or args.limit == 0 else args.limit,
            lcb_release=args.lcb_release, exclusions_from=exclusions)
        registry["benchmarks"][name] = {"directory": str((args.output_dir / name).resolve()),
            "tasks": str((args.output_dir / name / "eval.jsonl").resolve()),
            "manifest": str((args.output_dir / name / "manifest.json").resolve()),
            "task_count": manifest["output_files"]["eval.jsonl"]["count"],
            "evaluation_backend": manifest["evaluation_backend"],
            "evaluation_protocols": manifest["evaluation_protocols"],
            "revision": manifest["revision"], "request_sha256": manifest["request_sha256"]}
        atomic_json(registry_path, registry)
        print(json.dumps({"benchmark": name, **registry["benchmarks"][name]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
