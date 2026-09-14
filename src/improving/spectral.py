"""Classical spectral controls and temporary pre-RoPE linear-output folding.

These operators define a local intervention; they do not establish diversity or
improvement of the complete model. A row-vector activation is transformed as
``h @ T``. Folding therefore uses ``T.T @ W`` and ``T.T @ b``.
"""

from collections.abc import Mapping, Sequence
from contextlib import contextmanager
import math
from numbers import Integral

import torch
from torch import Tensor, nn


def _covariance_eigh(covariance: Tensor) -> tuple[Tensor, Tensor, Tensor]:
    if not isinstance(covariance, Tensor) or covariance.ndim != 2:
        raise ValueError("covariance must be a square tensor")
    if covariance.shape[0] == 0 or covariance.shape[0] != covariance.shape[1]:
        raise ValueError("covariance must be nonempty and square")
    if covariance.is_complex():
        raise ValueError("covariance must be real")
    matrix = covariance.detach().to(device="cpu", dtype=torch.float64)
    if not torch.isfinite(matrix).all():
        raise ValueError("covariance must contain only finite values")
    scale = float(matrix.abs().max())
    if scale == 0:
        raise ValueError("covariance is zero; calibration has no gradient signal")
    if not torch.allclose(matrix, matrix.T, rtol=1e-7, atol=scale * 1e-9):
        raise ValueError("covariance must be symmetric")
    matrix = (matrix + matrix.T) * 0.5
    eigenvalues, eigenvectors = torch.linalg.eigh(matrix)
    if float(eigenvalues[0]) < -scale * 1e-7:
        raise ValueError("covariance must be positive semidefinite")
    eigenvalues = eigenvalues.clamp_min(0)
    if float(eigenvalues[-1]) <= 0:
        raise ValueError("covariance has no positive eigenvalue")
    return matrix, eigenvalues, eigenvectors


def make_operator(
    covariance: Tensor,
    kind: str = "spectral_soft",
    rank: int | None = None,
    tau: float = 1.0,
    rho: float = 0.5,
    seed: int = 42,
) -> Tensor:
    """Return a CPU float64 operator from an uncentered gradient covariance.

    ``spectral_soft`` is ``(I + tau*(I-C/lambda_max(C)))^-1``.
    ``hard`` uses the top ``rank`` eigenvectors, defaulting to ``d//2``.
    ``blend`` is ``P + rho*(I-P)``; ``random`` uses a seeded random subspace
    of the same rank. Eigenvectors for repeated eigenvalues are not unique.
    """
    allowed = {"spectral_soft", "hard", "identity", "blend", "random"}
    if kind not in allowed:
        raise ValueError(f"unknown operator kind {kind!r}; expected {sorted(allowed)}")
    if not math.isfinite(tau) or tau < 0:
        raise ValueError("tau must be finite and nonnegative")
    if not math.isfinite(rho) or not 0 <= rho <= 1:
        raise ValueError("rho must be finite and between zero and one")
    matrix, eigenvalues, eigenvectors = _covariance_eigh(covariance)
    dimension = matrix.shape[0]
    if rank is None:
        rank = dimension // 2
    if isinstance(rank, bool) or not isinstance(rank, Integral) or not 0 <= rank <= dimension:
        raise ValueError(f"rank must be an integer between 0 and {dimension}")
    identity = torch.eye(dimension, dtype=torch.float64)
    if kind == "identity" or (kind == "spectral_soft" and tau == 0):
        return identity
    if kind == "spectral_soft":
        gains = 1 / (1 + tau * (1 - eigenvalues / eigenvalues[-1]))
        return (eigenvectors * gains.unsqueeze(0)) @ eigenvectors.T
    if rank == 0:
        projector = torch.zeros_like(identity)
    elif rank == dimension:
        projector = identity
    else:
        if kind == "random":
            generator = torch.Generator(device="cpu").manual_seed(seed)
            basis, _ = torch.linalg.qr(torch.randn(dimension, rank, generator=generator,
                                                  dtype=torch.float64), mode="reduced")
        else:
            basis = eigenvectors[:, -rank:]
        projector = basis @ basis.T
    return projector + rho * (identity - projector) if kind == "blend" else projector


def _native_linear(model: nn.Module, name: str) -> nn.Linear:
    if not isinstance(name, str) or not name:
        raise ValueError("module names must be nonempty strings")
    try:
        module = model.get_submodule(name)
    except AttributeError as error:
        raise ValueError(f"target module {name!r} does not exist") from error
    if type(module) is not nn.Linear:
        raise TypeError(f"{name!r} must be a native torch.nn.Linear; merge adapters and "
                        "use unquantized weights before calibration or folding")
    if (not module.weight.is_floating_point() or module.weight.device.type == "meta"
            or not torch.isfinite(module.weight).all()
            or (module.bias is not None and not torch.isfinite(module.bias).all())):
        raise ValueError(f"{name!r} must have materialized finite floating-point weights")
    return module


def target_modules(
    model: nn.Module,
    layers: Sequence[int] | None = None,
    projections: Sequence[str] = ("k_proj", "v_proj"),
) -> list[str]:
    """Select exact Qwen/Llama-style attention paths, with no layer ranking.

    Defaults to the middle (zero-based ``n//2``) and last decoder layers.
    The selected Linear outputs precede rotary position embeddings and any
    subsequent key normalization; interventions after those operations differ.
    Unsupported model topologies fail instead of guessing projection paths.
    """
    count = getattr(getattr(model, "config", None), "num_hidden_layers", None)
    if not isinstance(count, Integral) or count <= 0:
        raise ValueError("model.config.num_hidden_layers must be a positive integer")
    selected = [count // 2, count - 1] if layers is None else list(layers)
    if not selected:
        raise ValueError("at least one layer is required")
    if any(isinstance(layer, bool) or not isinstance(layer, Integral)
           or not 0 <= layer < count for layer in selected):
        raise ValueError(f"layers must be integer indices in [0, {count})")
    if not projections or any(projection not in {"k_proj", "v_proj"} for projection in projections):
        raise ValueError("projections must contain k_proj and/or v_proj")
    names = [f"model.layers.{layer}.self_attn.{projection}"
             for layer in dict.fromkeys(selected) for projection in dict.fromkeys(projections)]
    for name in names:
        _native_linear(model, name)
    return names


@contextmanager
def folded_operators(model: nn.Module, operators: Mapping[str, Tensor]):
    """Temporarily fold row-output operators into native Linear parameters.

    Products are computed in float32 on each parameter's device, then cast to
    its original dtype. Exact original tensors are backed up on CPU and restored
    even if generation raises. Call on the pre-RoPE/pre-key-normalization
    projections returned by :func:`target_modules` for the documented protocol.
    """
    if not isinstance(operators, Mapping):
        raise TypeError("operators must map exact module names to tensors")
    prepared = []
    seen = set()
    for name, operator in operators.items():
        module = _native_linear(model, name)
        if id(module) in seen:
            raise ValueError("multiple names resolve to the same target module")
        seen.add(id(module))
        if (not isinstance(operator, Tensor) or operator.is_complex()
                or operator.shape != (module.out_features, module.out_features)
                or not torch.isfinite(operator).all()):
            raise ValueError(f"operator for {name!r} must be a finite square output-dimension tensor")
        transform = operator.detach().to(device=module.weight.device, dtype=torch.float32)
        if not torch.isfinite(transform).all():
            raise ValueError(f"operator for {name!r} cannot be represented in float32")
        weight = module.weight.detach().to(device="cpu", copy=True)
        bias = None if module.bias is None else module.bias.detach().to(device="cpu", copy=True)
        new_weight = (transform.T @ module.weight.detach().float()).to(module.weight.dtype)
        new_bias = None if module.bias is None else (transform.T @ module.bias.detach().float()).to(module.bias.dtype)
        if not torch.isfinite(new_weight).all() or (new_bias is not None and not torch.isfinite(new_bias).all()):
            raise ValueError(f"folded parameters for {name!r} are nonfinite")
        prepared.append((module, weight, bias, new_weight, new_bias))
    try:
        with torch.no_grad():
            for module, _, _, weight, bias in prepared:
                module.weight.copy_(weight)
                if bias is not None:
                    module.bias.copy_(bias)
        yield model
    finally:
        with torch.no_grad():
            for module, weight, bias, _, _ in prepared:
                module.weight.copy_(weight)
                if bias is not None:
                    module.bias.copy_(bias)
