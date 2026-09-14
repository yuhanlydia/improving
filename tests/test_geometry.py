"""Geometry checks use analytic subspaces, not implementation-shaped mocks."""

import json
import math

import pytest
import torch

from improving.geometry import (
    basis_from_gradients,
    compare_subspaces,
    concatenate_span,
    grassmann_interpolate,
    normalized_operator,
    projector,
)


def eye(d):
    return torch.eye(d, dtype=torch.float64)


def test_gradient_spectrum_keeps_rank_grid_and_reports_energy_rank():
    gradients = torch.diag(torch.tensor([4.0, 2.0, 1.0, 0.0]))
    result = basis_from_gradients(gradients, max_rank=4, energy=0.9, method="exact")
    assert result["basis"].shape == (4, 3)
    assert result["effective_rank"] == 2
    assert result["total_energy"] == pytest.approx(21 / 4)
    assert result["captured_energy"] == pytest.approx(1)
    assert not result["rank_capped"]
    torch.testing.assert_close(result["eigenvalues"], torch.tensor([4, 1, 0.25], dtype=torch.float64))
    torch.testing.assert_close(projector(result["basis"]), torch.diag(torch.tensor([1, 1, 1, 0], dtype=torch.float64)))


def test_rank_cap_is_distinguished_from_energy_target():
    result = basis_from_gradients(eye(5), max_rank=2, energy=0.95, method="exact")
    assert result["basis"].shape == (5, 2)
    assert result["rank_capped"]
    assert not result["energy_target_reached"]
    assert result["captured_energy"] == pytest.approx(0.4)
    assert result["effective_rank"] == 2


@pytest.mark.parametrize("rows", [0, 5])
def test_zero_gradient_has_no_invented_directions(rows):
    result = basis_from_gradients(torch.zeros(rows, 7))
    assert result["basis"].shape == (7, 0)
    assert result["eigenvalues"].numel() == 0
    assert result["effective_rank"] == 0
    assert result["captured_energy"] == 0
    assert result["total_energy"] == 0
    assert not result["rank_capped"]


def test_randomized_svd_recovers_low_rank_signal_without_changing_global_rng():
    generator = torch.Generator().manual_seed(4)
    left, _ = torch.linalg.qr(torch.randn(90, 3, generator=generator, dtype=torch.float64))
    right, _ = torch.linalg.qr(torch.randn(75, 3, generator=generator, dtype=torch.float64))
    gradients = (left * torch.tensor([5.0, 3.0, 1.0])) @ right.T
    before = torch.random.get_rng_state().clone()
    result = basis_from_gradients(gradients, max_rank=4, seed=8)
    assert torch.equal(before, torch.random.get_rng_state())
    assert result["basis"].shape == (75, 3)
    torch.testing.assert_close(projector(result["basis"]), projector(right), atol=1e-10, rtol=1e-10)
    torch.testing.assert_close(result["eigenvalues"], torch.tensor([25, 9, 1], dtype=torch.float64) / 90)
    repeat = basis_from_gradients(gradients, max_rank=4, seed=8)
    torch.testing.assert_close(result["basis"], repeat["basis"], atol=0, rtol=0)


def test_containment_direction_and_chance_baseline_account_for_rank():
    result = compare_subspaces(eye(5)[:, :1], eye(5)[:, :3])
    assert result["rank_u"] == 1 and result["rank_v"] == 3
    assert result["containment_u_in_v"] == pytest.approx(1)
    assert result["containment_v_in_u"] == pytest.approx(1 / 3)
    assert result["chance_containment_u_in_v"] == pytest.approx(3 / 5)
    assert result["chance_containment_v_in_u"] == pytest.approx(1 / 5)
    assert result["chance_adjusted_containment_u_in_v"] == pytest.approx(1)
    assert result["overlap_min"] == pytest.approx(1)
    json.dumps(result, allow_nan=False)


def test_orthogonal_subspaces_have_right_principal_angles():
    result = compare_subspaces(eye(6)[:, :2], eye(6)[:, 2:4])
    assert result["principal_angles_degrees"] == pytest.approx([90, 90])
    assert result["overlap_min"] == pytest.approx(0)
    assert result["containment_u_in_v"] == pytest.approx(0)


def test_empty_geometry_is_json_safe_and_zero_space_is_contained():
    empty = eye(4)[:, :0]
    result = compare_subspaces(empty, eye(4)[:, :1])
    assert result["principal_angles_degrees"] == []
    assert result["overlap_min"] is None
    assert result["containment_u_in_v"] == 1
    assert result["containment_v_in_u"] == 0
    json.dumps(result, allow_nan=False)
    torch.testing.assert_close(projector(empty), torch.zeros(4, 4, dtype=torch.float64))
    torch.testing.assert_close(normalized_operator(empty), eye(4))


def test_true_span_removes_duplicate_directions_and_is_a_projector():
    u, v = eye(5)[:, :2], eye(5)[:, 1:3]
    span = concatenate_span([u, v, -u])
    assert span.shape == (5, 3)
    expected = torch.diag(torch.tensor([1, 1, 1, 0, 0], dtype=torch.float64))
    torch.testing.assert_close(projector(span), expected)
    torch.testing.assert_close(projector(span) @ projector(span), expected)
    assert not torch.allclose(projector(u) + projector(v), expected)
    assert concatenate_span([eye(5)[:, :0]]).shape == (5, 0)


def example_pair():
    u = eye(6)[:, :2]
    angles = torch.tensor([0.3, 0.7], dtype=torch.float64)
    v = u * angles.cos() + eye(6)[:, 2:4] * angles.sin()
    return u, v, angles


def test_grassmann_interpolation_has_correct_endpoints_and_constant_angle_speed():
    u, v, angles = example_pair()
    torch.testing.assert_close(projector(grassmann_interpolate(u, v, 0)), projector(u))
    torch.testing.assert_close(projector(grassmann_interpolate(u, v, 1)), projector(v))
    middle = grassmann_interpolate(u, v, 0.5)
    expected = u * (angles / 2).cos() + eye(6)[:, 2:4] * (angles / 2).sin()
    torch.testing.assert_close(projector(middle), projector(expected), atol=1e-12, rtol=1e-12)
    torch.testing.assert_close(middle.T @ middle, eye(2), atol=1e-12, rtol=1e-12)


def test_grassmann_path_ignores_basis_signs_and_rotations_away_from_cut_locus():
    u, v, _ = example_pair()
    angle = 0.9
    rotation = torch.tensor([[math.cos(angle), -math.sin(angle)],
                             [math.sin(angle), math.cos(angle)]], dtype=torch.float64)
    expected = projector(grassmann_interpolate(u, v, 0.37))
    actual = projector(grassmann_interpolate(-u @ rotation, v @ rotation.T, 0.37))
    torch.testing.assert_close(actual, expected, atol=1e-12, rtol=1e-12)


def test_identical_and_partly_shared_spaces_do_not_divide_by_zero():
    u = eye(5)[:, :2]
    v = torch.stack([eye(5)[:, 0], math.cos(0.6) * eye(5)[:, 1] + math.sin(0.6) * eye(5)[:, 2]], dim=1)
    torch.testing.assert_close(projector(grassmann_interpolate(u, -u, 0.4)), projector(u))
    middle = grassmann_interpolate(u, v, 0.5)
    assert torch.isfinite(middle).all()
    assert compare_subspaces(u[:, :1], middle)["containment_u_in_v"] == pytest.approx(1)
    assert grassmann_interpolate(eye(5)[:, :0], eye(5)[:, :0], 0.5).shape == (5, 0)


def test_orthogonal_interpolation_selects_a_finite_nonunique_geodesic():
    u, v = eye(4)[:, :2], eye(4)[:, 2:]
    middle = grassmann_interpolate(u, v, 0.5)
    torch.testing.assert_close(middle.T @ middle, eye(2))
    assert compare_subspaces(u, middle)["principal_angles_degrees"] == pytest.approx([45, 45])


def test_residual_operator_has_equal_frobenius_budget_across_ranks():
    for rank in [1, 2, 4]:
        operator = normalized_operator(eye(5)[:, :rank], strength=-0.25)
        assert torch.linalg.vector_norm(operator - eye(5)).item() == pytest.approx(0.25)
    torch.testing.assert_close(normalized_operator(eye(5)[:, :2], strength=0), eye(5))


@pytest.mark.parametrize("kwargs", [{"max_rank": 0}, {"energy": 0}, {"energy": 1.1}, {"method": "bad"}])
def test_invalid_spectrum_configuration_fails(kwargs):
    with pytest.raises(ValueError):
        basis_from_gradients(eye(4), **kwargs)


def test_invalid_shapes_nonfinite_values_and_nonorthonormal_bases_fail():
    with pytest.raises(ValueError):
        basis_from_gradients(torch.tensor([[float("nan")]]))
    with pytest.raises(ValueError):
        compare_subspaces(eye(4)[:, :1], eye(5)[:, :1])
    with pytest.raises(ValueError):
        projector(eye(4)[:, :2] * 2)
    with pytest.raises(ValueError):
        concatenate_span([])
    with pytest.raises(ValueError):
        grassmann_interpolate(eye(4)[:, :1], eye(4)[:, :2], 0.5)
    with pytest.raises(ValueError):
        grassmann_interpolate(eye(4)[:, :1], eye(4)[:, :1], -0.5)
