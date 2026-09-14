import json
import shutil
import subprocess

import pytest

from improving import verification
from improving.data import read_jsonl


def task(**extra):
    return {"task_id": "Fixture/0", "prompt": "Add two integers.", "source": "fixture", "split": "eval",
            "entry_point": "add", "tests": "assert add(2, 3) == 5\nassert add(-1, 1) == 0", **extra}


def completion(code="def add(a, b):\n    return a + b", sample_id=0, **extra):
    return {"task_id": "Fixture/0", "sample_id": sample_id, "completion": code, **extra}


def test_extraction_only_removes_a_single_outer_code_fence():
    assert verification.extract_python_code("```python\ndef add(a, b):\n    return a+b\n```\n") == "def add(a, b):\n    return a+b\n"
    raw = "Here is code:\n```python\npass\n```\nExplanation."
    assert verification.extract_python_code(raw) == raw
    assert verification.extract_python_code("    return 4\n") == "    return 4\n"


def test_first_fence_extraction_ignores_surrounding_prose_and_accepts_unclosed_fence():
    surrounded = "Here is the solution:\n```python\ndef add(a, b):\n    return a + b\n```\nExplanation."
    assert verification.extract_python_code(surrounded, mode="first_fence") == "def add(a, b):\n    return a + b\n"
    unclosed = "```py\ndef add(a, b):\n    return a + b\n"
    assert verification.extract_python_code(unclosed, mode="first_fence") == "def add(a, b):\n    return a + b\n"
    raw = "def add(a, b):\n    return a + b\n"
    assert verification.extract_python_code(raw, mode="first_fence") == raw


def test_first_fence_mode_changes_execution_and_is_recorded():
    row = completion("Prose.\n```python\ndef add(a, b):\n    return a + b\n```\nMore prose.")
    strict = verification.verify_completions(
        [task()], [row], backend="local", allow_unsafe_local=True)
    fenced = verification.verify_completions(
        [task()], [row], backend="local", allow_unsafe_local=True,
        code_extraction="first_fence")
    assert strict[0]["status"] == "compile_error"
    assert fenced[0]["status"] == "passed"
    assert fenced[0]["code_extraction"] == "first_fence"
    assert fenced[0]["evaluation_provenance"] == {
        "backend": "local", "code_extraction": "first_fence",
        "docker_image": "python:3.11-slim", "protocol_version": "task-tests-v2", "provenance_version": 2,
        "task_harness_sha256": fenced[0]["evaluation_provenance"]["task_harness_sha256"],
        "runner_sha256": fenced[0]["evaluation_provenance"]["runner_sha256"],
        "local_python_version": fenced[0]["evaluation_provenance"]["local_python_version"],
        "timeout": 5.0, "memory_mb": 512, "pids_limit": 64,
    }
    assert len(fenced[0]["evaluation_provenance"]["task_harness_sha256"]) == 64


def test_provenance_changes_when_continuation_harness_changes():
    base = task(completion_mode="continuation", code_prefix="def add(a, b):\n")
    changed = task(completion_mode="continuation", code_prefix="def add(a, b, c=0):\n")
    row = completion("    return a + b\n")
    first = verification.verify_completions(
        [base], [row], backend="local", allow_unsafe_local=True)[0]
    second = verification.verify_completions(
        [changed], [row], backend="local", allow_unsafe_local=True)[0]
    assert (first["evaluation_provenance"]["task_harness_sha256"] !=
            second["evaluation_provenance"]["task_harness_sha256"])


def test_unknown_code_extraction_mode_is_rejected():
    with pytest.raises(ValueError, match="code_extraction"):
        verification.verify_completions(
            [task()], [completion()], backend="local", allow_unsafe_local=True,
            code_extraction="guess")


def test_local_execution_requires_explicit_trust():
    with pytest.raises(ValueError, match="allow_unsafe_local"):
        verification.verify_completions([task()], [completion()], backend="local")


def test_trusted_fixtures_preserve_correct_wrong_empty_invalid_and_timeout():
    records = [completion(method="fixture"), completion("def add(a, b):\n    return 0", 1),
               completion("", 2), completion("def broken(:", 3), completion("while True:\n    pass", 4),
               completion("raise RuntimeError('boom')", 5)]
    verified = verification.verify_completions([task()], records, backend="local", allow_unsafe_local=True, timeout=0.3)
    assert len(verified) == len(records)
    assert [row["correct"] for row in verified] == [True, False, False, False, False, False]
    assert [row["status"] for row in verified] == ["passed", "failed", "empty", "compile_error", "timeout", "runtime_error"]
    for original, row in zip(records, verified):
        assert all(row[key] == value for key, value in original.items())


def test_humaneval_continuation_and_full_function_both_run_check():
    human = task(prompt='def add(a, b):\n    """Add integers."""\n',
                 code_prefix='def add(a, b):\n    """Add integers."""\n',
                 completion_mode="continuation", test_mode="check", tests="def check(candidate):\n    assert candidate(2, 3) == 5\n")
    verified = verification.verify_completions([human], [completion("    return a + b\n"), completion(sample_id=1),
        completion("    return 0\n", sample_id=2)], backend="local", allow_unsafe_local=True)
    assert [row["correct"] for row in verified] == [True, True, False]


def test_missing_tasks_duplicate_keys_and_incomplete_budgets_are_errors():
    with pytest.raises(ValueError, match="Missing"):
        verification.verify_completions([task()], [])
    with pytest.raises(ValueError, match="Duplicate"):
        verification.verify_completions([task()], [completion(), completion()])
    with pytest.raises(ValueError, match="expected_samples"):
        verification.verify_completions([task()], [completion()], expected_samples=2)
    with pytest.raises(ValueError, match="tests"):
        verification.verify_completions([task(tests="")], [completion()])


def test_parallel_verification_preserves_input_order_and_rejects_bad_workers():
    rows = [completion("import time\ntime.sleep(0.05)\ndef add(a,b): return a+b", 19), completion("def add(a,b): return 0", 3)]
    verified = verification.verify_completions([task()], rows, backend="local", allow_unsafe_local=True, workers=2)
    assert [(row["sample_id"], row["correct"]) for row in verified] == [(19, True), (3, False)]
    with pytest.raises(ValueError, match="workers"):
        verification.verify_completions([task()], rows, backend="local", allow_unsafe_local=True, workers=0)


def test_early_clean_exit_does_not_bypass_checks():
    rows = [completion("import os\nos._exit(0)"), completion("raise SystemExit(0)", 1)]
    result = verification.verify_completions([task()], rows, backend="local", allow_unsafe_local=True)
    assert [row["correct"] for row in result] == [False, False]
    assert [row["status"] for row in result] == ["runtime_error", "runtime_error"]


def test_evalplus_manifest_restores_mapping_after_records_reordered(tmp_path):
    rows = [completion(sample_id=7), completion("def add(a,b): return 0", 11)]
    path = tmp_path / "samples.jsonl"
    manifest = verification.export_evalplus([task()], rows, path)
    results = {"eval": {"Fixture/0": [
        {"task_id": "Fixture/0", "solution": row["completion"], "base_status": status, "plus_status": status}
        for row, status in zip(rows, ["pass", "fail"])]}}
    result_path = tmp_path / "results.json"
    result_path.write_text(json.dumps(results))
    imported = verification.import_evalplus_results(rows[::-1], result_path, manifest_path=manifest)
    assert [(row["sample_id"], row["correct"]) for row in imported] == [(11, False), (7, True)]


def test_missing_docker_never_falls_back_to_host(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda executable: None)
    with pytest.raises(RuntimeError, match="Docker"):
        verification.verify_completions([task()], [completion()])


def test_docker_command_is_isolated_and_timeout_removes_container(monkeypatch):
    commands = []
    monkeypatch.setattr(shutil, "which", lambda executable: "/usr/bin/docker")

    def run(command, **kwargs):
        commands.append(command)
        if command[1] == "run":
            raise subprocess.TimeoutExpired(command, kwargs["timeout"])
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", run)
    result = verification.verify_completions([task()], [completion()], timeout=0.1)
    assert result[0]["status"] == "timeout"
    command = commands[0]
    assert command[command.index("--network") + 1] == "none"
    assert "--read-only" in command and "--pids-limit" in command and "--memory" in command
    assert command[command.index("--cap-drop") + 1] == "ALL"
    assert "readonly" in command[command.index("--mount") + 1]
    container_name = command[command.index("--name") + 1]
    assert commands[-1] == ["/usr/bin/docker", "rm", "-f", container_name]


def test_evalplus_official_v031_bridge_preserves_noncontiguous_ids(tmp_path):
    rows = [completion(sample_id=7), completion("", 2), completion("def add(a, b):\n    return 0", 99)]
    export_path = tmp_path / "samples.jsonl"
    manifest = verification.export_evalplus([task()], rows, export_path)
    exported = read_jsonl(export_path)
    assert len(exported) == 3
    assert exported[1]["solution"] == ""
    assert manifest.exists()
    results = {"date": "fixture", "hash": "fixture-hash", "eval": {"Fixture/0": [
        {"task_id": "Fixture/0", "solution": row["solution"], "base_status": base, "plus_status": plus,
         "base_fail_tests": [], "plus_fail_tests": []}
        for row, base, plus in zip(exported, ["pass", "fail", "pass"], ["pass", "fail", "fail"])]}}
    result_path = tmp_path / "samples_eval_results.json"
    result_path.write_text(json.dumps(results))
    verified = verification.import_evalplus_results(rows, result_path, tasks=[task()], manifest_path=manifest)
    assert [row["sample_id"] for row in verified] == [7, 2, 99]
    assert [row["correct"] for row in verified] == [True, False, False]
    assert all(row["evaluation_backend"] == "evalplus" for row in verified)
    results["eval"]["Fixture/0"].pop()
    result_path.write_text(json.dumps(results))
    with pytest.raises(ValueError, match="count"):
        verification.import_evalplus_results(rows, result_path, tasks=[task()], manifest_path=manifest)


def test_evalplus_rejects_missing_plus_and_changed_solution(tmp_path):
    rows = [completion()]
    row = {"task_id": "Fixture/0", "solution": rows[0]["completion"], "base_status": "pass", "plus_status": None}
    path = tmp_path / "results.json"
    path.write_text(json.dumps({"eval": {"Fixture/0": [row]}}))
    with pytest.raises(ValueError, match="plus_status"):
        verification.import_evalplus_results(rows, path, tasks=[task()])
    assert verification.import_evalplus_results(rows, path, tasks=[task()], require_plus=False)[0]["correct"]
    row.update(solution="def add(a,b): return 123", plus_status="pass")
    path.write_text(json.dumps({"eval": {"Fixture/0": [row]}}))
    with pytest.raises(ValueError, match="solution"):
        verification.import_evalplus_results(rows, path, tasks=[task()])


def test_verification_provenance_is_batching_invariant_and_detects_changed_tests():
    from improving.metrics import summarize_records, compare_summaries
    tasks = [task(), task(task_id="Fixture/1", prompt="Another addition problem.")]
    rows = [completion(), completion(task_id="Fixture/1")]
    options = dict(backend="local", allow_unsafe_local=True)
    joint = verification.verify_completions(tasks, rows, **options)
    separate = [verification.verify_completions([t], [r], **options)[0] for t, r in zip(tasks, rows)]
    assert joint == separate
    a, b = [summarize_records(value, ks=[1], bootstrap_samples=0) for value in (joint, separate)]
    assert a == b
    assert set(a["protocol"]["evaluation_task_harnesses"]) == {"Fixture/0", "Fixture/1"}
    assert compare_summaries(a, b, bootstrap_samples=0)["evaluation_identity_check"] == "declared_provenance_equal"
    changed = verification.verify_completions([task(tests="assert add(1, 2) == 3")], [rows[0]], **options)
    c = summarize_records(changed + separate[1:], ks=[1], bootstrap_samples=0)
    with pytest.raises(ValueError, match="evaluation provenance"):
        compare_summaries(a, c)
    changed[0]["sample_id"] = 1
    with pytest.raises(ValueError, match="changed task harness"):
        summarize_records(joint + changed)


def test_evalplus_first_fence_manifest_reproduces_code_and_both_correctnesses(tmp_path):
    rows = [completion("Prose.\n```python\ndef add(a,b): return a+b\n```\nExplanation.")]
    path = tmp_path / "samples.jsonl"
    manifest = verification.export_evalplus([task()], rows, path, code_extraction="first_fence")
    exported = read_jsonl(path)
    payload = {"hash": "official-fixture-hash", "eval": {"Fixture/0": [dict(exported[0], base_status="pass", plus_status="fail")]}}
    result_path = tmp_path / "results.json"
    result_path.write_text(json.dumps(payload))
    imported = verification.import_evalplus_results(rows, result_path, manifest_path=manifest)
    row = imported[0]
    assert row["completion"] == rows[0]["completion"]
    assert row["code"] == "def add(a,b): return a+b\n"
    assert row["code_extraction"] == "first_fence"
    assert row["base_correct"] is True and row["plus_correct"] is False and row["correct"] is False
    assert row["evaluation_provenance"]["dataset_hash"] == "official-fixture-hash"
    assert row["evaluation_provenance"]["export_identity"] == "manifest_v2_reproduced"
    base = verification.import_evalplus_results(rows, result_path, manifest_path=manifest, require_plus=False)[0]
    assert base["correct"] is True and base["plus_correct"] is False
    entries = read_jsonl(manifest)
    entries[0]["code_extraction"] = "strict"
    from improving.data import write_jsonl
    write_jsonl(manifest, entries)
    with pytest.raises(ValueError, match="code_extraction"):
        verification.import_evalplus_results(rows, result_path, manifest_path=manifest)


def test_evalplus_manifest_rejects_changed_task_context_and_preserves_continuation(tmp_path):
    human = task(completion_mode="continuation", code_prefix="def add(a,b):\n")
    rows = [completion("Here:\n```python\n    return a+b\n```\nDone.")]
    path = tmp_path / "samples.jsonl"
    manifest = verification.export_evalplus([human], rows, path, code_extraction="first_fence")
    exported = read_jsonl(path)
    assert exported[0]["solution"] == "def add(a,b):\n    return a+b\n"
    results = tmp_path / "result.json"
    results.write_text(json.dumps({"hash": "fixture", "eval": {"Fixture/0": [dict(exported[0], base_status="pass", plus_status="pass")]}}))
    assert verification.import_evalplus_results(rows, results, manifest_path=manifest)[0]["correct"]
    changed = dict(human, code_prefix="def add(a,b,c=0):\n")
    with pytest.raises(ValueError, match="Task harness"):
        verification.import_evalplus_results(rows, results, manifest_path=manifest, tasks=[changed])
