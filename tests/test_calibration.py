from pathlib import Path
from types import SimpleNamespace

import pytest
import torch
from torch import nn
from torch.nn import functional as F

from improving.calibration import collect_covariances, load_calibration, save_calibration


class ToyCausalLM(nn.Module):
    """Cumulative context ensures prompt positions affect completion loss."""

    def __init__(self):
        super().__init__()
        self.embedding = nn.Embedding(7, 3)
        self.k_proj = nn.Linear(3, 3)
        self.head = nn.Linear(3, 7)
        self.config = SimpleNamespace(use_cache=True)
        self.fail = False

    def get_input_embeddings(self):
        return self.embedding

    def forward(self, *, inputs_embeds, attention_mask, use_cache=False):
        assert use_cache is False
        hidden = self.k_proj(inputs_embeds)
        if self.fail:
            raise RuntimeError("forward failed")
        context = (hidden * attention_mask.unsqueeze(-1)).cumsum(dim=1)
        return SimpleNamespace(logits=self.head(context))


def setup_case():
    torch.manual_seed(5)
    model = ToyCausalLM()
    batch = {"input_ids": torch.tensor([[1, 2, 3, 4, 0]]),
             "attention_mask": torch.tensor([[1, 1, 1, 1, 0]]),
             "labels": torch.tensor([[-100, -100, -100, 4, -100]])}
    return model, batch


def test_covariance_uses_all_nonpadding_positions_with_frozen_parameters(monkeypatch):
    model, batch = setup_case()
    model.requires_grad_(False)
    # Independent analytic chain through the toy's cumulative context and CE.
    with torch.no_grad():
        hidden = model.k_proj(model.embedding(batch["input_ids"]))
        logits = model.head(hidden[:, :3].sum(dim=1))
        residual = logits.softmax(-1)
        residual[0, 4] -= 1
        direction = residual @ model.head.weight
        expected_sum = 3 * direction.double().T @ direction.double()
    def no_hooks(*args, **kwargs):
        raise AssertionError("calibration may not register activation hooks")
    monkeypatch.setattr(nn.Module, "register_forward_hook", no_hooks)
    monkeypatch.setattr(nn.Module, "register_forward_pre_hook", no_hooks)
    original = model.k_proj
    result = collect_covariances(model, [batch], ["k_proj"])["k_proj"]
    assert result["token_count"] == 4
    assert result["example_count"] == 1
    assert result["covariance"].device.type == "cpu"
    assert result["covariance"].dtype == torch.float64
    torch.testing.assert_close(result["second_moment_sum"], expected_sum, rtol=3e-6, atol=1e-9)
    torch.testing.assert_close(result["covariance"], expected_sum / 4, rtol=3e-6, atol=1e-9)
    assert torch.linalg.matrix_rank(result["covariance"], atol=1e-8) == 1
    assert model.k_proj is original
    assert model.training
    assert model.config.use_cache
    assert not any(parameter.requires_grad for parameter in model.parameters())
    assert all(parameter.grad is None for parameter in model.parameters())


def test_covariance_invariant_to_input_batch_grouping():
    model, batch = setup_case()
    paired = {key: torch.cat([value, value], dim=0) for key, value in batch.items()}
    grouped = collect_covariances(model, [paired], ["k_proj"])["k_proj"]
    separate = collect_covariances(model, [batch, batch], ["k_proj"])["k_proj"]
    assert grouped["token_count"] == 8
    assert grouped["example_count"] == 2
    torch.testing.assert_close(grouped["second_moment_sum"], separate["second_moment_sum"], atol=0, rtol=0)


def test_exception_restores_modules_parameter_flags_and_mixed_training_states():
    model, batch = setup_case()
    model.embedding.requires_grad_(False)
    model.head.eval()
    flags = [parameter.requires_grad for parameter in model.parameters()]
    states = {name: module.training for name, module in model.named_modules()}
    original = model.k_proj
    model.fail = True
    with pytest.raises(RuntimeError, match="forward failed"):
        collect_covariances(model, [batch], ["k_proj"])
    assert model.k_proj is original
    assert [parameter.requires_grad for parameter in model.parameters()] == flags
    assert {name: module.training for name, module in model.named_modules()} == states
    assert model.config.use_cache


@pytest.mark.parametrize("case", ["empty", "no_labels", "padding_labels", "zero_gradients", "nonfinite"])
def test_empty_or_invalid_calibration_is_rejected(case):
    model, batch = setup_case()
    batches = [batch]
    if case == "empty":
        batches = []
    elif case == "no_labels":
        batch["labels"].fill_(-100)
    elif case == "padding_labels":
        batch["labels"].fill_(-100)
        batch["labels"][0, -1] = 2
    elif case == "zero_gradients":
        nn.init.zeros_(model.head.weight)
    else:
        with torch.no_grad():
            model.head.weight.fill_(float("nan"))
    with pytest.raises(ValueError):
        collect_covariances(model, batches, ["k_proj"])


def test_artifact_roundtrip_saves_eigenbasis_counts_and_metadata(tmp_path):
    model, batch = setup_case()
    covariances = collect_covariances(model, [batch], ["k_proj"])
    path = tmp_path / "calibration.pt"
    save_calibration(path, covariances, metadata={"split": "train", "model": "toy"})
    result = load_calibration(path)
    assert result["metadata"] == {"split": "train", "model": "toy"}
    entry = result["modules"]["k_proj"]
    assert entry["token_count"] == 4
    torch.testing.assert_close(entry["covariance"], covariances["k_proj"]["covariance"])
    reconstruction = (entry["eigenvectors"] * entry["eigenvalues"].unsqueeze(0)) @ entry["eigenvectors"].T
    torch.testing.assert_close(reconstruction, entry["covariance"])
    assert torch.load(path, weights_only=True)["format_version"] == 1


@pytest.mark.parametrize("existing", [False, True])
def test_failed_serialization_preserves_prior_artifact_and_cleans_partial_file(tmp_path, monkeypatch, existing):
    path = tmp_path / "calibration.pt"
    covariances = {"k_proj": {"covariance": torch.eye(2), "token_count": 3}}
    if existing:
        save_calibration(path, covariances, metadata={"version": "original"})
    prior_bytes = path.read_bytes() if existing else None

    def interrupted_save(artifact, destination):
        if hasattr(destination, "write"):
            destination.write(b"incomplete archive")
        else:
            Path(destination).write_bytes(b"incomplete archive")
        raise OSError("serialization interrupted")

    monkeypatch.setattr(torch, "save", interrupted_save)
    with pytest.raises(OSError, match="serialization interrupted"):
        save_calibration(path, covariances, metadata={"version": "replacement"})
    if existing:
        assert path.read_bytes() == prior_bytes
        assert load_calibration(path)["metadata"] == {"version": "original"}
    else:
        assert not path.exists()
    assert list(tmp_path.iterdir()) == ([path] if existing else [])


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_metadata_is_rejected_on_save_and_load(tmp_path, value):
    path = tmp_path / "calibration.pt"
    covariances = {"k_proj": {"covariance": torch.eye(2), "token_count": 3}}
    with pytest.raises(ValueError, match="finite"):
        save_calibration(path, covariances, metadata={"nested": [{"value": value}]})
    assert not path.exists()
    save_calibration(path, covariances, metadata={"value": 1.0})
    artifact = torch.load(path, weights_only=True)
    artifact["metadata"] = {"nested": [{"value": value}]}
    torch.save(artifact, path)
    with pytest.raises(ValueError, match="finite"):
        load_calibration(path)
