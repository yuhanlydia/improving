"""Formal report decisions must pair the registered phase, round and seed."""

import json
from pathlib import Path

import pytest

from improving import formal_reporting
from improving.metrics import summarize_records


SEEDS = [42, 43, 44, 45, 46]


def summary(kinds):
    records = [{"task_id": task, "sample_id": sample, "correct": sample < 4,
                "code": f"def solve():\n return {sample % kinds}",
                "evaluation_provenance": {"backend": "docker", "protocol_version": "task-tests-v2",
                                          "code_extraction": "first_fence"}}
               for task in ("a", "b") for sample in range(16)]
    result = summarize_records(records, ks=(1, 4, 8, 16), correct_budget=4,
                               correct_budgets=(4, 8, 16), bootstrap_samples=0,
                               expected_samples={"a": 16, "b": 16})
    result["protocol"]["evaluation_task_harnesses"] = {"a": "sha-a", "b": "sha-b"}
    return result


def entry(tmp_path, phase, stage, method, seed, *, round=1, kinds=None, signature="native"):
    value = summary(kinds if kinds is not None else (4 if method == "spectral_soft" else 1))
    path = tmp_path / f"{phase}-{stage}-{method}-{seed}-{round}.metrics.json"
    path.write_text(json.dumps(value))
    return {"phase": phase, "stage": stage, "method": method, "seed": seed,
            "round": round, "summary": value, "sampling_signature": signature,
            "path": str(path), "verified_path": str(path.with_suffix(".verified.jsonl"))}


def confirmation(tmp_path):
    return [entry(tmp_path, "confirm", "evaluation", method, seed)
            for method in ("plain", "spd_hard", "spectral_soft", "ssd") for seed in SEEDS]


def report(tmp_path, monkeypatch, entries):
    manifest = tmp_path / "suite.json"
    manifest.write_text(json.dumps({
        "identity": "test-suite", "jobs": [], "budget": {"candidate_programs": 0},
        "config": {"output_dir": str(tmp_path), "data_seed": 42,
                   "formal": {"confirm_seeds": SEEDS, "mechanism_seeds": SEEDS[:3],
                              "retention_seeds": SEEDS[:3], "retention_rounds": 3,
                              "mechanism_methods": ["matched_hard", "random_spectrum", "permuted_spectrum"],
                              "bootstrap_samples": 200}}}))
    monkeypatch.setattr(formal_reporting, "collect_entries", lambda suite: entries)
    status = formal_reporting.build_formal_report(manifest)
    return status, json.loads((tmp_path / "report/summary.json").read_text())


def comparison(result, phase, control, *, stage="evaluation", round=1):
    return next(item for item in result["comparisons"] if (
        item["phase"], item["stage"], item["round"], item["reference"]
    ) == (phase, stage, round, control))


def test_five_seed_primary_requires_both_registered_controls(tmp_path, monkeypatch):
    status, result = report(tmp_path, monkeypatch, confirmation(tmp_path))
    assert status["primary_decision"] == result["primary_decision"] == "supported"
    primary = [item for item in result["comparisons"] if item["primary"]]
    assert {item["reference"] for item in primary} == {"plain", "spd_hard"}
    assert all(item["stage"] == "evaluation" for item in primary)
    assert all(item["statistics"]["seed_count"] == 5 for item in primary)
    assert all(item["statistics"]["bootstrap"]["family_size"] == 4 for item in primary)
    assert all(item["statistics"]["decision"]["success"] is True for item in primary)
    for filename in ("summary.md", "summary.json", "per_seed.csv", "per_task.jsonl", "comparisons.csv"):
        assert (tmp_path / "report" / filename).exists()


def test_missing_one_seed_leaves_primary_pending(tmp_path, monkeypatch):
    entries = [item for item in confirmation(tmp_path)
               if not (item["method"] == "spd_hard" and item["seed"] == 46)]
    _, result = report(tmp_path, monkeypatch, entries)
    assert result["primary_decision"] == "pending"
    missing = comparison(result, "confirm", "spd_hard")
    assert missing["status"] == "pending"
    assert missing["missing_seeds"] == [46]
    assert "statistics" not in missing


def test_generation_ssd_is_incomparable_but_post_lora_ssd_is_comparable(tmp_path, monkeypatch):
    entries = confirmation(tmp_path)
    entries += [entry(tmp_path, "confirm", "generation_policy", method, seed,
                      signature="hot" if method == "ssd" else "native")
                for method in ("plain", "spd_hard", "spectral_soft", "ssd") for seed in SEEDS]
    _, result = report(tmp_path, monkeypatch, entries)
    assert comparison(result, "confirm", "ssd", stage="generation_policy")["status"] == "incomparable_decoding"
    assert comparison(result, "confirm", "ssd")["status"] == "completed"
    assert result["primary_decision"] == "supported"


def test_mechanism_uses_confirmation_candidate_and_only_mechanism_seed_subset(tmp_path, monkeypatch):
    entries = confirmation(tmp_path)
    entries += [entry(tmp_path, "mechanism", "evaluation", method, seed)
                for method in ("matched_hard", "random_spectrum", "permuted_spectrum") for seed in SEEDS[:3]]
    # This decoy would erase the effect if the wrong phase supplied the candidate.
    entries += [entry(tmp_path, "mechanism", "evaluation", "spectral_soft", seed, kinds=1)
                for seed in SEEDS[:3]]
    _, result = report(tmp_path, monkeypatch, entries)
    for control in ("matched_hard", "random_spectrum", "permuted_spectrum"):
        item = comparison(result, "mechanism", control)
        assert item["status"] == "completed"
        statistics = item["statistics"]
        assert statistics["seed_ids"] == ["42", "43", "44"]
        assert statistics["bootstrap"]["family_size"] == 6
        assert statistics["implementation_proxy"]["correct_matched_coverage_at_budgets"]["4"]["mean"] == 3


def test_retention_pairs_each_round_and_accounts_for_all_rounds(tmp_path, monkeypatch):
    entries = confirmation(tmp_path)
    entries += [entry(tmp_path, "retention", "evaluation", method, seed, round=r,
                      kinds=r + 1 if method == "spectral_soft" else 1)
                for r in (1, 2, 3) for method in ("plain", "spd_hard", "spectral_soft") for seed in SEEDS[:3]]
    _, result = report(tmp_path, monkeypatch, entries)
    for r in (1, 2, 3):
        for control in ("plain", "spd_hard"):
            item = comparison(result, "retention", control, round=r)
            assert item["status"] == "completed"
            statistics = item["statistics"]
            assert statistics["bootstrap"]["family_size"] == 12
            assert statistics["implementation_proxy"]["correct_matched_coverage_at_budgets"]["4"]["mean"] == r


def test_transfer_base_uses_base_round_zero_evaluation(tmp_path, monkeypatch):
    entries = confirmation(tmp_path)
    entries += [entry(tmp_path, "transfer", "evaluation", method, seed,
                      round=0 if method == "base" else 1)
                for method in ("base", "plain", "spd_hard", "spectral_soft", "ssd") for seed in SEEDS]
    _, result = report(tmp_path, monkeypatch, entries)
    item = comparison(result, "transfer", "base")
    assert item["status"] == "completed"
    assert item["statistics"]["bootstrap"]["family_size"] == 8


def test_duplicate_identity_rejected(tmp_path, monkeypatch):
    entries = confirmation(tmp_path)
    with pytest.raises(ValueError, match="Duplicate"):
        report(tmp_path, monkeypatch, [*entries, entries[0]])


def test_primary_not_supported_if_one_registered_control_has_no_gain(tmp_path, monkeypatch):
    entries = confirmation(tmp_path)
    entries = [entry(tmp_path, "confirm", "evaluation", "spd_hard", item["seed"], kinds=4)
               if item["method"] == "spd_hard" else item for item in entries]
    _, result = report(tmp_path, monkeypatch, entries)
    assert result["primary_decision"] == "not_supported"
