import json
import sys
import types

import pytest

from improving import data


def task(task_id="Fixture/0", prompt="Write a function.", split="train"):
    return {"task_id": task_id, "prompt": prompt, "source": "fixture", "split": split}


def test_jsonl_roundtrip_and_atomic_failure_preserve_existing(tmp_path):
    path = tmp_path / "nested" / "rows.jsonl"
    original = [{"text": "λ\nhello", "sample_id": 0}]
    data.write_jsonl(path, iter(original))
    assert data.read_jsonl(path) == original
    with pytest.raises((TypeError, ValueError)):
        data.write_jsonl(path, [{"text": "replacement"}, {"bad": object()}])
    assert data.read_jsonl(path) == original
    assert list(path.parent.iterdir()) == [path]


def test_jsonl_rejects_nonobjects_and_reports_line(tmp_path):
    path = tmp_path / "bad.jsonl"
    path.write_text('{"ok": 1}\n[1, 2]\n')
    with pytest.raises(ValueError, match="line 2"):
        data.read_jsonl(path)


def test_validation_rejects_duplicate_and_unknown_completion_ids():
    row = {"task_id": "Fixture/0", "sample_id": 0, "completion": ""}
    assert data.validate_completions([row], [task()]) == [row]
    with pytest.raises(ValueError, match="Duplicate"):
        data.validate_completions([row, row], [task()])
    with pytest.raises(ValueError, match="Unknown"):
        data.validate_completions([dict(row, task_id="Fixture/missing")], [task()])
    with pytest.raises(ValueError, match="sample_id"):
        data.validate_completions([dict(row, sample_id=True)])
    with pytest.raises(ValueError, match="Duplicate"):
        data.validate_tasks([task(), task()])


def test_validation_checks_calibration_span_bounds():
    good = dict(task(), reference="return 1", calibration_spans=[[0, 6]])
    assert data.validate_tasks([good]) == [good]
    with pytest.raises(ValueError, match="calibration_spans"):
        data.validate_tasks([dict(good, calibration_spans=[[3, 99]])])


def test_split_leakage_checks_ids_and_normalized_prompts():
    data.assert_disjoint_splits({"train": [task()], "eval": [task("Fixture/1", "Different task", "eval")]})
    with pytest.raises(ValueError, match="task_id"):
        data.assert_disjoint_splits({"train": [task()], "eval": [task(split="eval", prompt="Other")]})
    with pytest.raises(ValueError, match="prompt"):
        data.assert_disjoint_splits({"train": [task()], "eval": [task("Fixture/1", "  Write\n a function.  ", "eval")]})


def test_mbpp_uses_official_train_pool_and_preserves_provenance(tmp_path, monkeypatch):
    def example(i):
        return {"task_id": i, "text": f"Return integer {i}", "code": f"def f{i}():\n    return {i}",
                "test_list": [f"assert f{i}() == {i}"], "test_setup_code": "", "challenge_test_list": []}

    calls = []
    def load_dataset(name, config, **kwargs):
        calls.append((name, config, kwargs))
        return {"train": [example(i) for i in range(601, 607)], "test": [example(11)],
                "validation": [example(511)], "prompt": [example(1)]}

    monkeypatch.setitem(sys.modules, "datasets", types.SimpleNamespace(load_dataset=load_dataset))
    first = data.prepare_mbpp(tmp_path / "first", seed=7, calibration_size=2, validation_size=1, revision="pinned")
    second = data.prepare_mbpp(tmp_path / "second", seed=7, calibration_size=2, validation_size=1, revision="pinned")
    assert first == second
    assert {split: len(rows) for split, rows in first.items()} == {"train": 3, "calibration": 2, "validation": 1, "eval": 1}
    assert {row["task_id"] for split in ("train", "calibration", "validation") for row in first[split]} == {f"Mbpp/{i}" for i in range(601, 607)}
    assert first["eval"][0]["task_id"] == "Mbpp/11"
    assert first["eval"][0]["original_split"] == "test"
    assert first["eval"][0]["original_prompt"] == "Return integer 11"
    assert "def f11():" in first["eval"][0]["prompt"]
    assert "assert f11" not in first["eval"][0]["prompt"]
    assert "return 11" not in first["eval"][0]["prompt"]
    assert first["eval"][0]["prompt_protocol"] == "mbpp-function-interface-v1"
    assert all(row["revision"] == "pinned" for rows in first.values() for row in rows)
    assert calls[0] == ("google-research-datasets/mbpp", "full", {"revision": "pinned"})
    for split, rows in first.items():
        assert data.read_jsonl(tmp_path / "first" / f"{split}.jsonl") == rows


def test_mbpp_refuses_to_exhaust_train_pool(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "datasets", types.SimpleNamespace(load_dataset=lambda *a, **k: {"train": [], "test": []}))
    with pytest.raises(ValueError, match="train"):
        data.prepare_mbpp(tmp_path, calibration_size=0, validation_size=0)


def test_humaneval_preserves_original_body_prompt_and_check(tmp_path, monkeypatch):
    problem = {"task_id": "HumanEval/0", "prompt": "def add(a, b):\n    \"\"\"Add integers.\"\"\"\n",
               "canonical_solution": "    return a + b\n", "entry_point": "add",
               "test": "def check(candidate):\n    assert candidate(2, 3) == 5\n"}
    monkeypatch.setitem(sys.modules, "evalplus.data.humaneval", types.SimpleNamespace(get_human_eval=lambda: {"HumanEval/0": problem}))
    prepared = data.prepare_humaneval(tmp_path)
    assert prepared["eval"][0]["reference"] == "    return a + b\n"
    assert prepared["eval"][0]["prompt"] == problem["prompt"]
    assert prepared["eval"][0]["tests"] == problem["test"]
    assert prepared["eval"][0]["completion_mode"] == "continuation"
    assert prepared["eval"][0]["test_mode"] == "check"
    assert data.read_jsonl(tmp_path / "eval.jsonl") == prepared["eval"]


def test_mbpp_stub_omits_decorators_annotations_and_executable_defaults(tmp_path, monkeypatch):
    example = {"task_id": 601, "text": "Add values.", "code": "@decorator()\ndef add(a: Danger(), b=side_effect(), /, *args, c: str='secret', **kwargs) -> Danger():\n    return 314159\n", "test_list": ["assert add(1, 2) == 3"], "test_setup_code": ""}
    monkeypatch.setitem(sys.modules, "datasets", types.SimpleNamespace(load_dataset=lambda *a, **k: {"train": [example], "test": []}))
    prepared = data.prepare_mbpp(tmp_path, calibration_size=0, validation_size=0)
    prompt = prepared["train"][0]["prompt"]
    assert "def add(a, b=..., /, *args, c=..., **kwargs):" in prompt
    assert all(value not in prompt for value in ["Danger", "decorator", "side_effect", "314159", "secret"])


def test_split_leakage_checks_original_prompts_after_interface_templating():
    with pytest.raises(ValueError, match="prompt"):
        data.assert_disjoint_splits({"train": [dict(task(), original_prompt="Same source")],
            "eval": [dict(task("Fixture/1", "Different interface", "eval"), original_prompt="Same source")]})


def _mbpp_example(task_id, text=None):
    return {"task_id": task_id, "text": text or f"Return integer {task_id}",
            "code": f"def f{task_id}():\n    return {task_id}",
            "test_list": [f"assert f{task_id}() == {task_id}"], "test_setup_code": ""}


def test_mbpp_removes_original_prompt_overlap_before_assigning_splits(tmp_path, monkeypatch):
    raw = {"train": [_mbpp_example(601, "  Find\n the minimum. "),
                     *[_mbpp_example(i) for i in range(602, 608)]],
           "test": [_mbpp_example(216, "Find the minimum."), _mbpp_example(217)]}
    monkeypatch.setitem(sys.modules, "datasets", types.SimpleNamespace(load_dataset=lambda *a, **k: raw))
    prepared = data.prepare_mbpp(tmp_path, seed=42, calibration_size=2, validation_size=1)
    assert {split: len(rows) for split, rows in prepared.items()} == {
        "train": 3, "calibration": 2, "validation": 1, "eval": 2}
    assert [row["task_id"] for row in prepared["eval"]] == ["Mbpp/216", "Mbpp/217"]
    assert "Mbpp/601" not in {row["task_id"] for rows in prepared.values() for row in rows}
    data.assert_disjoint_splits(prepared)
    manifest, = data.read_jsonl(tmp_path / "preparation_manifest.jsonl")
    assert manifest["source_counts"] == {"train": 7, "test": 2}
    assert manifest["clean_train_pool_count"] == 6
    assert manifest["output_counts"] == {key: len(rows) for key, rows in prepared.items()}
    assert manifest["exclusions"] == [{
        "task_id": "Mbpp/601", "original_task_id": 601, "original_split": "train",
        "reason": "original_prompt_overlaps_official_test",
        "prompt_fingerprint": data.prompt_fingerprint("Find the minimum."),
        "matching_task_ids": ["Mbpp/216"]}]
    assert all(len(value["prompt_snapshot_sha256"]) == 64 for value in manifest["source_fingerprints"].values())


def test_mbpp_deduplicates_pool_by_lowest_id_before_shuffle(tmp_path, monkeypatch):
    pool = [_mbpp_example(702, "Find the maximum."), _mbpp_example(601, "Find\n the maximum."),
            *[_mbpp_example(i) for i in range(602, 606)]]
    raw = {"train": pool, "test": [_mbpp_example(216)]}
    monkeypatch.setitem(sys.modules, "datasets", types.SimpleNamespace(load_dataset=lambda *a, **k: raw))
    first = data.prepare_mbpp(tmp_path / "first", seed=9, calibration_size=2, validation_size=1)
    raw["train"] = list(reversed(pool))
    second = data.prepare_mbpp(tmp_path / "second", seed=9, calibration_size=2, validation_size=1)
    assert first == second
    assert {split: len(rows) for split, rows in first.items()} == {
        "train": 2, "calibration": 2, "validation": 1, "eval": 1}
    retained = {row["task_id"] for split, rows in first.items() if split != "eval" for row in rows}
    assert "Mbpp/601" in retained and "Mbpp/702" not in retained
    manifest, = data.read_jsonl(tmp_path / "first" / "preparation_manifest.jsonl")
    assert manifest == data.read_jsonl(tmp_path / "second" / "preparation_manifest.jsonl")[0]
    assert manifest["exclusions"][0]["reason"] == "duplicate_original_prompt_in_train_pool"
    assert manifest["exclusions"][0]["matching_task_ids"] == ["Mbpp/601"]
    assert manifest["excluded_count"] == 1


def test_mbpp_checks_remaining_capacity_after_decontamination(tmp_path, monkeypatch):
    raw = {"train": [_mbpp_example(601, "Same task"), _mbpp_example(602)],
           "test": [_mbpp_example(216, "Same task")]}
    monkeypatch.setitem(sys.modules, "datasets", types.SimpleNamespace(load_dataset=lambda *a, **k: raw))
    with pytest.raises(ValueError, match="train pool"):
        data.prepare_mbpp(tmp_path, calibration_size=1, validation_size=0)
