"""Actual tiny-Qwen checks for per-correct-solution extraction and masks."""
import pytest
import torch
from torch import nn
from torch.nn import functional as F

from improving.geometry_extraction import (
    SolutionTooLongError, _masked_loss, _prepare_solution, collect_solution_subspaces, score_solution,
)
from improving.modeling import collate_examples
from tests.helpers import tiny_model_and_tokenizer


def setup_case():
    model, tokenizer = tiny_model_and_tokenizer()
    task = {"task_id": "toy/1", "prompt": "Write a function", "reference": "return 2",
            "calibration_spans": [[100, 999]]}
    ids = tokenizer.encode("def f ( ) : return 1", add_special_tokens=False) + [tokenizer.eos_token_id]
    record = {"task_id": task["task_id"], "sample_id": 0, "correct": True,
              "completion": tokenizer.decode(ids, skip_special_tokens=True), "completion_ids": ids}
    settings = {"layers": [0, 1], "max_length": 64, "max_rank": 8,
                "energy": .95, "method": "randomized", "seed": 42}
    return model, tokenizer, task, record, settings


def test_exact_token_ids_and_prompt_mask_match_independent_causal_loss():
    model, tokenizer, task, record, settings = setup_case()
    example = _prepare_solution(tokenizer, task, record, settings)
    prefix = tokenizer.encode(task["prompt"], add_special_tokens=False)
    assert example["input_ids"] == prefix + record["completion_ids"]
    assert example["labels"] == [-100] * len(prefix) + record["completion_ids"]
    batch = collate_examples([example], tokenizer.pad_token_id)
    model.eval()
    with torch.no_grad():
        logits = model(input_ids=batch["input_ids"], use_cache=False).logits
        wanted = F.cross_entropy(logits[:, len(prefix) - 1:-1].reshape(-1, logits.shape[-1]),
                                 torch.tensor(record["completion_ids"]))
    result = score_solution(model, tokenizer, task, record, settings)
    assert result["loss"] == pytest.approx(float(wanted), abs=1e-7)
    assert result["nll_sum"] == pytest.approx(float(wanted) * len(record["completion_ids"]))
    assert result["target_token_count"] == len(record["completion_ids"])
    assert result["mask_scope"] == "completion"


def test_record_spans_mask_exact_original_ids_and_never_reference_spans():
    _, tokenizer, task, record, settings = setup_case()
    start = record["completion"].index("return")
    record["loss_spans"] = [[start, start + len("return")]]
    example = _prepare_solution(tokenizer, task, record, settings)
    assert example["input_ids"][-len(record["completion_ids"]):] == record["completion_ids"]
    supervised = [label for label in example["labels"] if label != -100]
    assert supervised == tokenizer.encode("return", add_special_tokens=False)
    assert example["labels"][-1] == -100  # EOS is outside the character span.
    assert example["mask_scope"] == "record_loss_spans"


def test_repeat_extraction_is_identical_hook_free_and_restores_every_state(monkeypatch):
    model, tokenizer, task, record, settings = setup_case()
    model.train()
    model.model.layers[0].eval()
    next(model.parameters()).requires_grad_(False)
    first_parameter = next(model.parameters())
    first_parameter.grad = torch.ones_like(first_parameter)
    prior_grad = first_parameter.grad.clone()
    flags = [parameter.requires_grad for parameter in model.parameters()]
    states = {name: module.training for name, module in model.named_modules()}
    originals = {name: module for name, module in model.named_modules()
                 if name.endswith(("k_proj", "v_proj"))}

    def forbidden(*args, **kwargs):
        raise AssertionError("geometry extraction must not register hooks")

    monkeypatch.setattr(nn.Module, "register_forward_hook", forbidden)
    monkeypatch.setattr(nn.Module, "register_forward_pre_hook", forbidden)
    monkeypatch.setattr(nn.Module, "register_full_backward_hook", forbidden)
    first = collect_solution_subspaces(model, tokenizer, task, record, settings)
    second = collect_solution_subspaces(model, tokenizer, task, record, settings)
    assert first["metadata"] == second["metadata"]
    assert first["metadata"]["loss"] == pytest.approx(
        score_solution(model, tokenizer, task, record, settings)["loss"], abs=1e-7)
    for name, module_record in first["modules"].items():
        assert model.get_submodule(name) is originals[name]
        basis = module_record["basis"]
        assert basis.ndim == 2 and basis.shape[0] == originals[name].out_features
        assert basis.shape[1] > 0
        torch.testing.assert_close(basis.T @ basis, torch.eye(basis.shape[1], dtype=basis.dtype),
                                   rtol=1e-5, atol=1e-6)
        torch.testing.assert_close(basis @ basis.T,
                                   second["modules"][name]["basis"] @ second["modules"][name]["basis"].T,
                                   rtol=0, atol=0)
        assert module_record["token_count"] == first["metadata"]["token_count"]
        assert module_record["token_count"] > module_record["target_token_count"]
        torch.testing.assert_close(module_record["gradient_sum"],
                                   module_record["gradient_mean"] * module_record["token_count"])
        assert "covariance" not in module_record
    assert [parameter.requires_grad for parameter in model.parameters()] == flags
    assert {name: module.training for name, module in model.named_modules()} == states
    assert model.config.use_cache
    torch.testing.assert_close(first_parameter.grad, prior_grad, rtol=0, atol=0)
    assert all(parameter.grad is None for parameter in list(model.parameters())[1:])


def test_activation_rows_match_full_svd_and_include_prompt(monkeypatch):
    import improving.geometry as geometry

    model, tokenizer, task, record, settings = setup_case()
    original_decompose = geometry.basis_from_gradients
    gradients = []

    def capture(rows, **kwargs):
        gradients.append(rows.clone())
        return original_decompose(rows, **kwargs)

    monkeypatch.setattr(geometry, "basis_from_gradients", capture)
    artifact = collect_solution_subspaces(model, tokenizer, task, record, settings)
    prompt_length = len(tokenizer.encode(task["prompt"], add_special_tokens=False))
    for rows, module in zip(gradients, artifact["modules"].values()):
        assert rows[:prompt_length].norm() > 0
        assert len(rows) == artifact["metadata"]["token_count"]
        # The final activation cannot influence any selected next-token target,
        # but must still be present as a zero row in the decomposition.
        torch.testing.assert_close(rows[-1], torch.zeros_like(rows[-1]), rtol=0, atol=0)
        _, singular, vh = torch.linalg.svd(rows, full_matrices=False)
        rank = module["basis"].shape[1]
        wanted = vh[:rank].T
        torch.testing.assert_close(module["basis"] @ module["basis"].T,
                                   wanted @ wanted.T, rtol=1e-5, atol=1e-6)
        assert singular[0] > 0


@pytest.mark.parametrize("api", [collect_solution_subspaces, score_solution])
def test_forward_exception_restores_native_modules_and_flags(monkeypatch, api):
    model, tokenizer, task, record, settings = setup_case()
    model.train()
    model.model.layers[0].eval()
    model.model.embed_tokens.requires_grad_(False)
    flags = [p.requires_grad for p in model.parameters()]
    states = {name: module.training for name, module in model.named_modules()}
    original = model.model.layers[0].self_attn.k_proj

    def broken(*args, **kwargs):
        raise RuntimeError("injected forward failure")

    monkeypatch.setattr(model, "forward", broken)
    with pytest.raises(RuntimeError, match="injected forward failure"):
        api(model, tokenizer, task, record, settings)
    assert model.model.layers[0].self_attn.k_proj is original
    assert [p.requires_grad for p in model.parameters()] == flags
    assert {name: module.training for name, module in model.named_modules()} == states
    assert model.config.use_cache


@pytest.mark.parametrize("case", ["truncation", "wrong_task", "unverified", "bad_ids", "all_loss", "spans"])
def test_invalid_records_fail_explicitly(case):
    model, tokenizer, task, record, settings = setup_case()
    if case == "truncation":
        settings["max_length"] = 5
    elif case == "wrong_task":
        record["task_id"] = "another-task"
    elif case == "unverified":
        record["correct"] = False
    elif case == "bad_ids":
        record["completion_ids"][0] = True
    elif case == "all_loss":
        settings["loss_scope"] = "all"
    else:
        record["loss_spans"] = [[0, len(record["completion"]) + 1]]
    with pytest.raises(ValueError):
        collect_solution_subspaces(model, tokenizer, task, record, settings)


def test_span_alignment_failure_does_not_retokenize(monkeypatch):
    _, tokenizer, task, record, settings = setup_case()
    record["loss_spans"] = [[0, 3]]
    # Simulate a generated sequence whose decoded text admits another tokenization.
    record["completion_ids"] = [tokenizer.unk_token_id] + record["completion_ids"]
    monkeypatch.setattr(tokenizer, "decode", lambda *args, **kwargs: record["completion"])
    with pytest.raises(ValueError, match="cannot be aligned"):
        _prepare_solution(tokenizer, task, record, settings)


def test_masked_loss_selects_rows_before_ce_and_matches_dense_bfloat16_gradient(monkeypatch):
    torch.manual_seed(19)
    logits = torch.randn(2, 7, 23, dtype=torch.bfloat16, requires_grad=True)
    batch = {"input_ids": torch.ones(2, 7, dtype=torch.long),
             "attention_mask": torch.tensor([[1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 1, 1, 1, 1]]),
             "labels": torch.tensor([[-100, -100, -100, 6, 7, 8, 9], [-100, 4, -100, 2, -100, 3, 5]])}
    dense_labels = batch["labels"][:, 1:].clone()
    valid = batch["attention_mask"].bool()
    dense_labels.masked_fill_(~(valid[:, 1:] & valid[:, :-1]), -100)
    dense = F.cross_entropy(logits[:, :-1].float().reshape(-1, 23), dense_labels.reshape(-1))
    expected_gradient, = torch.autograd.grad(dense, logits)
    original_ce = F.cross_entropy
    calls = []

    def inspect_ce(inputs, targets, **kwargs):
        calls.append((inputs.shape, inputs.dtype, targets.clone()))
        return original_ce(inputs, targets, **kwargs)

    monkeypatch.setattr(F, "cross_entropy", inspect_ce)
    actual, count = _masked_loss(logits, batch)
    actual_gradient, = torch.autograd.grad(actual, logits)
    assert count == 5
    assert len(calls) == 1
    shape, dtype, targets = calls[0]
    assert shape == (count, 23)  # Excluded prompt/padding rows do not enter CE.
    assert dtype == torch.float32
    assert targets.tolist() == [6, 7, 2, 3, 5]
    torch.testing.assert_close(actual, dense, rtol=1e-6, atol=1e-7)
    torch.testing.assert_close(actual_gradient, expected_gradient, rtol=0, atol=0)


@pytest.mark.parametrize("limit", ["configured", "model"])
def test_complete_solution_length_errors_have_specific_type(limit):
    model, tokenizer, task, record, settings = setup_case()
    if limit == "configured":
        settings["max_length"] = 5
    else:
        model.config.max_position_embeddings = 5
    with pytest.raises(SolutionTooLongError):
        score_solution(model, tokenizer, task, record, settings)
