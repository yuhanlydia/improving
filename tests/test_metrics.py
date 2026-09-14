"""Analytic, enumerated, and missing-data checks for evaluation statistics."""

import copy
import itertools
import json
import math

import pytest
from improving import metrics

from improving.metrics import (
    compare_summaries,
    coverage_at_k,
    implementation_proxy,
    pass_at_k,
    strategy_retention,
    summarize_records,
)


def record(task, sample, correct, strategy=None, code="def solve(x):\n return x"):
    result = dict(task_id=task, sample_id=sample, correct=correct,
                  completion=code, code=code, status="passed" if correct else "failed")
    if strategy is not None:
        result["strategy_id"] = strategy
    return result


def summary(records, **kwargs):
    return summarize_records(records, ks=[1, 2, 4], correct_budget=2,
                             bootstrap_samples=200, **kwargs)


@pytest.mark.parametrize("n,c,k,want", [(4, 2, 2, 5/6), (4, 0, 4, 0),
                                       (4, 4, 1, 1), (0, 0, 0, 0)])
def test_pass_at_k_analytic(n, c, k, want):
    assert pass_at_k(n, c, k) == pytest.approx(want)


def test_estimators_match_exhaustive_sampling_with_wrong_draws():
    population = ["a", "a", "b", None, None]
    for k in range(6):
        draws = list(itertools.combinations(population, k))
        exact_pass = sum(any(label is not None for label in draw) for draw in draws) / len(draws)
        exact_coverage = sum(len(set(draw) - {None}) for draw in draws) / len(draws)
        assert pass_at_k(5, 3, k) == pytest.approx(exact_pass)
        assert coverage_at_k({"a": 2, "b": 1}, 5, k) == pytest.approx(exact_coverage)
    assert coverage_at_k([2, 1], 5, 2) == pytest.approx(1.1)


def test_pass_at_k_is_stable_for_extreme_valid_integer_counts():
    assert pass_at_k(10**20, 1, 1) == pytest.approx(1e-20, rel=1e-14, abs=0)
    assert pass_at_k(10**20, 1, 10**20 - 1) == 1.0


def test_correct_count_matching_is_sampling_from_corrects_only():
    rows = [record("a", 0, True, "a"), record("a", 1, True, "a"),
            record("a", 2, True, "b"), record("a", 3, False)]
    result = summary(rows)
    strategy = result["per_task"]["a"]["strategy"]
    # Correct-only size-two draws: aa, ab, ab -> mean distinct count 5/3.
    assert strategy["correct_matched_coverage"] == pytest.approx(5/3)
    # All-sample draws: aa, ab, aw, ab, aw, bw -> mean distinct count 8/6.
    assert strategy["coverage_at_k"]["2"] == pytest.approx(4/3)


@pytest.mark.parametrize("args", [(3, 1, 4), (3, 4, 1), (3, -1, 1),
                                  (3, 1, -1), (3.0, 1, 1), (3, True, 1)])
def test_pass_rejects_invalid_counts_and_budgets(args):
    with pytest.raises(ValueError):
        pass_at_k(*args)


@pytest.mark.parametrize("counts,total,k", [([2, 2], 3, 1), ([-1], 3, 1),
                                           ([True], 3, 1), ([1], 3, 4)])
def test_coverage_rejects_invalid_counts(counts, total, k):
    with pytest.raises(ValueError):
        coverage_at_k(counts, total, k)


def test_proxy_normalizes_local_names_and_preserves_operations():
    a = "def solve(xs):\n total = 0\n for item in xs:\n  total += item\n return total"
    b = "def solve(values):\n '''a docstring'''\n acc=0\n for value in values:\n  acc+=value\n return acc"
    assert implementation_proxy(a) == implementation_proxy(b)
    assert implementation_proxy(a) != implementation_proxy(b.replace("acc+=value", "acc-=value"))
    assert implementation_proxy("def broken(") is None
    assert implementation_proxy("def solve(x):\n return sorted(x)") != implementation_proxy("def solve(x):\n return reversed(x)")


def test_proxy_does_not_merge_shadowed_builtin_with_global_builtin():
    assert implementation_proxy("def solve(sum, x):\n return sum(x)") != implementation_proxy("def solve(other, x):\n return sum(x)")
    # Nested scopes and comprehensions are preserved conservatively, without
    # conflating distinct lexical bindings.
    a = "def solve(x):\n def inner(y):\n  return x+y\n return inner(x)"
    b = "def solve(x):\n def inner(y):\n  return y+y\n return inner(x)"
    assert implementation_proxy(a) != implementation_proxy(b)


def test_control_flow_proxy_tracks_algorithmic_skeleton_not_local_names():
    loop_a = "def solve(xs):\n for x in xs:\n  if x: return x"
    loop_b = "def solve(values):\n for value in values:\n  if value: return value"
    branch = "def solve(xs):\n if xs: return xs[0]"
    assert metrics.control_flow_proxy(loop_a) == metrics.control_flow_proxy(loop_b)
    assert metrics.control_flow_proxy(loop_a) != metrics.control_flow_proxy(branch)


def test_summary_reports_exact_control_flow_balance_and_multiple_correct_budgets():
    codes = ["x=1", "x=1", "x=2", "for x in []:\n pass"]
    rows = [record("a", i, True, code=code) for i, code in enumerate(codes)]
    result = summarize_records(rows, ks=[1, 4], correct_budget=2,
                               correct_budgets=[2, 4, 8], bootstrap_samples=0)
    exact = result["per_task"]["a"]["exact_program"]
    assert exact["unique_label_count"] == 3
    assert exact["unique_fraction"] == pytest.approx(3 / 4)
    assert exact["effective_label_count"] == pytest.approx(math.exp(-(0.5 * math.log(0.5) + 2 * 0.25 * math.log(0.25))))
    assert exact["simpson_diversity"] == pytest.approx(5 / 6)
    assert exact["correct_matched_coverage_at_budgets"] == {
        "2": pytest.approx(11 / 6), "4": pytest.approx(3), "8": None}
    control = result["per_task"]["a"]["control_flow_proxy"]
    assert control["unique_label_count"] == 2
    assert result["per_task"]["a"]["lexical"]["pairwise_token_jaccard_distance"] == pytest.approx(11 / 18)
    assert result["protocol"]["correct_budgets"] == [2, 4, 8]
    assert result["protocol"]["metric_versions"] == {
        "implementation_proxy": "python-ast-conservative-locals-v1",
        "exact_program": "stripped-source-sha256-v1",
        "control_flow_proxy": "python-ast-control-flow-v1",
        "lexical": "python-token-set-jaccard-v1",
    }


def test_summary_includes_zero_correct_tasks_and_task_macro_denominator():
    records = [record("a", 0, True, "loop"), record("a", 1, True, "recursion"),
               record("a", 2, False), record("a", 3, False),
               *[record("b", i, False) for i in range(4)]]
    before = copy.deepcopy(records)
    result = summary(records, expected_samples=4)
    assert records == before
    assert result["aggregate"]["pass_at_k"]["1"]["mean"] == pytest.approx(.25)
    assert result["aggregate"]["strategy"]["coverage_at_k"]["2"]["mean"] == pytest.approx(.5)
    assert result["per_task"]["b"]["strategy"]["coverage_at_k"]["4"] == 0
    assert result["per_task"]["b"]["strategy"]["correct_label_entropy"] is None
    matched = result["aggregate"]["strategy"]["correct_matched_coverage"]
    assert matched["mean"] == 2
    assert matched["eligible_tasks"] == 1
    assert matched["unavailable_tasks"] == ["b"]
    assert result["per_task"]["a"]["strategy"]["correct_label_entropy"] == pytest.approx(math.log(2))
    json.dumps(result, allow_nan=False)


def test_strategy_metrics_unavailable_for_partially_annotated_corrects():
    result = summary([record("a", 0, True, "loop"), record("a", 1, True)])
    strategy = result["per_task"]["a"]["strategy"]
    assert strategy["status"] == "incomplete"
    assert strategy["coverage_at_k"]["1"] is None
    assert strategy["correct_label_entropy"] is None
    assert strategy["correct_matched_coverage"] is None
    assert result["per_task"]["a"]["implementation_proxy"]["coverage_at_k"]["1"] == 1
    assert result["aggregate"]["strategy"]["coverage_at_k"]["1"]["eligible_tasks"] == 0


def test_unparseable_correct_program_makes_proxy_explicitly_unavailable():
    result = summary([record("a", 0, True, "loop", "not valid python @")])
    assert result["per_task"]["a"]["implementation_proxy"]["status"] == "incomplete"
    assert result["per_task"]["a"]["implementation_proxy"]["coverage_at_k"]["1"] is None
    assert result["per_task"]["a"]["strategy"]["coverage_at_k"]["1"] == 1


def test_insufficient_draw_budgets_are_null_with_eligibility_counts():
    result = summary([record("a", 0, True), *[record("b", i, False) for i in range(4)]])
    assert result["per_task"]["a"]["pass_at_k"]["2"] is None
    aggregate = result["aggregate"]["pass_at_k"]["2"]
    assert aggregate["eligible_tasks"] == 1
    assert aggregate["total_tasks"] == 2
    assert aggregate["unavailable_tasks"] == ["a"]
    assert aggregate["all_task_mean"] is None


def test_macro_weights_tasks_equally_when_sample_counts_differ():
    result = summary([*[record("a", i, True) for i in range(8)], record("b", 0, False)])
    assert result["aggregate"]["correct_fraction"]["mean"] == .5
    assert result["aggregate"]["pass_at_k"]["1"]["all_task_mean"] == .5


@pytest.mark.parametrize("records", [
    [record("a", 0, True), record("a", 0, False)],
    [dict(record("a", 0, True), correct=1)],
    [dict(record("a", 0, True), correct="false")],
    [dict(record("a", 0, True), sample_id=True)],
])
def test_summary_rejects_duplicate_keys_and_coerced_booleans(records):
    with pytest.raises(ValueError):
        summary(records)


def test_expected_samples_rejects_missing_tasks_and_incomplete_groups():
    records = [record("a", 0, True)]
    with pytest.raises(ValueError):
        summary(records, expected_samples=2)
    with pytest.raises(ValueError):
        summary(records, expected_samples={"a": 1, "b": 1})
    zero = summary([], expected_samples={"empty": 0})
    assert zero["per_task"]["empty"]["sample_count"] == 0
    assert zero["per_task"]["empty"]["pass_at_k"]["1"] is None


def test_task_bootstrap_is_reproducible_and_uses_tasks_not_samples():
    records = [*[record("a", i, True, "one") for i in range(4)],
               *[record("b", i, False) for i in range(4)]]
    a = summary(records, seed=19)
    b = summary(list(reversed(records)), seed=19)
    assert a == b
    assert a["aggregate"]["correct_fraction"]["ci95"] == [0., 1.]


def test_summary_preserves_one_explicit_evaluation_protocol_and_rejects_mixed_protocols():
    protocol = {"backend": "docker", "protocol_version": "task-tests-v1",
                "code_extraction": "first_fence", "task_tests_sha256": "abc"}
    rows = [dict(record("a", 0, True), evaluation_provenance=protocol),
            dict(record("a", 1, False), evaluation_provenance=protocol)]
    result = summary(rows)
    assert result["protocol"]["evaluation"] == protocol
    rows[1]["evaluation_provenance"] = {**protocol, "code_extraction": "strict"}
    with pytest.raises(ValueError, match="evaluation provenance"):
        summary(rows)


def test_comparison_checks_noninferiority_with_paired_task_deltas():
    previous = summary([record("a", 0, False), record("a", 1, False),
                        record("b", 0, True, "a"), record("b", 1, False)])
    current = summary([record("a", 0, True, "a"), record("a", 1, False),
                       record("b", 0, True, "a"), record("b", 1, True, "b")])
    comparison = compare_summaries(previous, current, correctness_margin=.01,
                                   bootstrap_samples=200, seed=9)
    assert comparison["correctness"]["delta"]["mean"] == .5
    assert comparison["correctness"]["delta"]["ci95"] == [.5, .5]
    assert comparison["correctness"]["noninferior"] is True
    assert comparison["pass_at_k"]["4"]["mean"] is None
    worse = compare_summaries(current, previous, correctness_margin=.01)
    assert worse["correctness"]["noninferior"] is False


def test_comparison_rejects_different_task_universes_or_budgets():
    a = summary([record("a", 0, True)])
    with pytest.raises(ValueError):
        compare_summaries(a, summary([record("b", 0, True)]))
    with pytest.raises(ValueError):
        compare_summaries(a, summary([record("a", 0, True), record("a", 1, False)]))
    other = copy.deepcopy(a)
    other["protocol"]["ks"] = [1]
    with pytest.raises(ValueError):
        compare_summaries(a, other)
    other = copy.deepcopy(a)
    other["protocol"]["metric_versions"]["lexical"] = "changed"
    with pytest.raises(ValueError, match="metric_versions"):
        compare_summaries(a, other)


def test_cross_round_retention_uses_supplied_labels_and_reports_absence_caveat():
    previous = summary([record("a", 0, True, "loop"), record("a", 1, True, "recursion")])
    current = summary([record("a", 0, True, "loop"), record("a", 1, True, "dp")])
    result = strategy_retention(previous, current)
    assert result["per_task"]["a"]["retained_labels"] == ["loop"]
    assert result["per_task"]["a"]["unobserved_previous_labels"] == ["recursion"]
    assert result["per_task"]["a"]["newly_observed_labels"] == ["dp"]
    assert result["per_task"]["a"]["retention_fraction"] == .5
    assert "eradication" in result["caveat"]
    partial = summary([record("a", 0, True), record("a", 1, True, "loop")])
    assert strategy_retention(previous, partial)["per_task"]["a"]["retention_fraction"] is None
