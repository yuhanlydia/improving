from copy import deepcopy

import pytest
import torch
from torch import nn

from improving.spectral import folded_operators, make_operator, target_modules


def test_soft_spectrum_endpoints_and_covariance_scaling():
    covariance = torch.diag(torch.tensor([4.0, 1.0, 0.0], dtype=torch.float64))
    torch.testing.assert_close(make_operator(covariance, tau=0), torch.eye(3, dtype=torch.float64))
    expected = torch.diag(torch.tensor([1.0, 4 / 13, 0.25], dtype=torch.float64))
    torch.testing.assert_close(make_operator(covariance, tau=3), expected)
    torch.testing.assert_close(make_operator(covariance * 17, tau=3), expected)
    eigenvalues = torch.linalg.eigvalsh(make_operator(covariance, tau=3))
    assert eigenvalues.min() >= 0.25 - 1e-12
    assert eigenvalues.max() <= 1 + 1e-12


def test_projector_blend_and_seeded_random_controls():
    covariance = torch.diag(torch.tensor([4.0, 1.0, 0.0, 0.0], dtype=torch.float64))
    expected = torch.diag(torch.tensor([1.0, 0.0, 0.0, 0.0], dtype=torch.float64))
    torch.testing.assert_close(make_operator(covariance, kind="hard", rank=1), expected)
    torch.testing.assert_close(make_operator(covariance, kind="blend", rank=1, rho=0.2),
                               expected + 0.2 * (torch.eye(4, dtype=torch.float64) - expected))
    assert torch.linalg.matrix_rank(make_operator(covariance, kind="hard")) == 2
    torch.testing.assert_close(make_operator(covariance, kind="hard", rank=0), torch.zeros_like(covariance))
    state = torch.random.get_rng_state().clone()
    random = make_operator(covariance, kind="random", rank=2, seed=19)
    assert torch.equal(state, torch.random.get_rng_state())
    torch.testing.assert_close(random @ random, random)
    assert torch.linalg.matrix_rank(random) == 2
    torch.testing.assert_close(random, make_operator(covariance, kind="random", rank=2, seed=19))


@pytest.mark.parametrize("covariance,kwargs", [
    (torch.ones(2, 3), {}),
    (torch.zeros(2, 2), {}),
    (torch.diag(torch.tensor([1.0, -1.0])), {}),
    (torch.tensor([[1.0, 1.0], [0.0, 1.0]]), {}),
    (torch.eye(2) * float("nan"), {}),
    (torch.eye(2), {"tau": -1}),
    (torch.eye(2), {"tau": float("inf")}),
    (torch.eye(2), {"rank": 3, "kind": "hard"}),
    (torch.eye(2), {"rank": 1.5, "kind": "hard"}),
    (torch.eye(2), {"rho": -0.1, "kind": "blend"}),
    (torch.eye(2), {"kind": "unknown"}),
])
def test_invalid_operator_inputs_fail(covariance, kwargs):
    with pytest.raises((ValueError, TypeError)):
        make_operator(covariance, **kwargs)


def test_folding_transposes_operator_transforms_bias_and_restores_after_error():
    model = nn.Sequential(nn.Linear(3, 2, bias=True))
    operator = torch.tensor([[1.0, 0.2], [0.7, 0.5]])
    x = torch.tensor([[2.0, -1.0, 3.0]])
    before = {name: tensor.clone() for name, tensor in model.state_dict().items()}
    expected = model(x) @ operator
    with pytest.raises(RuntimeError, match="generation failed"):
        with folded_operators(model, {"0": operator}):
            torch.testing.assert_close(model(x), expected)
            raise RuntimeError("generation failed")
    for name, value in model.state_dict().items():
        assert torch.equal(value, before[name])


def test_folding_validates_every_target_before_mutation():
    model = nn.Sequential(nn.Linear(3, 2), nn.Linear(2, 1))
    before = deepcopy(model.state_dict())
    with pytest.raises(ValueError):
        with folded_operators(model, {"0": torch.eye(2) * 0.5, "1": torch.eye(2)}):
            pass
    for name, value in model.state_dict().items():
        assert torch.equal(value, before[name])


def tiny_qwen():
    transformers = pytest.importorskip("transformers")
    config = transformers.Qwen2Config(vocab_size=23, hidden_size=16, intermediate_size=24,
                                     num_hidden_layers=3, num_attention_heads=4,
                                     num_key_value_heads=2, attention_dropout=0.0)
    return transformers.Qwen2ForCausalLM(config).eval()


def test_tiny_qwen_native_outputs_match_folded_logits():
    torch.manual_seed(3)
    model = tiny_qwen()
    names = target_modules(model)
    assert names == ["model.layers.1.self_attn.k_proj", "model.layers.1.self_attn.v_proj",
                     "model.layers.2.self_attn.k_proj", "model.layers.2.self_attn.v_proj"]
    operators = {name: make_operator(torch.diag(torch.arange(1.0, 9.0)), tau=2) for name in names}
    reference = deepcopy(model)

    class DirectOutput(nn.Module):
        def __init__(self, base, operator):
            super().__init__()
            self.base = base
            self.operator = operator

        def forward(self, x):
            result = self.base(x)
            return result @ self.operator.to(result)

    for name, operator in operators.items():
        parent_name, leaf = name.rsplit(".", 1)
        parent = reference.get_submodule(parent_name)
        setattr(parent, leaf, DirectOutput(reference.get_submodule(name), operator))
    ids = torch.tensor([[1, 2, 5, 4, 3]])
    expected = reference(input_ids=ids, use_cache=False).logits
    original = model(input_ids=ids, use_cache=False).logits.detach().clone()
    with folded_operators(model, operators):
        actual = model(input_ids=ids, use_cache=False).logits
        torch.testing.assert_close(actual, expected, atol=2e-7, rtol=2e-5)
    torch.testing.assert_close(model(input_ids=ids, use_cache=False).logits, original, atol=0, rtol=0)


def test_non_native_linear_is_rejected():
    class AdapterLinear(nn.Linear):
        pass
    model = nn.Sequential(AdapterLinear(2, 2))
    with pytest.raises(TypeError, match="native"):
        with folded_operators(model, {"0": torch.eye(2)}):
            pass
