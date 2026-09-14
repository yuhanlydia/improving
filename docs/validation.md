# Development validation — 2026-09-14

This records code validation, not model performance.

- CPU environment: Python 3.12.14, PyTorch 2.6.0+cpu, Transformers 4.51.3, PEFT 0.15.2.
- The full pytest suite passes **114 tests** and exercises real tiny randomly initialized Qwen2 models, causal loss, actual LoRA updates, checkpoint reload, calibration/folding and resume. No pretrained-model improvement is inferred.
- Independent review additionally exercised a real tiny BF16 LoRA update with nonreentrant gradient checkpointing: merged projections stayed native BF16 Linear modules, no forward/backward hooks remained, and logits were finite.
- MBPP downloaded and prepared successfully: original 374 training examples, 3 exact normalized prompt overlaps with evaluation removed before subdivision, 291 train / 50 calibration / 30 validation / 500 evaluation. Original official evaluation IDs all retained.
- `improving validate --config configs/pilot_16gb.yaml` succeeds against those actual files; the selected pilot uses 128 training tasks and 64 evaluation tasks with 64 samples per evaluation task.
- `pip check` reports no broken requirements. CLI import/help and Python compilation succeed.

Review-driven regression fixes cover:

1. Native generated token IDs are authoritative; capped or alternate-EOS streams never acquire synthetic termination labels.
2. SSD's generating-policy diagnostic uses its actual decoding parameters; final evaluation remains common across arms.
3. Checkpoint/calibration files publish atomically. Resume checks weight-shard bytes, tokenizer/config assets and source/data provenance. Remote base revisions are pinned within a run.
4. Per-stage resource records retain prior attempts and total elapsed time, so cached resume does not erase original compute costs.
5. Data preparation retains leakage assertions and logs every deterministic decontamination exclusion.

Not exercised here: CUDA throughput/peak memory on 16/24 GB hardware, full pretrained-model training, real generated-program benchmark scores, Docker execution/build, or human/independent-judge validity of algorithm strategy labels. EvalPlus sample mapping was checked against the inspected 0.3.1 source and representative payloads; the offline container adds build-time imports and dataset integrity checks, but requires validation on a Docker host.
