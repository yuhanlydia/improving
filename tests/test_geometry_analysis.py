"""Geometry reports must respect problems, real ranks, and operator budgets."""

from copy import deepcopy
import json
import math

import pytest
import torch

from improving.geometry import projector
from improving.geometry_analysis import build_bank, operator_family, summarize_geometry


def record(task, sample, basis, *, module="k", values=None):
    basis = torch.as_tensor(basis, dtype=torch.float64)
    rank = basis.shape[1]
    if values is None:
        values = torch.arange(rank, 0, -1, dtype=torch.float64)
    return {"task_id": task, "sample_id": sample,
            "modules": {module: {"basis": basis, "eigenvalues": values}},
            "metadata": {"mask_scope": "program"}}


def test_summary_never_compares_other_tasks_or_modules_and_is_json_safe():
    eye = torch.eye(6, dtype=torch.float64)
    data = [record("a", "0", eye[:, :2]), record("a", "1", eye[:, 1:3]),
            record("a", "2", eye[:, :2], module="v"), record("b", "0", eye[:, :2])]
    report = summarize_geometry(data, ranks=[1, 2, 4])
    json.dumps(report, allow_nan=False)
    assert {row["task_id"] for row in report["pairs"]} == {"a"}
    assert {row["module"] for row in report["pairs"]} == {"k"}
    assert all({row["sample_a"], row["sample_b"]} == {"0", "1"}
               for row in report["pairs"])
    by_rank = {row["rank"]: row for row in report["eligibility"] if row["module"] == "k"}
    assert by_rank[2]["possible_eligible_pairs"] == 1
    assert by_rank[2]["eligible_artifact_count"] == 3
    assert by_rank[4]["evaluated_eligible_pairs"] == 0
    assert by_rank[4]["ineligible_artifact_count"] == 3


def test_macro_mean_weights_problems_equally_despite_different_solution_counts():
    eye = torch.eye(4, dtype=torch.float64)
    # Task A has three identical pairs with overlap 1; B one pair with overlap 0.
    data = [record("a", str(i), eye[:, :1]) for i in range(3)]
    data += [record("b", "0", eye[:, :1]), record("b", "1", eye[:, 1:2])]
    report = summarize_geometry(data, ranks=[1])
    summary = report["macro_aggregates"][0]
    assert summary["pair_count"] == 4
    assert summary["task_count"] == 2
    assert summary["task_macro_mean"]["overlap_min"] == pytest.approx(0.5)


def test_pair_subsampling_keeps_full_denominator_and_is_seeded():
    eye = torch.eye(6, dtype=torch.float64)
    data = [record("task", str(i), eye[:, :2]) for i in range(20)]
    first = summarize_geometry(data, ranks=[2], max_pairs_per_task=7, seed=9)
    assert first == summarize_geometry(list(reversed(data)), ranks=[2], max_pairs_per_task=7, seed=9)
    assert first["eligibility"][0]["possible_eligible_pairs"] == 190
    assert first["eligibility"][0]["evaluated_eligible_pairs"] == 7
    pairs = {(row["sample_a"], row["sample_b"]) for row in first["pairs"]}
    assert len(pairs) == 7


def test_unequal_rank_containment_is_directional_and_effective_rank_is_descriptive():
    eye = torch.eye(4, dtype=torch.float64)
    data = [record("a", "0", eye[:, :2]), record("a", "1", eye[:, :2])]
    report = summarize_geometry(data, ranks=[1, 2])
    unequal = [row for row in report["pairs"] if row["rank_a"] == 1 and row["rank_b"] == 2][0]
    assert unequal["metrics"]["containment_u_in_v"] == 1
    assert unequal["metrics"]["containment_v_in_u"] == 0.5
    assert report["individual"][0]["effective_rank"] == pytest.approx(math.exp(
        -(2 / 3) * math.log(2 / 3) - (1 / 3) * math.log(1 / 3)))
    assert not any("strategy_label_a" in row for row in report["pairs"])


def test_external_strategy_labels_remain_descriptive():
    eye = torch.eye(4, dtype=torch.float64)
    data = [record("a", "0", eye[:, :1]), record("a", "1", eye[:, 1:2])]
    data[0]["metadata"]["strategy_label"] = "sort"
    data[1]["metadata"]["strategy_label"] = "sort"
    report = summarize_geometry(data, ranks=[1])
    assert report["pairs"][0]["same_supplied_strategy_label"] is True
    assert report["pairs"][0]["metrics"]["overlap_min"] == 0


def test_zero_signal_is_reported_without_inventing_basis_vectors():
    report = summarize_geometry([record("a", "0", torch.empty(4, 0))], ranks=[1])
    assert report["individual"][0]["stored_rank"] == 0
    assert report["eligibility"][0]["eligible_artifact_count"] == 0
    json.dumps(report, allow_nan=False)


@pytest.mark.parametrize("change", ["ambient", "duplicate", "padding", "unsorted"])
def test_invalid_coordinate_or_rank_artifacts_fail(change):
    eye = torch.eye(4, dtype=torch.float64)
    data = [record("a", "0", eye[:, :2]), record("a", "1", eye[:, :2])]
    if change == "ambient":
        data[1] = record("b", "1", torch.eye(5)[:, :2])
    elif change == "duplicate":
        data[1]["sample_id"] = "0"
    elif change == "padding":
        data[1]["modules"]["k"]["eigenvalues"][1] = 0
    else:
        data[1]["modules"]["k"]["eigenvalues"] = torch.tensor([1.0, 2.0])
    with pytest.raises(ValueError):
        summarize_geometry(data, ranks=[1])


def test_bank_farthest_first_is_reproducible_excludes_short_rank_and_does_not_mutate():
    eye = torch.eye(6, dtype=torch.float64)
    data = [record("a", "0", eye[:, :2]), record("a", "1", eye[:, :2]),
            record("b", "0", eye[:, 2:4]), record("c", "0", eye[:, 4:6]),
            record("d", "0", eye[:, :1])]
    original = deepcopy(data)
    selected = build_bank(data, rank=2, count=3, seed=4)
    reversed_bank = build_bank(list(reversed(data)), rank=2, count=3, seed=4)
    identities = lambda records: [(r["task_id"], r["sample_id"]) for r in records]
    assert identities(selected) == identities(reversed_bank)
    assert len({tuple(r["modules"]["k"]["basis"].argmax(dim=0).tolist()) for r in selected}) == 3
    assert selected[0]["bank_selection"]["excluded_count"] == 1
    selected[0]["modules"]["k"]["basis"].zero_()
    for before, after in zip(original, data):
        torch.testing.assert_close(before["modules"]["k"]["basis"], after["modules"]["k"]["basis"])
    with pytest.raises(ValueError, match="rank padding"):
        build_bank(data, rank=2, count=5)


def test_bank_distances_are_basis_rotation_invariant():
    generator = torch.Generator().manual_seed(71)
    data = [record(str(i), "0", torch.linalg.qr(torch.randn(8, 2, generator=generator,
                                                          dtype=torch.float64)).Q)
            for i in range(7)]
    rotated = deepcopy(data)
    rotation = torch.tensor([[0.6, -0.8], [0.8, 0.6]], dtype=torch.float64)
    for entry in rotated:
        entry["modules"]["k"]["basis"] @= rotation
    expected = [r["task_id"] for r in build_bank(data, 2, 4, seed=9)]
    assert [r["task_id"] for r in build_bank(rotated, 2, 4, seed=9)] == expected


def test_operator_families_match_perturbation_norm_union_rank_and_rng_isolation():
    eye = torch.eye(6, dtype=torch.float64)
    # One shared direction and one different direction -> union rank 3.
    bank = [record("a", "0", eye[:, :2]), record("a", "1", eye[:, 1:3])]
    before = torch.random.get_rng_state().clone()
    arms = operator_family(bank, strength=0.7, seed=6)
    assert torch.equal(before, torch.random.get_rng_state())
    assert set(arms) == {"single0", "single1", "random_single", "pooled", "span",
                         "matched_random_span", "interpolate_0.25", "interpolate_0.5", "interpolate_0.75"}
    identity = torch.eye(6, dtype=torch.float64)
    for name, modules in arms.items():
        operator = modules["k"]
        assert float(torch.linalg.norm(operator - identity)) == pytest.approx(0.7)
        expected_rank = 3 if name in {"span", "matched_random_span"} else 2
        assert torch.linalg.matrix_rank(operator - identity, atol=1e-10) == expected_rank
        assert torch.linalg.eigvalsh(operator).min() >= 1 - 1e-12
    second = operator_family(bank, strength=0.7, seed=6)
    torch.testing.assert_close(arms["random_single"]["k"], second["random_single"]["k"])


def test_pooled_arm_is_top_rank_of_mean_projector_and_not_projector_sum():
    eye = torch.eye(5, dtype=torch.float64)
    bank = [record("a", "0", eye[:, :1]), record("a", "1", eye[:, :1]),
            record("b", "0", eye[:, 1:2])]
    pooled = operator_family(bank, strength=1)["pooled"]["k"] - torch.eye(5)
    torch.testing.assert_close(pooled, projector(eye[:, :1]))


def test_operator_family_requires_matching_module_sets_ranks_and_valid_fractions():
    eye = torch.eye(5, dtype=torch.float64)
    one = record("a", "0", eye[:, :1])
    with pytest.raises(ValueError, match="module set"):
        operator_family([one, record("b", "0", eye[:, :1], module="v")])
    with pytest.raises(ValueError, match="common positive"):
        operator_family([one, record("b", "0", eye[:, :2])])
    with pytest.raises(ValueError, match="distinct"):
        operator_family([one], interpolation=[0.5, 0.5])
    assert set(operator_family([one])) == {"single0", "pooled", "random_single"}
