"""Failure-phase contracts for the native verifier; trusted fixtures only."""
import io
import json
import signal

import pytest

from improving import verification


def verify(code, tests="assert add(2, 3) == 5", **options):
    task = {"task_id": "Fixture/diagnostic", "prompt": "Add integers.",
            "source": "fixture", "split": "eval", "tests": tests}
    row = {"task_id": task["task_id"], "sample_id": 0, "completion": code}
    return verification.verify_completions(
        [task], [row], backend="local", allow_unsafe_local=True,
        workers=1, **options)[0]


@pytest.mark.parametrize("code,tests,status,phase,exception", [
    ("def broken(:", "assert True", "compile_error", "candidate_compile", "SyntaxError"),
    ("raise ValueError('candidate failed')", "assert True", "runtime_error", "candidate_exec", "ValueError"),
    ("pass", "return", "runtime_error", "tests_compile", "SyntaxError"),
    ("pass", "assert missing_name == 1", "runtime_error", "tests_exec", "NameError"),
    ("def add(a, b): return 0", "assert add(2, 3) == 5", "failed", "tests_exec", "AssertionError"),
    ("raise AssertionError('candidate assertion')", "assert True", "failed", "candidate_exec", "AssertionError"),
])
def test_failure_phase_preserves_existing_correctness(code, tests, status, phase, exception):
    row = verify(code, tests)
    assert row["completion"] == code
    assert row["status"] == status
    assert row["correct"] is False
    assert row["verification_error"]["phase"] == phase
    assert row["verification_error"]["exception_type"] == exception


def test_test_invoked_candidate_error_retains_both_safe_frame_locations():
    row = verify("def add(a, b):\n    return missing_candidate_name")
    error = row["verification_error"]
    assert error["phase"] == "tests_exec"
    assert [frame["filename"] for frame in error["frames"]] == ["tests.py", "candidate.py"]
    assert error["frames"][-1]["lineno"] == 2
    assert error["frames"][-1]["name"] == "add"


def test_diagnostics_bound_frames_and_messages_and_redact_absolute_paths():
    code = "def f(n):\n    if n: return f(n - 1)\n    raise ValueError('/private/work/run/file.py ' + 'x' * 2000)\nf(8)"
    error = verify(code, "assert True")["verification_error"]
    assert len(error["frames"]) == 4
    assert all(frame["filename"] == "candidate.py" for frame in error["frames"])
    assert len(error["message"]) <= 512
    assert "/private" not in error["message"]
    assert "<path>" in error["message"]


def test_exception_formatting_cannot_turn_failure_into_pass():
    code = "class BadError(Exception):\n    def __str__(self): raise RuntimeError('format failed')\nraise BadError('original failure')"
    row = verify(code, "assert True")
    assert row["status"] == "runtime_error"
    assert row["correct"] is False
    assert row["verification_error"]["phase"] == "candidate_exec"
    assert row["verification_error"]["message"] == "original failure"


def test_diagnostics_do_not_call_candidate_exception_attribute_hooks():
    code = "class Meta(type):\n    def __getattribute__(cls, name):\n        if name == '__name__': raise AssertionError('metaclass hook called')\n        return super().__getattribute__(name)\nclass BadSyntax(SyntaxError, metaclass=Meta):\n    def __getattribute__(self, name):\n        if name in ('filename', 'lineno'): raise AssertionError('attribute hook called')\n        return super().__getattribute__(name)\nraise BadSyntax('original failure')"
    row = verify(code, "assert True")
    assert row["status"] == "runtime_error"
    assert row["verification_error"]["phase"] == "candidate_exec"
    assert row["verification_error"]["exception_type"] == "BadSyntax"
    assert row["verification_error"]["message"] == "original failure"


def test_exception_class_property_is_not_consulted_for_syntax_details():
    code = "class BadError(Exception):\n    @property\n    def __class__(self): raise AssertionError('class hook called')\nraise BadError('original failure')"
    row = verify(code, "assert True")
    assert row["status"] == "runtime_error"
    assert row["verification_error"]["phase"] == "candidate_exec"
    assert row["verification_error"]["exception_type"] == "BadError"


def test_exception_argument_type_comparisons_do_not_call_metaclass_equality():
    code = "class Meta(type):\n    def __eq__(cls, other): raise AssertionError('equality hook called')\nclass Argument(metaclass=Meta): pass\nraise ValueError(Argument())"
    row = verify(code, "assert True")
    assert row["status"] == "runtime_error"
    assert row["verification_error"]["phase"] == "candidate_exec"
    assert row["verification_error"]["exception_type"] == "ValueError"
    assert row["verification_error"]["message"] == ""


def test_exception_name_string_subclass_cannot_run_slicing_hooks():
    code = "class EvilStr(str):\n    def __getitem__(self, key): raise AssertionError('slice hook called')\nclass BadError(Exception): pass\nBadError.__name__ = EvilStr('BadError')\nraise BadError('original failure')"
    row = verify(code, "assert True")
    assert row["status"] == "runtime_error"
    assert row["verification_error"]["phase"] == "candidate_exec"
    assert row["verification_error"]["exception_type"] == "BadError"


@pytest.mark.parametrize("code,status", [
    ("import os\nos._exit(0)", "runtime_error"),
    ("while True: pass", "timeout"),
])
def test_missing_diagnostic_never_guesses_failure_phase(code, status):
    row = verify(code, "assert True", timeout=0.3)
    assert row["status"] == status
    assert row["verification_error"]["phase"] == "unknown"
    assert row["verification_error"]["exception_type"] is None
    assert row["verification_error"]["frames"] == []


def test_pass_and_legacy_execute_return_contract_are_unchanged():
    assert verify("def add(a, b): return a + b")["verification_error"] is None
    assert verification._execute(
        "pass", "assert True", backend="local", timeout=5, memory_mb=512,
        pids_limit=64, docker_image="python:3.11-slim", docker=None) == "passed"


@pytest.mark.parametrize("returncode,duplicate,malformed", [
    (-signal.SIGKILL, False, False), (0, True, False), (0, False, True),
])
def test_untrusted_or_ambiguous_auxiliary_markers_are_unknown(returncode, duplicate, malformed):
    marker = "__IMPROVING_fixture__:"
    error = {"status": "runtime_error", "phase": "candidate_exec",
             "exception_type": "NameError", "message": "missing", "frames": []}
    line = marker + "error:" + ("{broken" if malformed else json.dumps(error)) + "\n"
    output = io.BytesIO((marker + "runtime_error\n" + line * (2 if duplicate else 1)).encode())
    assert verification._read_verification_error(
        output, marker, returncode, "runtime_error")["phase"] == "unknown"


def test_ordinary_stdout_error_text_is_not_a_diagnostic_marker():
    output = io.BytesIO(b'error:{"phase":"candidate_exec"}\n')
    assert verification._read_verification_error(
        output, "__IMPROVING_fixture__:", 0, "runtime_error")["phase"] == "unknown"


@pytest.mark.parametrize("extra", ["", "x" * 16385])
def test_valid_diagnostic_plus_malformed_duplicate_is_not_accepted(extra):
    marker = "__IMPROVING_fixture__:"
    error = {"status": "runtime_error", "phase": "candidate_exec",
             "exception_type": "NameError", "message": "missing", "frames": []}
    content = marker + "runtime_error\n" + marker + "error:" + json.dumps(error) + "\n"
    content += marker + "error:" + extra + "\n"
    assert verification._read_verification_error(
        io.BytesIO(content.encode()), marker, 0, "runtime_error")["phase"] == "unknown"
