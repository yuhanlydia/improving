import json
from pathlib import Path

import pytest

from improving import formal_transfer as transfer
from improving.data import read_jsonl, write_jsonl
from improving.pipeline import checkpoint_fingerprint, file_sha
from improving.utils import atomic_json, stable_hash


def official_tasks():
    return [{"task_id": f"HumanEval/{i}", "prompt": f"def f{i}():\n    \"\"\"Return one.\"\"\"\n",
             "code_prefix": f"def f{i}():\n    \"\"\"Return one.\"\"\"\n",
             "reference": "    return 1\n", "entry_point": f"f{i}", "source": "evalplus/HumanEvalPlus",
             "split": "eval", "revision": "v0.1.10", "dataset_sha256": "a" * 64,
             "completion_mode": "continuation", "prompt_protocol": "evalplus-original-0.3.1"}
            for i in range(164)]


def metadata():
    return {"evalplus_version": "0.3.1", "datasets": {"HumanEvalPlus": {
        "version": "v0.1.10", "task_count": 164, "sha256": "a" * 64}}}


def setup(tmp_path, monkeypatch, prepare=False):
    config = {"output_dir": str(tmp_path / "suite"), "generation": {"batch_size": 2},
              "evaluation": {"ks": [1, 2], "code_extraction": "first_fence", "correct_budget": 2},
              "transfer": {"tasks": str(tmp_path / "human/tasks.jsonl"), "samples": 2,
                           "methods": ["plain"], "bootstrap_samples": 4}}
    source = tmp_path / "source"
    model = tmp_path / "base_model"
    model.mkdir()
    atomic_json(model / "config.json", {"model_type": "fixture"})
    (model / "model.safetensors").write_bytes(b"fixture-not-loaded")
    source_config = {"output_dir": str(source), "model": {"name": str(model)}, "seed": 42,
                     "methods": ["plain"], "rounds": 1, "data": {}}
    for index, split in enumerate(("train", "calibration", "validation", "eval")):
        path = tmp_path / f"{split}.jsonl"
        write_jsonl(path, [{"task_id": f"Mbpp/{index}", "prompt": f"Write different function {index}",
                            "reference": "def f(): return 1", "source": "mbpp", "split": split}])
        source_config["data"][split] = str(path)
    local = checkpoint_fingerprint(model)
    base_identity = stable_hash([source_config["model"], None, local])
    atomic_json(source / "manifest.json", {"config": source_config, "local_base_fingerprint": local})
    write_jsonl(source / "base/evaluation.jsonl", [{"some": "source-output"}])
    atomic_json(source / "base/complete.json", {"evaluation_sha": file_sha(source / "base/evaluation.jsonl"),
                                              "model_identity": base_identity, "resolved_revision": None})
    folder = source / "plain/round_1"
    atomic_json(folder / "model/config.json", {"model_type": "fixture"})
    (folder / "model/model.safetensors").write_bytes(b"trained-fixture-not-loaded")
    fingerprint = checkpoint_fingerprint(folder / "model")
    atomic_json(folder / "complete.json", {"status": "completed", "model_identity": stable_hash([
        base_identity, "plain", 1, fingerprint]), "files": {
            str(path.relative_to(folder)): file_sha(path) for path in (folder / "model").iterdir()}})
    jobs = [{"id": "confirm_42", "phase": "confirm", "seed": 42, "config": source_config}]
    if not prepare:
        write_jsonl(config["transfer"]["tasks"], official_tasks())
        atomic_json(tmp_path / "human/dataset_metadata.json", metadata())
    calls = []

    def wrapper(mode, output, settings, samples=None):
        assert not any(output.iterdir()), "the isolated wrapper requires a fresh output directory"
        calls.append((mode, str(output)))
        if mode == "prepare":
            write_jsonl(output / "tasks.jsonl", official_tasks())
            atomic_json(output / "dataset_metadata.json", metadata())
            return
        rows = read_jsonl(samples)
        results = {}
        for row in rows:
            status = "pass" if "return 1" in row["solution"] else "fail"
            results.setdefault(row["task_id"], []).append({**row, "base_status": status, "plus_status": status})
        atomic_json(output / "samples_eval_results.json", {"hash": "official-dataset-hash", "eval": results})
        atomic_json(output / "dataset_metadata.json", metadata())
        atomic_json(output / "evaluation_metadata.json", {"evalplus_version": "0.3.1", "dataset": "humaneval",
            "dataset_release": metadata()["datasets"]["HumanEvalPlus"], "dataset_hash": "official-dataset-hash",
            "samples_sha256": file_sha(samples), "task_count": 164, "sample_count": len(rows),
            "protocol": "official-base-and-plus-tests-no-sanitization"})
        (output / "environment.txt").write_text("evalplus==0.3.1\n")

    def generate(model, tokenizer, tasks, output, settings, **kwargs):
        rows = [{"task_id": task["task_id"], "sample_id": index, "completion":
                 "Some text\n```python\n    return 1\n```" if index == 0 else "    return 2\n"}
                for task in tasks for index in range(settings["samples"])]
        write_jsonl(output, rows)
        return rows

    monkeypatch.setattr(transfer, "_image_identity", lambda image: "sha256:fixed-image")
    monkeypatch.setattr(transfer, "_wrapper", wrapper)
    monkeypatch.setattr(transfer, "load_model", lambda *a, **k: (object(), object()))
    monkeypatch.setattr(transfer, "generate_to_file", generate)
    return config, jobs, calls, wrapper


def test_full_official_transfer_and_resume_integrity(tmp_path, monkeypatch):
    config, jobs, calls, _ = setup(tmp_path, monkeypatch, prepare=True)
    result = transfer.run_transfer(config, jobs)
    assert result["task_count"] == 164 and result["samples_per_task"] == 2
    assert {(trial["method"], trial["round"]) for trial in result["trials"]} == {("base", 0), ("plain", 1)}
    assert not result["training_on_humanevalplus"]
    for trial in result["trials"]:
        records = read_jsonl(trial["verified_path"])
        assert len(records) == 328 and sum(row["correct"] for row in records) == 164
        assert all(row["code_extraction"] == "first_fence" for row in records)
        metrics = json.loads(Path(trial["metrics_path"]).read_text())
        assert metrics["aggregate"]["pass_at_k"]["1"]["all_task_mean"] == .5
        assert metrics["evaluation"]["image_identity"] == "sha256:fixed-image"
    count = len(calls)
    assert transfer.run_transfer(config, jobs) == result
    assert len(calls) == count
    Path(result["trials"][0]["verified_path"]).write_text("altered\n")
    with pytest.raises(ValueError, match="output integrity"):
        transfer.run_transfer(config, jobs)


def test_interrupted_eval_keeps_attempt_and_uses_fresh_directory(tmp_path, monkeypatch):
    config, jobs, calls, wrapper = setup(tmp_path, monkeypatch)
    failed = []

    def fail_once(mode, output, settings, samples=None):
        if not failed:
            failed.append(output)
            (output / "partial.json").write_text("partial evaluator data")
            raise RuntimeError("fixture interruption")
        return wrapper(mode, output, settings, samples)

    monkeypatch.setattr(transfer, "_wrapper", fail_once)
    with pytest.raises(RuntimeError, match="interruption"):
        transfer.run_transfer(config, jobs)
    result = transfer.run_transfer(config, jobs)
    assert failed[0].name == "attempt_0001" and (failed[0] / "partial.json").exists()
    first_marker = json.loads(Path(result["trials"][0]["complete_path"]).read_text())
    assert first_marker["official_output"] == "official/attempt_0002"


@pytest.mark.parametrize("case", ["incomplete", "checkpoint", "overlap", "subset", "revision"])
def test_rejects_invalid_sources_and_heldout_data(tmp_path, monkeypatch, case):
    config, jobs, calls, _ = setup(tmp_path, monkeypatch)
    source = Path(jobs[0]["config"]["output_dir"])
    if case == "incomplete":
        (source / "plain/round_1/complete.json").unlink()
        match = "completed source"
    elif case == "checkpoint":
        (source / "plain/round_1/model/model.safetensors").write_bytes(b"corrupt")
        match = "round integrity"
    elif case == "overlap":
        write_jsonl(jobs[0]["config"]["data"]["validation"], [{**official_tasks()[0], "split": "validation"}])
        match = "overlaps"
    elif case == "subset":
        write_jsonl(config["transfer"]["tasks"], official_tasks()[:-1])
        match = "164 tasks"
    else:
        tasks = official_tasks()
        tasks[0]["revision"] = "changed"
        write_jsonl(config["transfer"]["tasks"], tasks)
        match = "provenance"
    with pytest.raises(ValueError, match=match):
        transfer.run_transfer(config, jobs)
    assert calls == []


def test_resume_rejects_changed_generation_config(tmp_path, monkeypatch):
    config, jobs, _, _ = setup(tmp_path, monkeypatch)
    transfer.run_transfer(config, jobs)
    config["generation"]["temperature"] = .9
    with pytest.raises(ValueError, match="changed"):
        transfer.run_transfer(config, jobs)


def test_refuses_mismatched_official_result_provenance(tmp_path, monkeypatch):
    config, jobs, _, wrapper = setup(tmp_path, monkeypatch)

    def wrong_hash(mode, output, settings, samples=None):
        wrapper(mode, output, settings, samples)
        path = output / "evaluation_metadata.json"
        data = json.loads(path.read_text())
        data["samples_sha256"] = "incorrect-source"
        atomic_json(path, data)

    monkeypatch.setattr(transfer, "_wrapper", wrong_hash)
    with pytest.raises(ValueError, match="provenance"):
        transfer.run_transfer(config, jobs)
    assert not list((Path(config["output_dir"]) / "transfer").rglob("complete.json"))


def test_remote_base_requires_resolved_revision(tmp_path, monkeypatch):
    config, jobs, _, _ = setup(tmp_path, monkeypatch)
    source = Path(jobs[0]["config"]["output_dir"])
    jobs[0]["config"]["model"]["name"] = "example/remote-model"
    manifest = json.loads((source / "manifest.json").read_text())
    manifest["config"] = jobs[0]["config"]
    manifest["local_base_fingerprint"] = None
    atomic_json(source / "manifest.json", manifest)
    with pytest.raises(ValueError, match="immutable revision"):
        transfer.run_transfer(config, jobs)


def test_no_confirmation_jobs_no_model_loading(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match="confirmation"):
        transfer.run_transfer({"output_dir": str(tmp_path)}, [])


def test_wrapper_pins_image_and_resource_environment(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setenv("IMPROVING_EVALPLUS_MEMORY_MB", "99999")
    monkeypatch.setattr(transfer.subprocess, "run", lambda command, **kwargs: calls.append((command, kwargs)))
    transfer._wrapper("evaluate", tmp_path / "output", {"image_identity": "sha256:fixed"}, tmp_path / "samples.jsonl")
    command, kwargs = calls[0]
    assert command[:4] == ["bash", str(transfer.WRAPPER), "evaluate", "humaneval"]
    assert kwargs["env"]["IMPROVING_EVALPLUS_IMAGE"] == "sha256:fixed"
    assert kwargs["env"]["IMPROVING_EVALPLUS_MEMORY_MB"] == "4096"


def test_actual_native_generation_with_tiny_frozen_model(tmp_path):
    # Only trusted fixture model generation runs locally; no candidate Python
    # or reference program is executed in this test.
    from helpers import tiny_model_and_tokenizer
    from improving.generation import generate_to_file
    model, tokenizer = tiny_model_and_tokenizer()
    before = {key: tensor.clone() for key, tensor in model.state_dict().items()}
    tasks = [{"task_id": "HumanEval/0", "prompt": "Write a function", "split": "eval", "source": "fixture"}]
    rows = generate_to_file(model, tokenizer, tasks, tmp_path / "raw.jsonl", {"samples": 2, "batch_size": 2,
             "max_new_tokens": 3, "max_prompt_tokens": 16}, stage="humanevalplus_transfer", model_identity="fixture")
    assert len(rows) == 2 and all(row["generation_tokens"] <= 3 for row in rows)
    import torch
    assert all(torch.equal(before[key], tensor) for key, tensor in model.state_dict().items())
