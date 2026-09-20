"""LCB private fixtures retain large official tests without unbounded decoding."""
import base64
import json
import pickle
import zlib

import pytest

from improving import benchmarks


def _encoded(value):
    return base64.b64encode(zlib.compress(pickle.dumps(value))).decode()


def test_private_fixture_larger_than_legacy_limit_retains_entire_test():
    # Official abc304_e exceeds 64 MiB; no private inputs may be discarded.
    input_text = "x" * (65 * 1024 * 1024)
    fixture = _encoded(json.dumps([
        {"input": input_text, "output": "answer", "testtype": "stdin"}
    ]))
    decoded = benchmarks._private_lcb_tests(fixture, "large-official-shape")
    assert len(decoded) == 1
    assert decoded[0]["input"] == input_text
    assert decoded[0]["output"] == "answer"
    assert decoded[0]["testtype"] == "stdin"


def test_private_fixture_exceeding_bound_is_rejected(monkeypatch):
    monkeypatch.setattr(benchmarks, "_LCB_MAX_PRIVATE_TEST_BYTES", 128)
    with pytest.raises(ValueError, match="cannot decode"):
        benchmarks._private_lcb_tests(_encoded(json.dumps(["x" * 256])), "too-large")


def test_private_fixture_truncated_zlib_is_rejected():
    compressed = zlib.compress(pickle.dumps("[]"))[:-1]
    with pytest.raises(ValueError, match="cannot decode"):
        benchmarks._private_lcb_tests(base64.b64encode(compressed).decode(), "truncated")


def test_private_fixture_pickle_global_remains_forbidden():
    with pytest.raises(ValueError, match="cannot decode") as error:
        benchmarks._private_lcb_tests(_encoded(str), "pickle-global")
    assert "forbidden pickle global" in str(error.value.__cause__)
