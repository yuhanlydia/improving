"""Basis-invariant geometry for the frozen-model coding diagnostic.

All calculations detach tensors and use CPU float64. These routines compare
subspaces of a *shared feature coordinate system*; callers must keep layer,
projection type, checkpoint, and mask convention fixed. Geometry alone does not
identify algorithms. No dense feature-by-feature covariance is constructed by
``basis_from_gradients``.
"""

from collections.abc import Sequence
import math
from numbers import Integral

import torch
from torch import Tensor


def _matrix(value: Tensor, name: str) -> Tensor:
    if not isinstance(value, Tensor) or value.ndim != 2 or value.is_complex():
        raise ValueError(f"{name} must be a real two-dimensional tensor")
    matrix = value.detach().to(device="cpu", dtype=torch.float64)
    if not torch.isfinite(matrix).all():
        raise ValueError(f"{name} must contain only finite values")
    return matrix


def _basis(value: Tensor, name: str = "basis") -> Tensor:
    matrix = _matrix(value, name)
    dimension, rank = matrix.shape
    if dimension == 0 or rank > dimension:
        raise ValueError(f"{name} must have positive ambient dimension and rank <= dimension")
    if rank and not torch.allclose(matrix.T @ matrix, torch.eye(rank, dtype=torch.float64),
                                   atol=1e-6, rtol=1e-6):
        raise ValueError(f"{name} columns must be orthonormal")
    return matrix


def _paired_bases(u: Tensor, v: Tensor) -> tuple[Tensor, Tensor]:
    u, v = _basis(u, "U"), _basis(v, "V")
    if u.shape[0] != v.shape[0]:
        raise ValueError("U and V must share their ambient feature dimension")
    return u, v


def basis_from_gradients(
    G: Tensor,
    max_rank: int = 64,
    energy: float = 0.95,
    method: str = "randomized",
    seed: int = 42,
) -> dict:
    """Return all nonzero leading gradient directions up to ``max_rank``.

    Rows of G are gradient observations in shared feature coordinates. Returned
    eigenvalues approximate those of G.T @ G / n, in descending order. Exact
    ``total_energy`` is ||G||_F**2 / n, and ``captured_energy`` is the fraction
    represented by the returned spectrum. ``effective_rank`` is the minimum
    retained count meeting ``energy``; when that target is unavailable it is
    the available count, with ``rank_capped=True``. This energy diagnostic does
    not truncate the basis, so callers can independently compare a rank grid.

    Randomized range finding uses an isolated seeded generator, oversampling,
    and two power iterations, followed by thin SVD. Its eigenvalues/energy rank
    are approximate; target failure can reflect approximation as well as the
    rank cap. Small matrices or a full range use exact thin SVD. Zero gradients
    return an empty basis instead of arbitrary null-space directions.
    """
    matrix = _matrix(G, "G")
    rows, dimension = matrix.shape
    if dimension == 0:
        raise ValueError("G must have a positive feature dimension")
    if isinstance(max_rank, bool) or not isinstance(max_rank, Integral) or max_rank <= 0:
        raise ValueError("max_rank must be a positive integer")
    if not math.isfinite(energy) or not 0 < energy <= 1:
        raise ValueError("energy must be finite and in (0, 1]")
    if method not in {"randomized", "exact"}:
        raise ValueError("method must be 'randomized' or 'exact'")
    if isinstance(seed, bool) or not isinstance(seed, Integral):
        raise ValueError("seed must be an integer")
    total = float(matrix.square().sum()) / rows if rows else 0.0
    if not math.isfinite(total):
        raise ValueError("G squared energy must be representable in float64")
    common = {
        "total_energy": total,
        "energy_target": float(energy),
        "max_rank": int(max_rank),
        "n_observations": rows,
        "ambient_dimension": dimension,
        "seed": int(seed),
    }
    if total == 0:
        return {
            **common, "basis": torch.empty(dimension, 0, dtype=torch.float64),
            "eigenvalues": torch.empty(0, dtype=torch.float64),
            "captured_energy": 0.0, "captured_energy_absolute": 0.0,
            "effective_rank": 0, "rank_capped": False,
            "energy_target_reached": False, "method_used": "zero_signal",
            "numerical_rank_lower_bound": 0,
        }
    range_rank = min(rows, dimension, max_rank + 16)
    if method == "exact" or range_rank == min(rows, dimension):
        _, singular_values, vh = torch.linalg.svd(matrix, full_matrices=False)
        method_used = "exact"
    else:
        generator = torch.Generator(device="cpu").manual_seed(int(seed))
        omega = torch.randn(dimension, range_rank, generator=generator, dtype=torch.float64)
        q, _ = torch.linalg.qr(matrix @ omega, mode="reduced")
        for _ in range(2):
            z, _ = torch.linalg.qr(matrix.T @ q, mode="reduced")
            q, _ = torch.linalg.qr(matrix @ z, mode="reduced")
        _, singular_values, vh = torch.linalg.svd(q.T @ matrix, full_matrices=False)
        method_used = "randomized"
    tolerance = max(rows, dimension) * torch.finfo(torch.float64).eps * float(singular_values[0])
    available = int((singular_values > tolerance).sum())
    retained = min(available, int(max_rank))
    eigenvalues = singular_values[:retained].square() / rows
    cumulative = eigenvalues.cumsum(0) / total
    captured = min(1.0, max(0.0, float(cumulative[-1]))) if retained else 0.0
    # Permit rounding noise at energy=1 without masking substantive truncation.
    target_reached = captured >= energy - 1e-12
    reaching = torch.nonzero(cumulative >= energy - 1e-12, as_tuple=False)
    effective = int(reaching[0, 0]) + 1 if len(reaching) else retained
    return {
        **common,
        "basis": vh[:retained].T.contiguous(),
        "eigenvalues": eigenvalues.contiguous(),
        "captured_energy": captured,
        "captured_energy_absolute": float(eigenvalues.sum()),
        "effective_rank": effective,
        "rank_capped": not target_reached,
        "energy_target_reached": target_reached,
        "method_used": method_used,
        "numerical_rank_lower_bound": available,
    }


def compare_subspaces(U: Tensor, V: Tensor) -> dict:
    """JSON-safe principal angles, directional containment, and chance controls.

    Containment U->V averages the squared projection of U's basis vectors into
    V. A zero space is contained in every space by convention, but overlap and
    chance-adjusted scores involving a zero space are undefined (None). Chance
    expectations assume independent uniformly random subspaces in this ambient
    dimension; these controls are not significance tests.
    """
    u, v = _paired_bases(U, V)
    dimension, rank_u = u.shape
    rank_v = v.shape[1]
    singular_values = torch.linalg.svdvals(u.T @ v).clamp(0, 1)
    squared_overlap = min(float(singular_values.square().sum()), float(min(rank_u, rank_v)))
    angles = torch.rad2deg(torch.acos(singular_values)).tolist()
    containment_u = squared_overlap / rank_u if rank_u else 1.0
    containment_v = squared_overlap / rank_v if rank_v else 1.0
    chance_u, chance_v = rank_v / dimension, rank_u / dimension
    defined = rank_u > 0 and rank_v > 0

    def adjusted(score: float, chance: float):
        return (score - chance) / (1 - chance) if defined and chance < 1 else None

    overlap = squared_overlap / min(rank_u, rank_v) if defined else None
    chance_overlap = max(rank_u, rank_v) / dimension if defined else None
    return {
        "ambient_dimension": dimension,
        "rank_u": rank_u, "rank_v": rank_v,
        "principal_angles_degrees": angles,
        "overlap_min": overlap,
        "squared_overlap": squared_overlap,
        "containment_u_in_v": containment_u,
        "containment_v_in_u": containment_v,
        "chance_containment_u_in_v": chance_u,
        "chance_containment_v_in_u": chance_v,
        "chance_adjusted_containment_u_in_v": adjusted(containment_u, chance_u),
        "chance_adjusted_containment_v_in_u": adjusted(containment_v, chance_v),
        "chance_overlap_min": chance_overlap,
        "chance_adjusted_overlap_min": adjusted(overlap, chance_overlap) if defined else None,
        "projector_frobenius_distance": math.sqrt(max(0.0, rank_u + rank_v - 2 * squared_overlap)),
        "has_orthogonal_principal_direction": any(angle >= 90 - 1e-7 for angle in angles),
    }


def projector(U: Tensor) -> Tensor:
    """Return the orthogonal projector onto orthonormal U's columns."""
    basis = _basis(U)
    return basis @ basis.T


def concatenate_span(bases: Sequence[Tensor], *, rtol: float | None = None) -> Tensor:
    """Return an orthonormal basis for span(U_1, ..., U_m), not projector sum.

    Numerical rank uses ``rtol * largest_singular_value``; the default is the
    standard float64 matrix-size tolerance. A larger, preregistered rtol can
    define an approximate span but changes the scientific question.
    """
    if not bases:
        raise ValueError("at least one basis is required to determine ambient dimension")
    matrices = [_basis(basis) for basis in bases]
    dimension = matrices[0].shape[0]
    if any(matrix.shape[0] != dimension for matrix in matrices):
        raise ValueError("all bases must share their ambient feature dimension")
    if rtol is not None and (not math.isfinite(rtol) or rtol < 0):
        raise ValueError("rtol must be finite and nonnegative")
    joined = torch.cat(matrices, dim=1)
    if joined.shape[1] == 0:
        return joined
    left, singular_values, _ = torch.linalg.svd(joined, full_matrices=False)
    relative = max(joined.shape) * torch.finfo(torch.float64).eps if rtol is None else rtol
    rank = int((singular_values > relative * singular_values[0]).sum())
    return left[:, :rank].contiguous()


def grassmann_interpolate(U: Tensor, V: Tensor, t: float) -> Tensor:
    """Interpolate equal-rank subspaces along a shortest Grassmann geodesic.

    Away from a 90-degree principal angle (the cut locus), the resulting
    *projector* is invariant to input basis signs and rotations. At the cut
    locus the shortest path is nonunique; this implementation selects the
    branch supplied by torch's SVD. Its interior may then depend on basis
    choices, and cannot support a unique interpolation claim. Endpoints always
    equal the input subspaces. A convex projector blend is a different operator
    and generally not a rank-preserving projector.
    """
    u, v = _paired_bases(U, V)
    if u.shape[1] != v.shape[1]:
        raise ValueError("Grassmann interpolation requires equal ranks")
    if not math.isfinite(t) or not 0 <= t <= 1:
        raise ValueError("t must be finite and between zero and one")
    if t == 0 or u.shape[1] == 0:
        return u.clone()
    if t == 1:
        return v.clone()
    left, cosines, right_h = torch.linalg.svd(u.T @ v, full_matrices=False)
    cosines = cosines.clamp(0, 1)
    aligned_u, aligned_v = u @ left, v @ right_h.T
    residual = aligned_v - aligned_u * cosines
    sines = torch.linalg.vector_norm(residual, dim=0)
    angles = torch.atan2(sines, cosines)
    normal = torch.zeros_like(residual)
    active = sines > 1e-12
    normal[:, active] = residual[:, active] / sines[active]
    interpolated = aligned_u * torch.cos(t * angles) + normal * torch.sin(t * angles)
    # Remove accumulated roundoff without changing the represented subspace.
    return torch.linalg.qr(interpolated, mode="reduced")[0]


def normalized_operator(U: Tensor, strength: float = 1.0) -> Tensor:
    """Return I + strength * P_U / sqrt(rank(U)).

    For nonempty U, ||T-I||_F is |strength| irrespective of rank. This matches
    an operator budget, not activation change or output KL; experiments must
    also record those realized changes. Empty U returns identity.
    """
    basis = _basis(U)
    if not math.isfinite(strength):
        raise ValueError("strength must be finite")
    dimension, rank = basis.shape
    identity = torch.eye(dimension, dtype=torch.float64)
    return identity + strength / math.sqrt(rank) * (basis @ basis.T) if rank else identity
