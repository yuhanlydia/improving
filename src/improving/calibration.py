"""Hook-free gradient second moments from training-reference completion NLL."""

from collections.abc import Iterable, Mapping, Sequence
import math
import os
from pathlib import Path
import tempfile
from typing import Any

import torch
from torch import Tensor, nn
from torch.nn import functional as F

from improving.spectral import _covariance_eigh, _native_linear


class _CaptureLinear(nn.Module):
    """Explicit temporary forward module; no activation hook is registered."""

    def __init__(self, linear: nn.Linear):
        super().__init__()
        self.linear = linear
        self.output: Tensor | None = None
        self.calls = 0

    def forward(self, inputs: Tensor) -> Tensor:
        self.calls += 1
        self.output = self.linear(inputs)
        return self.output


def _parent_and_leaf(model: nn.Module, name: str) -> tuple[nn.Module, str]:
    parent_name, separator, leaf = name.rpartition(".")
    return (model.get_submodule(parent_name) if separator else model), leaf


def collect_covariances(
    model: nn.Module,
    batches: Iterable[Mapping[str, Tensor]],
    module_names: Sequence[str],
) -> dict[str, dict[str, Any]]:
    """Accumulate ``G.T @ G`` at every nonpadding projection-output position.

    Input dictionaries require equally shaped 2D ``input_ids``,
    ``attention_mask``, and ``labels`` tensors. Labels use -100 for excluded
    prompt/completion positions. NLL uses causal shifting and the mean over
    selected next-token targets **within each example**. Examples are evaluated
    separately so results do not depend on how input batches are grouped.

    Parameters are temporarily frozen; detached input embeddings require grad
    to keep the projection outputs differentiable. No backward/forward hooks or
    parameter gradients are used. Each result contains CPU float64
    ``second_moment_sum`` and ``covariance`` (sum divided by ``token_count``),
    plus token/example/selected-target counts. Zero gradients contribute to the
    count; an entirely empty or zero-signal calibration is rejected.
    """
    names = list(module_names)
    if not names or len(set(names)) != len(names):
        raise ValueError("module_names must be nonempty and unique")
    originals = {name: _native_linear(model, name) for name in names}
    if len({id(module) for module in originals.values()}) != len(originals):
        raise ValueError("multiple names resolve to the same target module")
    wrappers = {name: _CaptureLinear(module) for name, module in originals.items()}
    parents = {name: _parent_and_leaf(model, name) for name in names}
    parameters = [(parameter, parameter.requires_grad) for parameter in model.parameters()]
    training_states = [(module, module.training) for module in model.modules()]
    config = getattr(model, "config", None)
    has_cache = config is not None and hasattr(config, "use_cache")
    cache_before = config.use_cache if has_cache else None
    records = {name: {"second_moment_sum": torch.zeros(module.out_features, module.out_features,
                                                      dtype=torch.float64),
                      "token_count": 0, "example_count": 0, "target_token_count": 0}
               for name, module in originals.items()}
    try:
        model.eval()
        if has_cache:
            config.use_cache = False
        for parameter, _ in parameters:
            parameter.requires_grad_(False)
        for name, wrapper in wrappers.items():
            parent, leaf = parents[name]
            setattr(parent, leaf, wrapper)
        embedding = model.get_input_embeddings()
        device = embedding.weight.device
        with torch.enable_grad():
            for batch in batches:
                if not isinstance(batch, Mapping) or not all(key in batch for key in ("input_ids", "attention_mask", "labels")):
                    raise ValueError("calibration batches require input_ids, attention_mask, and labels")
                ids, mask, labels = (batch[key] for key in ("input_ids", "attention_mask", "labels"))
                if (not all(isinstance(value, Tensor) and value.ndim == 2 for value in (ids, mask, labels))
                        or ids.shape != mask.shape or ids.shape != labels.shape or ids.shape[1] < 2):
                    raise ValueError("calibration tensors must have matching [batch, sequence>=2] shapes")
                if ids.dtype not in (torch.int32, torch.int64) or labels.dtype not in (torch.int32, torch.int64):
                    raise ValueError("input_ids and labels must contain integer token indices")
                if not torch.all((mask == 0) | (mask == 1)):
                    raise ValueError("attention_mask must contain only zero or one")
                for index in range(ids.shape[0]):
                    example_ids = ids[index:index + 1].to(device=device, dtype=torch.long)
                    example_mask = mask[index:index + 1].to(device=device)
                    example_labels = labels[index:index + 1].to(device=device, dtype=torch.long).clone()
                    valid_positions = example_mask.bool()
                    example_labels.masked_fill_(~valid_positions, -100)
                    shifted_labels = example_labels[:, 1:].clone()
                    shifted_labels.masked_fill_(~valid_positions[:, :-1], -100)
                    selected_count = int((shifted_labels != -100).sum())
                    if selected_count == 0:
                        raise ValueError("every calibration example needs a selected nonpadding next-token label")
                    for wrapper in wrappers.values():
                        wrapper.output = None
                        wrapper.calls = 0
                    inputs_embeds = embedding(example_ids).detach().requires_grad_(True)
                    output = model(inputs_embeds=inputs_embeds, attention_mask=example_mask, use_cache=False)
                    logits = output.logits if hasattr(output, "logits") else output["logits"]
                    if logits.shape[:2] != example_ids.shape:
                        raise ValueError("model logits must preserve batch and sequence dimensions")
                    loss = F.cross_entropy(logits[:, :-1].float().reshape(-1, logits.shape[-1]),
                                           shifted_labels.reshape(-1), ignore_index=-100, reduction="mean")
                    if not torch.isfinite(loss):
                        raise ValueError("calibration loss is nonfinite")
                    if any(wrapper.calls != 1 or wrapper.output is None for wrapper in wrappers.values()):
                        raise ValueError("each target projection must run exactly once per example")
                    captured = [wrappers[name].output for name in names]
                    gradients = torch.autograd.grad(loss, captured, allow_unused=True)
                    for name, gradient in zip(names, gradients):
                        if gradient is None or gradient.shape[:2] != example_ids.shape:
                            raise ValueError(f"target {name!r} must have differentiable [batch, sequence, output] activations")
                        selected = gradient.detach()[valid_positions.to(gradient.device)].to(device="cpu", dtype=torch.float64)
                        if selected.ndim != 2 or not torch.isfinite(selected).all():
                            raise ValueError(f"target {name!r} has invalid or nonfinite gradients")
                        record = records[name]
                        record["second_moment_sum"].add_(selected.T @ selected)
                        record["token_count"] += selected.shape[0]
                        record["example_count"] += 1
                        record["target_token_count"] += selected_count
                    for wrapper in wrappers.values():
                        wrapper.output = None
        for name, record in records.items():
            if record["token_count"] == 0:
                raise ValueError("calibration batches contain no examples")
            record["covariance"] = record["second_moment_sum"] / record["token_count"]
            _covariance_eigh(record["covariance"])
        return records
    finally:
        for name, module in originals.items():
            parent, leaf = parents[name]
            setattr(parent, leaf, module)
            wrappers[name].output = None
        for parameter, requires_grad in parameters:
            parameter.requires_grad_(requires_grad)
        for module, training in training_states:
            module.training = training
        if has_cache:
            config.use_cache = cache_before


def _plain_metadata(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("calibration metadata numbers must be finite")
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, (list, tuple)):
        return [_plain_metadata(item) for item in value]
    if isinstance(value, Mapping) and all(isinstance(key, str) for key in value):
        return {key: _plain_metadata(item) for key, item in value.items()}
    raise ValueError("calibration metadata must contain only JSON-compatible primitive values")


def save_calibration(
    path: str | Path,
    covariances: Mapping[str, Mapping[str, Any]],
    metadata: Mapping[str, Any] | None = None,
) -> None:
    """Atomically save second moments, eigenbasis, counts, and provenance."""
    if not covariances:
        raise ValueError("cannot save empty calibration")
    modules = {}
    for name, record in covariances.items():
        matrix, eigenvalues, eigenvectors = _covariance_eigh(record["covariance"])
        count = record["token_count"]
        if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            raise ValueError("token_count must be a positive integer")
        moment_sum = record.get("second_moment_sum", matrix * count).detach().to(device="cpu", dtype=torch.float64)
        if moment_sum.shape != matrix.shape or not torch.allclose(moment_sum / count, matrix):
            raise ValueError("second moment sum must agree with covariance and token_count")
        modules[name] = {"covariance": matrix, "second_moment_sum": moment_sum,
                         "eigenvalues": eigenvalues, "eigenvectors": eigenvectors,
                         "token_count": count,
                         "example_count": int(record.get("example_count", 0)),
                         "target_token_count": int(record.get("target_token_count", 0))}
    artifact = {"format_version": 1, "modules": modules,
                "metadata": _plain_metadata(dict(metadata or {}))}
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        # A sibling file keeps os.replace on the same filesystem. The final
        # artifact is untouched until serialization and flushing both succeed.
        with tempfile.NamedTemporaryFile(mode="wb", dir=destination.parent,
                                         prefix=f".{destination.name}.", suffix=".tmp",
                                         delete=False) as temporary:
            temporary_path = Path(temporary.name)
            torch.save(artifact, temporary)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, destination)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def load_calibration(path: str | Path) -> dict[str, Any]:
    """Load a portable calibration artifact with PyTorch's restricted loader."""
    artifact = torch.load(Path(path), map_location="cpu", weights_only=True)
    if (not isinstance(artifact, dict) or artifact.get("format_version") != 1
            or not isinstance(artifact.get("modules"), dict) or not artifact["modules"]):
        raise ValueError("unsupported or empty calibration artifact")
    _plain_metadata(artifact.get("metadata", {}))
    for name, record in artifact["modules"].items():
        if not isinstance(name, str) or not isinstance(record, dict):
            raise ValueError("invalid calibration module record")
        matrix, _, _ = _covariance_eigh(record["covariance"])
        count = record["token_count"]
        if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            raise ValueError("invalid calibration token count")
        moment_sum = record["second_moment_sum"]
        if moment_sum.shape != matrix.shape or not torch.allclose(moment_sum / count, matrix):
            raise ValueError("calibration second moment sum disagrees with covariance")
        eigenvalues, eigenvectors = record["eigenvalues"], record["eigenvectors"]
        if eigenvalues.shape != (matrix.shape[0],) or eigenvectors.shape != matrix.shape:
            raise ValueError("invalid calibration eigenbasis shape")
        reconstructed = (eigenvectors * eigenvalues.unsqueeze(0)) @ eigenvectors.T
        if not torch.allclose(reconstructed, matrix, rtol=1e-6, atol=float(matrix.abs().max()) * 1e-8):
            raise ValueError("calibration eigenbasis disagrees with covariance")
    return artifact
