"""Paired inference with crossed training seeds and shared benchmark tasks."""

import copy
import json
import math

import pytest

from improving.metrics import summarize_records
from improving.formal_statistics import compare_seed_summaries


def summary(tasks, n=16):
    """Synthetic metric inputs: (correct count, distinct AST count) per task."""
    rows = []
    for task, (correct, kinds) in tasks.items():
        for sample in range(n):
            rows.append({"task_id": task, "sample_id": sample,
                         "correct": sample < correct,
                         "code": f"def solve():\n return {sample % max(kinds, 1)}",
                         "evaluation_provenance": {
                             "backend": "docker", "code_extraction": "first_fence",
                             "protocol_version": "task-tests-v2", "timeout": 5}})
    value = summarize_records(rows, ks=[1, 4, 8, 16], correct_budget=4,
                              correct_budgets=[4, 8, 16], bootstrap_samples=0,
                              expected_samples={task: n for task in tasks})
    value["protocol"]["evaluation_task_harnesses"] = {task: "sha-" + task for task in tasks}
    return value


def test_identical_correctness_and_exact_diversity_gain():
    before = {42: summary({"a": (4, 1), "b": (4, 1)}),
              43: summary({"a": (4, 1), "b": (4, 1)})}
    after = {42: summary({"a": (4, 4), "b": (4, 4)}),
             43: summary({"a": (4, 4), "b": (4, 4)})}
    result = compare_seed_summaries(before, after, bootstrap_samples=200)
    gain = result["implementation_proxy"]["correct_matched_coverage_at_budgets"]["4"]
    assert gain["mean"] == 3
    assert gain["ci95"] == gain["ci95_family"] == [3, 3]
    assert result["correctness"]["delta"]["mean"] == 0
    assert result["decision"]["success"] is True
    assert result["seed_ids"] == ["42", "43"]
    assert result["pass_at_k"]["16"]["mean"] == 0
    json.dumps(result, allow_nan=False)


def test_correct_matched_effect_uses_same_eligible_questions():
    before = {42: summary({"a": (4, 1), "b": (0, 0)})}
    after = {42: summary({"a": (4, 4), "b": (4, 4)})}
    result = compare_seed_summaries(before, after, bootstrap_samples=200)
    gain = result["implementation_proxy"]["correct_matched_coverage_at_budgets"]["4"]
    assert gain["mean"] == 3
    assert gain["per_seed"]["42"]["eligible_tasks"] == 1
    assert gain["per_seed"]["42"]["unavailable_tasks"] == ["b"]
    assert 0 < gain["bootstrap_null_replicates"] < 200
    assert result["decision"]["success"] is None  # one seed is exploratory
    assert result["decision"]["diversity_superior"] is True


def test_zero_correct_samples_are_null_for_conditional_diversity():
    before = {42: summary({"a": (0, 0)}), 43: summary({"a": (0, 0)})}
    result = compare_seed_summaries(before, before, bootstrap_samples=200)
    gain = result["implementation_proxy"]["correct_matched_coverage_at_budgets"]["4"]
    assert gain["mean"] is gain["ci95"] is gain["ci95_family"] is None
    assert gain["bootstrap_null_replicates"] == 200
    assert result["implementation_proxy"]["coverage_at_k"]["16"]["mean"] == 0
    assert result["decision"]["success"] is None


def test_missing_eligibility_in_one_seed_does_not_silently_remove_seed():
    before = {42: summary({"a": (4, 1)}), 43: summary({"a": (0, 0)})}
    after = {42: summary({"a": (4, 4)}), 43: summary({"a": (0, 0)})}
    result = compare_seed_summaries(before, after, bootstrap_samples=200)
    gain = result["implementation_proxy"]["correct_matched_coverage_at_budgets"]["4"]
    assert gain["mean"] is None
    assert gain["eligible_seeds"] == 1
    assert gain["ci95"] is None
    assert result["decision"]["success"] is None


def test_equal_seed_weights_and_seed_resampling_capture_training_variation():
    before = {42: summary({"a": (0, 0), "b": (0, 0)}),
              43: summary({"a": (16, 1), "b": (16, 1)})}
    after = {42: summary({"a": (16, 1), "b": (16, 1)}),
             43: summary({"a": (0, 0), "b": (0, 0)})}
    result = compare_seed_summaries(before, after, bootstrap_samples=1000)
    delta = result["correctness"]["delta"]
    assert delta["mean"] == 0
    assert delta["ci95"] == [-1, 1]
    assert delta["per_seed"]["42"]["mean"] == 1
    assert delta["per_seed"]["43"]["mean"] == -1
    assert result["correctness"]["noninferior"] is False


def test_task_resample_is_shared_across_seeds_not_independent():
    # All seeds have perfectly correlated task effects. Independent task
    # resampling per seed would wrongly shrink the standard error to 0.5.
    before = {s: summary({"a": (0, 0), "b": (16, 1)}) for s in (42, 43)}
    after = {s: summary({"a": (16, 1), "b": (0, 0)}) for s in (42, 43)}
    result = compare_seed_summaries(before, after, bootstrap_samples=10000)
    assert result["correctness"]["delta"]["bootstrap_standard_error"] == pytest.approx(
        math.sqrt(.5), abs=.015)


def test_reproducible_family_intervals_are_no_narrower_than_pointwise():
    before = {s: summary({"a": (4, 1), "b": (8, 2), "c": (16, 2)}) for s in (42, 43)}
    after = {s: summary({"a": (4, 4), "b": (8, 3), "c": (16, 4)}) for s in (42, 43)}
    result = compare_seed_summaries(before, after, bootstrap_samples=1000, seed=123)
    assert result == compare_seed_summaries(before, after, bootstrap_samples=1000, seed=123)
    delta = result["implementation_proxy"]["correct_matched_coverage_at_budgets"]["4"]
    assert delta["ci95_family"][0] <= delta["ci95"][0]
    assert delta["ci95_family"][1] >= delta["ci95"][1]
    assert result["bootstrap"]["family_size"] == 4


@pytest.mark.parametrize("invalid", [{}, {43: None}])
def test_missing_seed_runs_are_rejected(invalid):
    with pytest.raises(ValueError):
        compare_seed_summaries({42: summary({"a": (4, 1)})}, invalid)


def test_missing_task_or_changed_cross_seed_task_universe_rejected():
    value = summary({"a": (4, 1), "b": (4, 1)})
    with pytest.raises(ValueError, match="task"):
        compare_seed_summaries({42: value}, {42: summary({"a": (4, 1)})})
    with pytest.raises(ValueError, match="task"):
        compare_seed_summaries({42: value, 43: summary({"c": (4, 1)})},
                               {42: value, 43: summary({"c": (4, 1)})})


@pytest.mark.parametrize("field,new", [
    ("evaluation", None), ("evaluation", {"backend": "unsafe"}),
    ("evaluation_task_harnesses", {"a": "changed"}),
    ("sampling", "different"), ("metric_versions", {}),
    ("correct_budgets", [4, 8]), ("ks", [1, 8]),
])
def test_incompatible_protocols_are_rejected(field, new):
    value = summary({"a": (4, 1)})
    changed = copy.deepcopy(value)
    changed["protocol"][field] = new
    with pytest.raises(ValueError, match="protocol|provenance|budget"):
        compare_seed_summaries({42: value}, {42: changed})


def test_missing_shared_evaluation_provenance_rejected():
    value = summary({"a": (4, 1)})
    del value["protocol"]["evaluation"]
    with pytest.raises(ValueError, match="evaluation"):
        compare_seed_summaries({42: value}, {42: value})


def test_different_sample_counts_and_empty_run_are_rejected():
    value = summary({"a": (4, 1)})
    changed = copy.deepcopy(value)
    changed["per_task"]["a"]["sample_count"] = 15
    with pytest.raises(ValueError, match="budget|sample"):
        compare_seed_summaries({42: value}, {42: changed})
    empty = copy.deepcopy(value)
    empty["per_task"] = {}
    with pytest.raises(ValueError, match="empty|task"):
        compare_seed_summaries({42: empty}, {42: empty})


@pytest.mark.parametrize("kwargs", [{"correctness_margin": float("nan")},
    {"family_size": 0}, {"family_size": True}, {"correct_budgets": [8, 16]},
    {"bootstrap_samples": -1}, {"seed": True}])
def test_invalid_inference_settings_rejected(kwargs):
    value = summary({"a": (4, 1)})
    with pytest.raises(ValueError):
        compare_seed_summaries({42: value}, {42: value}, **kwargs)


def test_disabled_bootstrap_cannot_claim_success():
    value = summary({"a": (4, 1)})
    result = compare_seed_summaries({42: value, 43: value}, {42: value, 43: value},
                                    bootstrap_samples=0)
    assert result["correctness"]["noninferior"] is None
    assert result["decision"]["success"] is None
