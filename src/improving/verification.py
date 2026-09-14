"""Bounded code checks and a lossless bridge to official EvalPlus 0.3.1.

Docker is the default execution boundary. Local execution requires an explicit
trust flag and is only a resource-limited subprocess, NOT a security sandbox.
No verifier imports or calls EvalPlus's host-executing evaluator.

The EvalPlus bridge exports ``{task_id, solution}`` JSONL plus a manifest. Its
supported results format is the 0.3.1 ``*_eval_results.json`` object with an
``eval`` mapping to per-task lists sorted by input encounter order. That format
omits completion IDs, so exact task counts, solution text, and manifest order
are checked. Unknown/missing tasks, dropped samples, and absent plus results
fail explicitly. Run the external evaluator in a separately managed container;
full MBPP and MBPP+ have different task sets and cannot be silently equated.
"""

from __future__ import annotations

import ast
from collections import Counter
from collections.abc import Iterable, Mapping
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from typing import Any
import uuid

from .data import read_jsonl, validate_completions, validate_tasks, write_jsonl
from .utils import stable_hash


def extract_python_code(completion: str, mode: str = "strict") -> str:
    """Extract Python from a completion according to an explicit protocol.

    ``strict`` removes only a single enclosing Python/py/untagged fence.
    ``first_fence`` takes the first such block even with surrounding prose or a
    missing closing fence. Neither mode repairs the extracted Python.
    """
    if not isinstance(completion, str):
        raise TypeError("completion must be a string")
    if mode not in {"strict", "first_fence"}:
        raise ValueError("code_extraction must be strict or first_fence")
    pattern = r"\s*```(?:python|py)?[ \t]*\r?\n(?P<code>[\s\S]*?)\r?\n```[ \t]*\s*"
    if mode == "first_fence":
        pattern = r"```(?:python|py)?[ \t]*\r?\n(?P<code>[\s\S]*?)(?:\r?\n```|\Z)"
        match = re.search(pattern, completion, flags=re.IGNORECASE)
        return match.group("code").rstrip() + "\n" if match else completion
    match = re.fullmatch(pattern, completion, flags=re.IGNORECASE)
    if match and "```" not in match.group("code"):
        return match.group("code") + "\n"
    return completion


def _solution_code(task: Mapping[str, Any], completion: str, code_extraction: str = "strict") -> str:
    code = extract_python_code(completion, mode=code_extraction)
    if not code.strip():
        return code
    if task.get("completion_mode") == "continuation":
        try:
            complete = any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == task.get("entry_point") for node in ast.parse(code).body)
        except (SyntaxError, ValueError):
            complete = False
        if not complete:
            code = task.get("code_prefix", task["prompt"]) + code
    return code


def _test_code(task: Mapping[str, Any]) -> str:
    tests = task.get("tests")
    if not isinstance(tests, str) or not tests.strip():
        raise ValueError(f"{task['task_id']}: builtin verification requires nonempty tests")
    try:
        defines_check = any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "check" for node in ast.parse(tests).body)
    except SyntaxError as error:
        raise ValueError(f"{task['task_id']}: invalid task tests: {error}") from error
    if task.get("test_mode") == "check" or defines_check:
        if not task.get("entry_point"):
            raise ValueError(f"{task['task_id']}: check tests require entry_point")
        tests += f"\ncheck({task['entry_point']})\n"
    return tests


def _validate_groups(tasks: list[dict[str, Any]], records: Iterable[Mapping[str, Any]], expected_samples: int | None = None) -> list[dict[str, Any]]:
    rows = validate_completions(records, tasks)
    counts = Counter(row["task_id"] for row in rows)
    missing = set(task["task_id"] for task in tasks) - counts.keys()
    if missing:
        raise ValueError(f"Missing completions for task IDs: {sorted(missing)}")
    if expected_samples is not None:
        if type(expected_samples) is not int or expected_samples < 1:
            raise ValueError("expected_samples must be a positive integer")
        wrong = {task_id: count for task_id, count in counts.items() if count != expected_samples}
        if wrong:
            raise ValueError(f"Incomplete expected_samples={expected_samples}: {wrong}")
    return rows


# The wrapper distinguishes candidate syntax, failed assertions, and other
# exceptions. It catches SystemExit and requires a post-check marker, so an
# early os._exit(0) cannot count as passing. This is not an anti-cheating oracle:
# hostile code can inspect a Python evaluator and must not be assumed honest.
_RUNNER = r'''import contextlib
import json
import math
import os
import resource
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    payload = json.load(stream)
resource.setrlimit(resource.RLIMIT_AS, (payload["memory"], payload["memory"]))
cpu = max(1, math.ceil(payload["timeout"]))
resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu + 1))
resource.setrlimit(resource.RLIMIT_FSIZE, (1048576, 1048576))
resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
try:
    candidate = compile(payload["code"], "candidate.py", "exec")
except (SyntaxError, ValueError, TypeError, MemoryError):
    status = "compile_error"
else:
    try:
        namespace = {"__name__": "__main__"}
        with open(os.devnull, "w") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                exec(candidate, namespace)
                exec(compile(payload["tests"], "tests.py", "exec"), namespace)
        status = "passed"
    except AssertionError:
        status = "failed"
    except BaseException:
        status = "runtime_error"
print(payload["marker"] + status, flush=True)
'''


def _read_status(output: Any, marker: str, returncode: int) -> str:
    output.seek(0)
    content = output.read(1048576).decode("utf-8", errors="replace")
    statuses = re.findall(re.escape(marker) + r"(passed|failed|compile_error|runtime_error)(?:\r?\n|$)", content)
    if returncode == 0 and len(statuses) == 1:
        return statuses[0]
    if returncode in (-signal.SIGXCPU, 128 + signal.SIGXCPU):
        return "timeout"
    return "runtime_error"


def _execute(code: str, tests: str, *, backend: str, timeout: float, memory_mb: int, pids_limit: int, docker_image: str, docker: str | None) -> str:
    marker = f"__IMPROVING_{uuid.uuid4().hex}__:"
    with tempfile.TemporaryDirectory(prefix="improving-verify-") as directory, tempfile.TemporaryFile() as output:
        directory_path = Path(directory)
        directory_path.chmod(0o755)
        runner = directory_path / "runner.py"
        payload = directory_path / "payload.json"
        runner.write_text(_RUNNER, encoding="utf-8")
        payload.write_text(json.dumps(dict(code=code, tests=tests, memory=memory_mb * 1024 * 1024, timeout=timeout, marker=marker)), encoding="utf-8")
        runner.chmod(0o444)
        payload.chmod(0o444)
        if backend == "docker":
            name = f"improving-{uuid.uuid4().hex}"
            command = [docker, "run", "--rm", "--pull", "never", "--name", name,
                "--network", "none", "--read-only", "--memory", f"{memory_mb}m", "--memory-swap", f"{memory_mb}m",
                "--pids-limit", str(pids_limit), "--cpus", "1", "--cap-drop", "ALL",
                "--security-opt", "no-new-privileges", "--user", "65534:65534", "--stop-timeout", "0",
                "--ulimit", "fsize=1048576:1048576", "--ulimit", "nofile=64:64", "--ulimit", "core=0:0",
                "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m", "--workdir", "/tmp",
                "--mount", f"type=bind,src={directory_path},dst=/work,readonly", docker_image,
                "python", "-I", "/work/runner.py", "/work/payload.json"]
            try:
                result = subprocess.run(command, stdout=output, stderr=output, timeout=timeout, check=False)
            except subprocess.TimeoutExpired:
                return "timeout"
            finally:
                # Killing the client alone leaves a running container behind.
                try:
                    subprocess.run([docker, "rm", "-f", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10, check=False)
                except (OSError, subprocess.TimeoutExpired):
                    pass
            if result.returncode in (125, 126, 127):
                raise RuntimeError("Docker verification could not start; ensure the daemon and requested Python image are available (images are never pulled automatically)")
            return _read_status(output, marker, result.returncode)
        process = subprocess.Popen([sys.executable, "-I", str(runner), str(payload)], cwd=directory,
            stdout=output, stderr=output, start_new_session=True,
            env={"PATH": os.defpath, "PYTHONHASHSEED": "0", "LANG": "C.UTF-8"})
        try:
            process.wait(timeout=timeout)
            return _read_status(output, marker, process.returncode)
        except subprocess.TimeoutExpired:
            return "timeout"
        finally:
            # Also reap descendants created by a trusted fixture on early exit.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()


def verify_completions(tasks: Iterable[Mapping[str, Any]], records: Iterable[Mapping[str, Any]], backend: str = "docker", timeout: float = 5.0, allow_unsafe_local: bool = False, *, memory_mb: int = 512, pids_limit: int = 64, docker_image: str = "python:3.11-slim", expected_samples: int | None = None, workers: int = 4, code_extraction: str = "strict") -> list[dict[str, Any]]:
    """Verify every sample with task tests and preserve all original fields.

    ``timeout`` is per sample wall time, including container startup. Docker
    must already be installed and its Python image available locally. Local
    execution is only for explicitly trusted fixtures and provides no host
    filesystem/network isolation. Infrastructure failures raise; they are not
    mislabeled as model failures. Empty and invalid samples remain in output.
    """
    task_rows = validate_tasks(tasks)
    rows = _validate_groups(task_rows, records, expected_samples)
    task_map = {task["task_id"]: task for task in task_rows}
    tests = {task["task_id"]: _test_code(task) for task in task_rows}
    if backend not in {"docker", "local"}:
        raise ValueError("backend must be 'docker' or 'local'")
    if backend == "local" and not allow_unsafe_local:
        raise ValueError("Local execution requires allow_unsafe_local=True and trusted code; it is not a security sandbox")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be positive and finite")
    if any(type(value) is not int or value < 1 for value in (memory_mb, pids_limit)):
        raise ValueError("memory_mb and pids_limit must be positive integers")
    if type(workers) is not int or workers < 1:
        raise ValueError("workers must be a positive integer")
    if code_extraction not in {"strict", "first_fence"}:
        raise ValueError("code_extraction must be strict or first_fence")
    evaluation_provenance = {
        "backend": backend,
        "code_extraction": code_extraction,
        "docker_image": docker_image,
        "memory_mb": memory_mb,
        "pids_limit": pids_limit,
        "protocol_version": "task-tests-v1",
        "task_harness_sha256": stable_hash({task["task_id"]: {
            "tests": tests[task["task_id"]], "entry_point": task.get("entry_point"),
            "completion_mode": task.get("completion_mode"),
            "continuation_prefix": (task.get("code_prefix", task["prompt"])
                                    if task.get("completion_mode") == "continuation" else None),
        } for task in task_rows}),
        "timeout": float(timeout),
    }
    docker = shutil.which("docker") if backend == "docker" else None
    if backend == "docker" and docker is None:
        raise RuntimeError("Docker is required by default; install/start Docker and prepare its Python image. Local trusted execution requires explicit allow_unsafe_local=True")
    def verify_one(row: dict[str, Any]) -> dict[str, Any]:
        code = _solution_code(task_map[row["task_id"]], row["completion"], code_extraction)
        status = "empty" if not code.strip() else _execute(code, tests[row["task_id"]], backend=backend,
            timeout=timeout, memory_mb=memory_mb, pids_limit=pids_limit, docker_image=docker_image, docker=docker)
        return {**row, "code": code, "correct": status == "passed", "status": status,
                "code_extraction": code_extraction,
                "evaluation_provenance": evaluation_provenance,
                "evaluation_backend": backend, "evaluation_protocol": "task-tests-v1"}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(verify_one, rows))


def export_evalplus(tasks: Iterable[Mapping[str, Any]], records: Iterable[Mapping[str, Any]], path: str | Path) -> Path:
    """Export every full solution plus a sample-ID manifest; return its path."""
    task_rows = validate_tasks(tasks)
    rows = _validate_groups(task_rows, records)
    task_map = {task["task_id"]: task for task in task_rows}
    exported, manifest, counters = [], [], Counter()
    for row in rows:
        code = _solution_code(task_map[row["task_id"]], row["completion"])
        exported.append({"task_id": row["task_id"], "solution": code})
        manifest.append({"task_id": row["task_id"], "sample_id": row["sample_id"], "completion_index": counters[row["task_id"]],
            "solution": code, "completion_sha256": hashlib.sha256(row["completion"].encode("utf-8")).hexdigest(),
            "format": "evalplus-0.3.1"})
        counters[row["task_id"]] += 1
    manifest_path = Path(str(path) + ".manifest.jsonl")
    write_jsonl(manifest_path, manifest)
    write_jsonl(path, exported)
    return manifest_path


def import_evalplus_results(records: Iterable[Mapping[str, Any]], results_path: str | Path, *, tasks: Iterable[Mapping[str, Any]] | None = None, require_plus: bool = True, manifest_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Join official 0.3.1 results without dropping or guessing any sample.

    Pass the export manifest whenever records may have been reordered. Without
    it, input records must retain export order within each task and ``tasks``
    must be provided (or each record must contain its exact exported ``code``).
    Result solution equality is checked even when a manifest is supplied.
    """
    task_rows = None if tasks is None else validate_tasks(tasks)
    rows = validate_completions(records, task_rows) if task_rows is None else _validate_groups(task_rows, records)
    task_map = {} if task_rows is None else {task["task_id"]: task for task in task_rows}
    if manifest_path is not None:
        manifest_rows = read_jsonl(manifest_path)
        manifest = {(row.get("task_id"), row.get("sample_id")): row for row in manifest_rows}
        expected_keys = {(row["task_id"], row["sample_id"]) for row in rows}
        if len(manifest) != len(manifest_rows) or set(manifest) != expected_keys:
            raise ValueError("Manifest has duplicate, missing, or unexpected sample IDs")
    else:
        manifest = {}
    payload = json.loads(Path(results_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("eval"), dict):
        raise ValueError("Expected official EvalPlus 0.3.1 results with an 'eval' mapping")
    groups = payload["eval"]
    counts = Counter(row["task_id"] for row in rows)
    if set(groups) != set(counts):
        raise ValueError("EvalPlus result task IDs are missing or unexpected")
    for task_id, count in counts.items():
        if not isinstance(groups[task_id], list) or len(groups[task_id]) != count:
            raise ValueError(f"EvalPlus sample count mismatch for {task_id}")
    counters, used, output = Counter(), set(), []
    for row in rows:
        task_id, sample_id = row["task_id"], row["sample_id"]
        entry = manifest.get((task_id, sample_id))
        if entry is not None:
            index = entry.get("completion_index")
            if type(index) is not int or not 0 <= index < counts[task_id]:
                raise ValueError("Manifest completion_index is invalid")
            if entry.get("completion_sha256") != hashlib.sha256(row["completion"].encode("utf-8")).hexdigest():
                raise ValueError("Completion differs from its export manifest")
            code = entry.get("solution")
            if not isinstance(code, str):
                raise ValueError("Manifest solution must be a string")
        else:
            index = counters[task_id]
            if task_id in task_map:
                code = _solution_code(task_map[task_id], row["completion"])
            elif isinstance(row.get("code"), str):
                code = row["code"]
            else:
                raise ValueError("Import requires tasks, exact exported code, or manifest_path")
        counters[task_id] += 1
        if (task_id, index) in used:
            raise ValueError("Manifest maps multiple samples to one completion_index")
        used.add((task_id, index))
        result = groups[task_id][index]
        if not isinstance(result, dict) or result.get("task_id") != task_id:
            raise ValueError("EvalPlus result contains an invalid task_id")
        if result.get("solution") != code:
            raise ValueError(f"EvalPlus solution/order mismatch for {task_id}, sample {sample_id}")
        statuses = [result.get("base_status")]
        if require_plus:
            statuses.append(result.get("plus_status"))
        for field, status in zip(("base_status", "plus_status"), statuses):
            if status not in {"pass", "fail", "timeout"}:
                raise ValueError(f"Unsupported or missing EvalPlus {field}: {status!r}")
        correct = all(status == "pass" for status in statuses)
        status = "passed" if correct else "timeout" if "timeout" in statuses else "failed"
        output.append({**row, "code": code, "correct": correct, "status": status,
            "evaluation_backend": "evalplus", "evaluation_protocol": "evalplus-0.3.1-plus" if require_plus else "evalplus-0.3.1-base",
            "evalplus_base_status": result.get("base_status"), "evalplus_plus_status": result.get("plus_status"),
            "evalplus_dataset_hash": payload.get("hash")})
    return output
