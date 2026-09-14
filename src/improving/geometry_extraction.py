"""Per-solution gradient geometry from native, pre-RoPE K/V activations.

Only completion next-token targets enter the loss. Gradients are collected at
*all* nonpadding activation rows, including the prompt rows that influence those
targets. Generated token IDs are preserved and overlong inputs are rejected.
This measures local sensitivity of a selected loss; it does not identify an
algorithm or supply a differentiable execution-correctness objective.
"""
from __future__ import annotations

from collections.abc import Mapping
from contextlib import contextmanager
from typing import Any

import torch
from torch import nn
from torch.nn import functional as F

from .calibration import _CaptureLinear, _parent_and_leaf
from .modeling import collate_examples, encode_example, render_prompt
from .spectral import _native_linear, target_modules


class SolutionTooLongError(ValueError):
    """A complete program cannot fit the configured or model context budget."""


def _prepare_solution(tokenizer, task: Mapping, record: Mapping, settings: Mapping) -> dict:
    """Build the exact causal mask; task reference spans never address a rollout."""
    if not isinstance(task, Mapping) or not isinstance(record, Mapping):
        raise ValueError("task and solution record must be mappings")
    if not isinstance(task.get("task_id"), str) or not task["task_id"]:
        raise ValueError("task_id must be a nonempty string")
    if record.get("task_id") != task["task_id"]:
        raise ValueError("solution task_id differs from its task")
    if type(record.get("sample_id")) is not int or record["sample_id"] < 0:
        raise ValueError("sample_id must be a nonnegative integer")
    completion = record.get("completion")
    if not isinstance(completion, str) or not completion:
        raise ValueError("a nonempty solution completion is required")
    if settings.get("loss_scope", "completion") != "completion":
        raise ValueError("solution geometry requires prompt-masked completion loss")
    max_length = settings.get("max_length", 2048)
    if type(max_length) is not int or max_length < 2:
        raise ValueError("max_length must be an integer of at least two")
    ids = record.get("completion_ids")
    if ids is not None:
        if (not isinstance(ids, (list, tuple)) or not ids
                or any(type(token) is not int or token < 0 for token in ids)):
            raise ValueError("completion_ids must be nonempty nonnegative integer token IDs")
        ids = list(ids)
        decoded = tokenizer.decode(ids, skip_special_tokens=True)
        if decoded != completion:
            raise ValueError("completion text does not match its preserved completion_ids")
    spans = record.get("loss_spans")
    if spans is not None:
        if not isinstance(spans, (list, tuple)) or not spans:
            raise ValueError("loss_spans must be nonempty completion character intervals")
        previous_end = 0
        for span in spans:
            if (not isinstance(span, (list, tuple)) or len(span) != 2
                    or any(type(value) is not int for value in span)
                    or not 0 <= previous_end <= span[0] < span[1] <= len(completion)):
                raise ValueError("loss_spans must be ordered, nonoverlapping completion intervals")
            previous_end = span[1]
    prompt = render_prompt(tokenizer, task)
    if spans is not None and ids is not None:
        # A tokenizer may not reproduce a generated sequence after decoding.
        # Character offsets are usable only when their IDs match exactly.
        encoded = tokenizer(completion, add_special_tokens=False, return_offsets_mapping=True)
        text_ids = list(encoded["input_ids"])
        trailing = ids[len(text_ids):]
        special_ids = set(getattr(tokenizer, "all_special_ids", []))
        if ids[:len(text_ids)] != text_ids or any(token not in special_ids for token in trailing):
            raise ValueError("loss_spans cannot be aligned to original completion_ids without retokenization")
        example = encode_example(tokenizer, prompt, completion, max_length=max_length,
                                 completion_ids=ids, append_eos=False)
        prefix_length = len(example["input_ids"]) - len(ids) + example["truncated_tokens"]
        selected = [token if any(a < end and b > start for a, b in spans) else -100
                    for token, (start, end) in zip(text_ids, encoded["offset_mapping"])]
        example["labels"] = ([-100] * prefix_length + selected + [-100] * len(trailing))[:max_length]
    else:
        example = encode_example(
            tokenizer, prompt, completion, max_length=max_length, spans=spans,
            completion_ids=ids, append_eos=record.get("finish_reason") != "length",
        )
    if example["truncated_tokens"]:
        raise SolutionTooLongError("solution geometry does not truncate: increase max_length for the complete solution")
    if not any(label != -100 for label in example["labels"][1:]):
        raise ValueError("solution mask contains no next-token targets")
    example["mask_scope"] = "record_loss_spans" if spans is not None else "completion"
    return example


@contextmanager
def _evaluation_state(model: nn.Module, *, freeze: bool):
    """Restore mixed module modes, parameter flags, and cache on every exit."""
    parameters = [(parameter, parameter.requires_grad) for parameter in model.parameters()]
    states = [(module, module.training) for module in model.modules()]
    config = getattr(model, "config", None)
    has_cache = config is not None and hasattr(config, "use_cache")
    cache_before = config.use_cache if has_cache else None
    try:
        model.eval()
        if has_cache:
            config.use_cache = False
        if freeze:
            for parameter, _ in parameters:
                parameter.requires_grad_(False)
        yield
    finally:
        for parameter, requires_grad in parameters:
            parameter.requires_grad_(requires_grad)
        for module, training in states:
            module.training = training
        if has_cache:
            config.use_cache = cache_before


def _batch_for(model, tokenizer, example: dict) -> dict:
    limit = getattr(getattr(model, "config", None), "max_position_embeddings", None)
    if limit is not None and len(example["input_ids"]) > limit:
        raise SolutionTooLongError("complete solution exceeds the model context limit")
    embedding = model.get_input_embeddings()
    if max(example["input_ids"]) >= embedding.num_embeddings:
        raise ValueError("solution contains a token ID outside the model vocabulary")
    pad_id = tokenizer.pad_token_id
    if pad_id is None:
        pad_id = tokenizer.eos_token_id
    if pad_id is None:
        raise ValueError("tokenizer requires a padding or EOS token")
    return {key: value.to(embedding.weight.device)
            for key, value in collate_examples([example], pad_id).items()}


def _masked_loss(logits: torch.Tensor, batch: dict) -> tuple[torch.Tensor, int]:
    if logits.shape[:2] != batch["input_ids"].shape:
        raise ValueError("model logits must preserve batch and sequence dimensions")
    labels = batch["labels"][:, 1:].clone()
    valid = batch["attention_mask"].bool()
    labels.masked_fill_(~(valid[:, 1:] & valid[:, :-1]), -100)
    count = int((labels != -100).sum())
    if count == 0:
        raise ValueError("solution mask contains no nonpadding next-token targets")
    # Index before upcasting: a long prompt contributes activation gradients,
    # but its excluded prediction rows need no FP32 vocabulary-sized CE buffer.
    # Gather remains differentiable, so all causal paths into selected targets
    # (including prompt K/V rows) are preserved.
    supervised = labels != -100
    loss = F.cross_entropy(logits[:, :-1][supervised].float(), labels[supervised],
                           reduction="mean")
    if not torch.isfinite(loss):
        raise ValueError("solution loss is nonfinite")
    return loss, count


def score_solution(model, tokenizer, task, record, settings) -> dict[str, Any]:
    """Score exact completion masked NLL without updating weights or model state.

    Correctness is not required here: callers may score references under an
    intervention before running its generated programs through a verifier.
    """
    example = _prepare_solution(tokenizer, task, record, settings)
    batch = _batch_for(model, tokenizer, example)
    with _evaluation_state(model, freeze=False), torch.no_grad():
        output = model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"], use_cache=False)
        logits = output.logits if hasattr(output, "logits") else output["logits"]
        loss, count = _masked_loss(logits, batch)
    value = float(loss)
    return {"loss": value, "nll_sum": value * count, "target_token_count": count,
            "token_count": int(batch["attention_mask"].sum()), "mask_scope": example["mask_scope"]}


def collect_solution_subspaces(model, tokenizer, task, record, settings) -> dict[str, Any]:
    """Extract one independently verified solution's feature-space bases.

    Modules are explicit temporary Linear wrappers, with no activation hooks.
    Every base parameter is frozen. Gradients of mean selected-target CE are
    obtained with ``autograd.grad`` and the full nonpadding row matrix is passed
    to the thin decomposition. No feature-by-feature covariance is saved.

    ``gradient_mean`` is the mean over activation rows, and ``gradient_sum`` is
    the derivative for a common additive activation shift. Neither is a weight
    gradient or a gradient of execution success.
    """
    if record.get("correct") is not True:
        raise ValueError("solution subspaces require a record verified correct")
    from .geometry import basis_from_gradients

    example = _prepare_solution(tokenizer, task, record, settings)
    batch = _batch_for(model, tokenizer, example)
    names = target_modules(model, layers=settings.get("layers"),
                           projections=settings.get("projections", ("k_proj", "v_proj")))
    originals = {name: _native_linear(model, name) for name in names}
    if len({id(module) for module in originals.values()}) != len(originals):
        raise ValueError("multiple names resolve to the same target module")
    wrappers = {name: _CaptureLinear(module) for name, module in originals.items()}
    parents = {name: _parent_and_leaf(model, name) for name in names}
    modules = {}
    with _evaluation_state(model, freeze=True):
        try:
            for name, wrapper in wrappers.items():
                parent, leaf = parents[name]
                setattr(parent, leaf, wrapper)
            with torch.enable_grad():
                embeddings = model.get_input_embeddings()(batch["input_ids"]).detach().requires_grad_(True)
                output = model(inputs_embeds=embeddings, attention_mask=batch["attention_mask"], use_cache=False)
                logits = output.logits if hasattr(output, "logits") else output["logits"]
                loss, count = _masked_loss(logits, batch)
                if any(wrapper.calls != 1 or wrapper.output is None for wrapper in wrappers.values()):
                    raise ValueError("each target projection must run exactly once per solution")
                gradients = torch.autograd.grad(loss, [wrappers[name].output for name in names], allow_unused=True)
            mask = batch["attention_mask"].bool()
            for index, (name, gradient) in enumerate(zip(names, gradients)):
                if gradient is None or gradient.shape[:2] != batch["input_ids"].shape:
                    raise ValueError(f"target {name!r} must have differentiable [batch, sequence, feature] activations")
                rows = gradient.detach()[mask.to(gradient.device)].to(device="cpu", dtype=torch.float64)
                if rows.ndim != 2 or not torch.isfinite(rows).all():
                    raise ValueError(f"target {name!r} has invalid or nonfinite gradients")
                spectral = basis_from_gradients(
                    rows, max_rank=settings.get("max_rank", 64), energy=settings.get("energy", .95),
                    method=settings.get("method", "randomized"), seed=settings.get("seed", 42) + index,
                )
                modules[name] = {**spectral, "gradient_mean": rows.mean(dim=0),
                                 "gradient_sum": rows.sum(dim=0), "token_count": len(rows),
                                 "target_token_count": count, "feature_dimension": rows.shape[1]}
        finally:
            for name, module in originals.items():
                parent, leaf = parents[name]
                setattr(parent, leaf, module)
                wrappers[name].output = None
    return {"format_version": 1, "task_id": task["task_id"], "sample_id": record["sample_id"],
            "modules": modules,
            "metadata": {"mask_scope": example["mask_scope"], "loss": float(loss.detach()),
                         "target_token_count": count, "token_count": int(batch["attention_mask"].sum()),
                         "activation_site": "native_linear_output_before_rope_and_key_norm",
                         "loss_reduction": "mean_selected_next_token_cross_entropy",
                         "completion_ids_preserved": record.get("completion_ids") is not None,
                         "reference_spans_used": False}}
