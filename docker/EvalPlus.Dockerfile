# syntax=docker/dockerfile:1
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    XDG_CACHE_HOME=/opt/build-cache \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1

# Evaluation-only dependency closure. EvalPlus's declared extras also pull
# generation backends and SDKs; its evaluate.py import tree needs none of them.
# Installing the official wheel without those dependencies avoids torch/CUDA.
RUN python -m pip install --no-cache-dir \
        numpy==1.26.4 datasets==3.5.1 pyarrow==19.0.1 huggingface-hub==0.30.2 \
        tree-sitter==0.22.3 tree-sitter-python==0.21.0 \
        tqdm==4.67.1 termcolor==2.5.0 fire==0.7.0 rich==13.9.4 \
        psutil==6.1.1 appdirs==1.4.4 tempdir==0.7.1 wget==3.2 \
        multipledispatch==1.0.0 \
    && python -m pip install --no-cache-dir --no-deps evalplus==0.3.1

# Download data only. Do not call get_groundtruth/evaluate/trusted_exec here:
# reference and candidate execution belongs in the bounded runtime container.
RUN python - <<'PY'
import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess

import evalplus.evaluate
from evalplus.data import get_human_eval_plus, get_mbpp_plus
from evalplus.data.humaneval import HUMANEVAL_PLUS_VERSION
from evalplus.data.mbpp import MBPP_PLUS_VERSION
from evalplus.data.utils import get_dataset_metadata

assert importlib.util.find_spec("torch") is None, "Evaluation image must not install torch"
destination = pathlib.Path("/opt/evalplus-data")
destination.mkdir(parents=True)
metadata = {"evalplus_version": "0.3.1", "datasets": {}}
for name, version, loader in (
    ("HumanEvalPlus", HUMANEVAL_PLUS_VERSION, get_human_eval_plus),
    ("MbppPlus", MBPP_PLUS_VERSION, get_mbpp_plus),
):
    tasks = loader()
    _, cached_path = get_dataset_metadata(name, version, False, False)
    target = destination / f"{name}-{version}.jsonl"
    shutil.copyfile(cached_path, target)
    metadata["datasets"][name] = {"version": version, "task_count": len(tasks),
        "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
(destination / "dataset_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
(destination / "environment.txt").write_bytes(subprocess.check_output(["python", "-m", "pip", "freeze"]))
shutil.rmtree("/opt/build-cache")
PY

ENV XDG_CACHE_HOME=/tmp/evalplus-cache \
    HUMANEVAL_OVERRIDE_PATH=/opt/evalplus-data/HumanEvalPlus-v0.1.10.jsonl \
    MBPP_OVERRIDE_PATH=/opt/evalplus-data/MbppPlus-v0.2.0.jsonl \
    EVALPLUS_MAX_MEMORY_BYTES=2147483648

COPY <<'PY' /usr/local/bin/improving-evalplus
import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from evalplus.data import get_human_eval_plus, get_mbpp_plus


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prepare", "evaluate"))
    parser.add_argument("dataset", choices=("humaneval", "mbpp"))
    parser.add_argument("--parallel", type=int, default=2)
    parser.add_argument("--min-time-limit", type=float, default=1.0)
    parser.add_argument("--gt-time-limit-factor", type=float, default=4.0)
    args = parser.parse_args()
    if args.parallel < 1 or args.min_time_limit <= 0 or args.gt_time_limit_factor <= 0:
        parser.error("Parallelism and test time limits must be positive")
    tasks = get_human_eval_plus() if args.dataset == "humaneval" else get_mbpp_plus()
    metadata_path = Path("/opt/evalplus-data/dataset_metadata.json")
    metadata = json.loads(metadata_path.read_text())
    dataset_name = "HumanEvalPlus" if args.dataset == "humaneval" else "MbppPlus"
    provenance = metadata["datasets"][dataset_name]
    output = Path("/output")

    if args.mode == "prepare":
        # References are persisted as heldout provenance, never training input.
        # Extended tests are consumed only by EvalPlus, not exposed in prompts.
        with (output / "tasks.jsonl").open("x", encoding="utf-8") as stream:
            for task_id, task in sorted(tasks.items()):
                row = {"task_id": task_id, "prompt": task["prompt"],
                    "reference": task["canonical_solution"], "entry_point": task["entry_point"],
                    "source": f"evalplus/{dataset_name}", "split": "eval",
                    "revision": provenance["version"], "dataset_sha256": provenance["sha256"],
                    "completion_mode": "continuation", "code_prefix": task["prompt"],
                    "prompt_protocol": "evalplus-original-0.3.1", "evaluation_backend": "evalplus"}
                stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
        shutil.copyfile(metadata_path, output / "dataset_metadata.json")
        print(json.dumps({"tasks": len(tasks), "output": "/output/tasks.jsonl"}))
        return

    # Official EvalPlus skips unknown task IDs; preflight prevents that loss.
    source = Path("/input/samples.jsonl")
    groups = defaultdict(list)
    for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict) or not isinstance(row.get("solution"), str):
            raise ValueError(f"Line {line_number}: expected exported task_id and full solution")
        if row.get("task_id") not in tasks:
            raise ValueError(f"Line {line_number}: unknown {args.dataset}+ task_id {row.get('task_id')!r}")
        groups[row["task_id"]].append(row["solution"])
    if set(groups) != set(tasks):
        raise ValueError(f"Incomplete {args.dataset}+ task coverage: {len(groups)} of {len(tasks)} tasks")

    with tempfile.TemporaryDirectory(prefix="evalplus-run-") as directory:
        samples = Path(directory) / "samples.jsonl"
        shutil.copyfile(source, samples)
        command = ["evalplus.evaluate", "--dataset", args.dataset, "--samples", str(samples),
            "--parallel", str(args.parallel), "--min_time_limit", str(args.min_time_limit),
            "--gt_time_limit_factor", str(args.gt_time_limit_factor)]
        subprocess.run(command, check=True)
        result_path = samples.with_name("samples_eval_results.json")
        results = json.loads(result_path.read_text())
        evaluated = results.get("eval", {})
        if set(evaluated) != set(groups):
            raise ValueError("Evaluator omitted or added task IDs")
        for task_id, solutions in groups.items():
            returned = evaluated[task_id]
            if len(returned) != len(solutions) or any(
                row.get("task_id") != task_id or row.get("solution") != expected
                for row, expected in zip(returned, solutions)
            ):
                raise ValueError(f"Evaluator lost or reordered samples for {task_id}")
        shutil.copyfile(result_path, output / "samples_eval_results.json")
    run_metadata = {"evalplus_version": "0.3.1", "dataset": args.dataset,
        "dataset_release": provenance, "dataset_hash": results.get("hash"),
        "samples_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "task_count": len(groups), "sample_count": sum(map(len, groups.values())),
        "parallel": args.parallel, "min_time_limit": args.min_time_limit,
        "gt_time_limit_factor": args.gt_time_limit_factor,
        "max_memory_bytes_per_sample": int(os.environ["EVALPLUS_MAX_MEMORY_BYTES"]),
        "protocol": "official-base-and-plus-tests-no-sanitization"}
    (output / "evaluation_metadata.json").write_text(json.dumps(run_metadata, indent=2) + "\n")
    shutil.copyfile(metadata_path, output / "dataset_metadata.json")
    shutil.copyfile("/opt/evalplus-data/environment.txt", output / "environment.txt")
    print(json.dumps({"results": "/output/samples_eval_results.json", "samples": run_metadata["sample_count"]}))


if __name__ == "__main__":
    main()
PY

RUN chmod -R a=rX /opt/evalplus-data \
    && chmod 0555 /usr/local/bin/improving-evalplus \
    && python -I /usr/local/bin/improving-evalplus --help

USER 65534:65534
WORKDIR /tmp
ENTRYPOINT ["python", "-I", "/usr/local/bin/improving-evalplus"]
