"""Reports use real metric summaries and refuse incomparable protocols."""

import copy
import json

import pytest

from improving.metrics import summarize_records
from improving.reporting import annotate_records, build_report


def records(correct=(True, False), labels=True):
    return [{"task_id": "task/a", "sample_id": i, "correct": value,
             "code": "def solve(x):\n return x", "completion": "def solve(x):\n return x",
             **({"strategy_id": "identity"} if labels and value else {})}
            for i, value in enumerate(correct)]


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


def make_run(path, methods=("spectral_soft", "spd_hard"), rounds=1):
    write_json(path / "manifest.json", {"config": {
        "methods": list(methods), "rounds": rounds, "seed": 13,
        "evaluation": {"bootstrap_samples": 100, "correctness_margin": .02},
        "diagnostics": {"evaluate_generation_policy": True},
    }})


def write_stage(root, method="base", round_index=0, stage="evaluation", rows=None,
                evaluation=None, sampling=None, ks=(1, 2, 4)):
    directory = root / "base" if method == "base" else root / method / f"round_{round_index}"
    result = summarize_records(records() if rows is None else rows, ks=ks,
                               correct_budget=2, bootstrap_samples=50)
    result["protocol"]["evaluation"] = evaluation or {"backend": "docker", "task_tests_sha256": "same-tests"}
    write_json(directory / f"{stage}.metrics.json", result)
    protocol = {"prompts": "same-prompts", "settings": {"samples": 2, "temperature": .8},
                "method": method, "model_identity": f"{method}-model", "round": round_index,
                "stage": "evaluation", "seed": 13, "format": 1}
    if sampling:
        protocol.update(sampling)
    write_json(directory / f"{stage}.jsonl.budget.json", {
        "protocol": protocol, "samples": len(records() if rows is None else rows),
        "tasks": 1, "generation_tokens": 15, "prompt_tokens": 30,
    })
    return directory


def test_annotation_strict_join_preserves_raw_records_and_marks_missing_labels():
    original = records((True, True, False), labels=False)
    before = copy.deepcopy(original)
    annotated = annotate_records(original, [{"task_id": "task/a", "sample_id": 0, "strategy_id": "loop"}])
    assert original == before
    assert len(annotated) == 3
    assert annotated[0]["strategy_id"] == "loop"
    assert annotated[1]["strategy_id"] is None
    assert annotated[1]["strategy_annotation_status"] == "missing"
    assert annotated[2]["strategy_annotation_status"] == "not_applicable"
    assert all(a["completion"] == b["completion"] for a, b in zip(original, annotated))
    summary = summarize_records(annotated, ks=[1], bootstrap_samples=0)
    assert summary["per_task"]["task/a"]["strategy"]["status"] == "incomplete"


@pytest.mark.parametrize("annotations", [
    [{"task_id": "unknown", "sample_id": 0, "strategy_id": "x"}],
    [{"task_id": "task/a", "sample_id": 0, "strategy_id": "x"}] * 2,
    [{"task_id": "task/a", "sample_id": 1, "strategy_id": "x"}],
    [{"task_id": "task/a", "sample_id": True, "strategy_id": "x"}],
    [{"task_id": "task/a", "sample_id": 0, "strategy_id": 7}],
])
def test_annotation_rejects_unknown_duplicate_and_incorrect_positive_labels(annotations):
    with pytest.raises(ValueError):
        annotate_records(records(labels=False), annotations)


def test_annotation_rejects_duplicate_completions_and_truthy_correctness():
    with pytest.raises(ValueError):
        annotate_records([records()[0], records()[0]], [])
    with pytest.raises(ValueError):
        annotate_records([dict(records()[0], correct="true")], [])


def test_report_keeps_missing_results_pending_without_fabricated_zeros(tmp_path):
    make_run(tmp_path, methods=("spectral_soft",), rounds=2)
    result = build_report(tmp_path)
    assert result["status"] == "pending"
    assert len(result["stages"]) == 5
    assert all(stage["status"] == "pending_metrics" for stage in result["stages"])
    assert all(stage["metrics"] is None for stage in result["stages"])
    assert all(comparison["status"] != "available" for comparison in result["comparisons"])
    assert (tmp_path / "report.json").exists()
    markdown = (tmp_path / "report.md").read_text()
    assert "pending" in markdown.lower()
    assert "0.000" not in markdown
    assert json.loads((tmp_path / "report.json").read_text()) == result


def test_report_summarizes_both_stages_and_retains_budget_training_metadata(tmp_path):
    make_run(tmp_path)
    write_stage(tmp_path)
    for method in ("spectral_soft", "spd_hard"):
        directory = write_stage(tmp_path, method, 1)
        write_stage(tmp_path, method, 1, "generation_policy")
        write_json(directory / "model" / "training_stats.json", {"optimizer_steps": 3, "training_tokens": 123})
        write_json(directory / "train.jsonl.budget.json", {"samples": 7, "generation_tokens": 77})
    result = build_report(tmp_path)
    assert result["status"] == "complete"
    assert len(result["stages"]) == 5
    stage = next(s for s in result["stages"] if s["id"] == "spectral_soft/round_1/evaluation")
    assert stage["metrics"]["pass_at_1"]["mean"] == .5
    assert stage["metrics"]["pass_at_1"]["eligible_fraction"] == 1
    assert stage["metrics"]["implementation_coverage_at_k"]["4"]["coverage_status"] == "unavailable"
    assert stage["metrics"]["exact_program_unique_fraction"]["mean"] == 1
    assert stage["metrics"]["implementation_simpson_diversity"]["mean"] is None
    assert stage["metrics"]["control_flow_effective_label_count"]["mean"] == 1
    assert stage["metrics"]["lexical_pairwise_token_jaccard_distance"]["mean"] is None
    assert set(stage["metrics"]["implementation_correct_matched_coverage_at_budgets"]) == {"2", "4", "8"}
    assert stage["budget"]["generation_tokens"] == 15
    assert stage["protocol"]["sampling"]["model_identity"] == "spectral_soft-model"
    round_data = result["rounds"]["spectral_soft/round_1"]
    assert round_data["training_stats"]["optimizer_steps"] == 3
    assert round_data["training_budget"]["samples"] == 7
    compared = [c for c in result["comparisons"] if c["candidate"] == stage["id"]]
    assert {c["reference"] for c in compared} == {"base/evaluation", "spd_hard/round_1/evaluation"}
    assert all(c["status"] == "available" for c in compared)
    assert all(c["result"]["correctness"]["margin"] == .02 for c in compared)
    assert all(c["result"]["correctness"]["delta"]["ci95"] == [0, 0] for c in compared)


@pytest.mark.parametrize("mismatch", ["sampling", "evaluation"])
def test_report_refuses_comparison_when_protocol_differs(tmp_path, mismatch):
    make_run(tmp_path, methods=("spectral_soft",))
    write_stage(tmp_path)
    kwargs = ({"sampling": {"settings": {"samples": 2, "temperature": 1.5}}}
              if mismatch == "sampling" else {"evaluation": {"backend": "local", "task_tests_sha256": "same-tests"}})
    write_stage(tmp_path, "spectral_soft", 1, **kwargs)
    result = build_report(tmp_path)
    comparison = next(c for c in result["comparisons"] if c["candidate"].endswith("/evaluation") and c["reference"] == "base/evaluation")
    assert comparison["status"] == "incomparable"
    assert mismatch in comparison["reason"]
    assert comparison["result"] is None


def test_report_refuses_missing_evaluation_provenance_even_with_results(tmp_path):
    make_run(tmp_path, methods=("spectral_soft",))
    base = write_stage(tmp_path)
    write_stage(tmp_path, "spectral_soft", 1)
    path = base / "evaluation.metrics.json"
    metrics = json.loads(path.read_text())
    del metrics["protocol"]["evaluation"]
    write_json(path, metrics)
    result = build_report(tmp_path)
    comparison = next(c for c in result["comparisons"] if c["candidate"].endswith("/evaluation") and c["reference"] == "base/evaluation")
    assert comparison["status"] == "incomparable"
    assert "evaluation" in comparison["reason"]


def test_report_labels_partial_coverage_and_never_substitutes_ast_strategy_labels(tmp_path):
    make_run(tmp_path, methods=())
    rows = records((True, False) * 8, labels=False) + [
        dict(row, task_id="task/b") for row in records((True, False) * 8)]
    write_stage(tmp_path, rows=rows, ks=[1, 16])
    result = build_report(tmp_path)
    metrics = result["stages"][0]["metrics"]
    semantic = metrics["strategy_coverage_at_k"]["1"]
    assert semantic["eligible_tasks"] == 1
    assert semantic["total_tasks"] == 2
    assert semantic["eligible_fraction"] == .5
    assert semantic["coverage_status"] == "partial"
    assert semantic["all_task_mean"] is None
    assert metrics["implementation_coverage_at_k"]["1"]["eligible_fraction"] == 1
    assert metrics["strategy_coverage_at_k"]["16"]["coverage_status"] == "partial"
    assert "partial" in (tmp_path / "report.md").read_text()


def test_report_discovers_existing_rounds_without_manifest_and_supports_output_path(tmp_path):
    write_stage(tmp_path, "plain", 3)
    output = tmp_path / "exports" / "overview.json"
    report = build_report(tmp_path, output_path=output)
    assert any(stage["id"] == "plain/round_3/evaluation" for stage in report["stages"])
    assert output.exists()
    assert output.with_suffix(".md").exists()


def test_main_report_uses_16_and_64_and_preserves_pass1_in_appendix_and_json(tmp_path):
    make_run(tmp_path, methods=("spectral_soft",))
    for method, index in [("base", 0), ("spectral_soft", 1)]:
        write_stage(tmp_path, method, index, rows=records((True,) * 64), ks=[1, 4, 16, 64])
    result = build_report(tmp_path)
    markdown = (tmp_path / "report.md").read_text()
    main, appendix = markdown.split("## Appendix: Pass@1 and correctness noninferiority")
    assert "| Pass@16 | Pass@64 |" in main
    assert "Pass@1 |" not in main
    assert "Noninferiority" not in main
    assert "| ΔPass@16 | ΔPass@64 |" in main
    coverage = main.split("## Correct implementation richness")[1].split("## Coverage at a fixed")[0]
    assert "| base/evaluation | 16 | 1.000" in coverage
    assert "| base/evaluation | 64 | 1.000" in coverage
    assert "| base/evaluation | 1 |" not in coverage
    assert "| base/evaluation | 4 |" not in coverage
    assert "Pass@1" in appendix and "Noninferiority" in appendix
    assert result["stages"][0]["metrics"]["pass_at_1"]["mean"] == 1
    assert set(result["stages"][0]["metrics"]["pass_at_k"]) == {"1", "4", "16", "64"}
    assert any(c["result"] and "noninferior" in c["result"]["correctness"] for c in result["comparisons"])


def test_main_report_keeps_missing_64_pending_and_shows_all_fixed_correct_budgets(tmp_path):
    make_run(tmp_path, methods=())
    write_stage(tmp_path, rows=records((True,) * 16), ks=[1, 16])
    build_report(tmp_path)
    markdown = (tmp_path / "report.md").read_text()
    correctness = markdown.split("## Correct implementation richness")[0]
    assert "| Pass@16 | Pass@64 |" in correctness
    assert "| pending | 16 |" in correctness
    coverage = markdown.split("## Correct implementation richness")[1].split("## Coverage at a fixed")[0]
    assert "| base/evaluation | 64 | pending | pending |" in coverage
    fixed = markdown.split("## Coverage at a fixed")[1].split("## Paired comparisons")[0]
    for budget in (2, 4, 8):
        assert f"| base/evaluation | {budget} |" in fixed
