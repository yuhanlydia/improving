# UA-RL (adapted): a separate online-RL baseline

This runnable adapter implements the uniqueness-weighted advantage in Hu et al.,
**Rewarding the Rare: Uniqueness-Aware RL for Creative Problem Solving in LLMs**,
[Findings of ACL 2026](https://aclanthology.org/2026.findings-acl.1982/), Eq. (5).
It is **not self-distillation**, and its reporting epochs must not be called
self-distillation loops. The original public repository provided no runnable
training implementation when this adapter was prepared. Label table rows
**UA-RL (adapted)**, and leave results `x` until the resulting experiment completes.

## What is implemented

For each training question, the current policy generates `K` complete candidates.
The existing task-test verifier gives binary correctness rewards `r_i`. An
inference-only LLM judge sees the problem and **all** `K` candidates, partitions
them by high-level implementation strategy, and returns cluster sizes `f_i`.
Correctness labels and tests are not supplied to the judge.

```
z_i = (r_i - mean(r)) / (std(r) + 1e-4)
w_i = f_i ** (-alpha)
A_i = w_i * z_i
```

`A_i` replaces TRL's normalized correctness advantage **after normalization**;
there is no subsequent renormalization. Both positive and negative advantages
are weighted. The code never substitutes `r_i / f_i` as a reward: that would be a
different algorithm. TRL 0.23.1 supplies the clipped GRPO objective and KL penalty.
The reference remains the initial model throughout training (LoRA disabled).
The standard deviation uses TRL's sample-standard-deviation convention.

There is one active LoRA and one continuous GRPO run. Each reporting round is one
pass over the training prompts, with `K` online rollouts per prompt. For the
291-question MBPP training set and `K=16`, each full round uses 4,656 rollouts and
291 optimizer updates; five rounds use 23,280 rollouts. The trainer asserts this
count. This matches the number of generated training sequences in the new SD
suite, **not FLOPs, token count, verifier cost, or judge cost**. No eval question
or eval test is used for training, clustering, selection, or hyperparameter choice.

## Explicit adaptations and comparison conditions

- Code implementations and task-test correctness replace the paper's reasoning
  tasks and task-specific verifiers.
- The semantic judge uses the documented `code-strategy-partition-v1` prompt,
  rather than claiming a reproduction of the original multi-stage few-shot
  classification pipeline. There is no AST/lexical fallback.
- The shared configuration sets rollout count (normally 16), decoding temperature
  (normally 0.8), prompt template, maximum completion length, and LoRA dimensions.
  These differ from the original reported group size 8 and temperature 1.
- Learning rate defaults to `5e-7`, KL beta to `0.001`, and alpha to `1.0`.
  The learning-rate schedule is constant. Hyperparameters are explicit controls;
  this implementation does not tune on the test set or assert optimal tuning.
- TRL and Transformers versions differ from the original SD environment. Keep
  this in the experimental protocol; it is an algorithm-class baseline, not an
  isolated same-backend ablation. Native output verification and metrics match
  the shared pipeline.

## Installation and launch

Use a separate environment so the optional GRPO dependency does not alter the
core SPECTRUM environment. Start in the repository root:

```bash
python -m venv .venv-ua-rl
source .venv-ua-rl/bin/activate
pip install -r requirements-ua-rl.txt
pip install --no-deps -e .
```

Prepare the common MBPP JSONL partitions with the main suite first. A **semantic
judge endpoint must be explicitly provided**. A locally served suitable larger
code/reasoning model with an OpenAI-compatible `/v1/chat/completions` interface is
supported; serving software belongs in its own environment. No judge is downloaded
or started by this script. A remote endpoint additionally requires an API key in
the named environment variable. Endpoint URL credentials are rejected and keys
are never written to artifacts.

```bash
CUDA_VISIBLE_DEVICES=0 python scripts/run_ua_rl.py \
  --config configs/retention_5round_single_seed_n16_local.yaml \
  --judge-base-url http://127.0.0.1:8000/v1 \
  --judge-model YOUR_SERVED_JUDGE_MODEL \
  --output-dir runs/ua_rl_adapted_mbpp_seed43 \
  --rounds 5 --eval-samples 64 --alpha 1.0
```

The judge must support `seed`, `temperature`, and `max_tokens` in chat requests,
return an untruncated JSON cluster partition, and have enough context for all 16
512-token candidates plus the problem. Malformed partitions, unavailable judge
services, and verifier infrastructure failures abort rather than silently
changing the objective. HTTP retry is limited to transient failures; response
content is cached by the complete request and judge identity. Judge model quality
is part of this baseline's protocol and must be reported.

Use **one GPU / one process** for this adapter. Multiple independent seeds can
run on separate GPUs and output directories; DDP is deliberately rejected so a
rollout group cannot accidentally be partitioned across workers.

The example inherits the existing explicit local-execution setting. Docker
verification is also supported by setting the normal evaluation options and
preparing the specified Docker image. As in the core pipeline, local generated
code execution is resource-limited, not an isolation sandbox.

## Outputs and evaluation

```
protocol.json                    # exact data hashes, packages, judge and training settings
source_config.yaml
manifest.json                    # common transfer-evaluator manifest, algorithm_class=online_rl
tasks/*.jsonl                    # exact shared split snapshots
base/evaluation.jsonl
base/evaluation.verified.jsonl
base/evaluation.metrics.json
ua_rl/round_1/ ... round_5/
    adapter/                     # PEFT checkpoint + tokenizer; base model in checkpoint.json
    checkpoint.json
    evaluation.jsonl
    evaluation.verified.jsonl
    evaluation.metrics.json      # task-level values + task-bootstrap uncertainty
    evaluation.resources.json
    training.resources.json
training_groups/round_*/step_*.json
judge_cache/*.json
trainer/checkpoint-*/             # latest two resumable optimizer checkpoints
ua_rl/round_5/model/             # final merged HF checkpoint (round depends on --rounds)
final_model/                     # relative symlink to that final merged checkpoint
complete.json
```

Every round is evaluated on the same held-out task list, using 64 samples per
question by default. `evaluate_file` is the shared pipeline evaluator, retaining
verified programs, task-level metrics, eligibility counts, and task-bootstrap
intervals. Sampling budgets include 1, 4, 8, 16, 32, and 64; matched-correct budgets
include 4, 8, and 16. Evaluation preserves the training RNG states, mode, and cache
configuration. It never selects a checkpoint.

Per-round resource records use the shared `stage`, `status`, `elapsed_seconds`,
`cuda_peak_allocated_bytes`, and `cuda_peak_reserved_bytes` schema, so the common
report and longitudinal resource table include UA-RL. Records separate training
and evaluation wall time, peak CUDA
memory, rollout token counts, verifier time, and judge requests/input/output tokens.
An endpoint that omits usage marks `usage_missing_requests`; a missing token count
must not be presented as zero cost. Judge token counts are **additional** to policy
tokens. Resource logs are scoped to the current invocation; a resumed partial
epoch is flagged rather than presented as a complete cost measurement.

The adapter checkpoint can be loaded with `PeftModel.from_pretrained` on the exact
base model named in `checkpoint.json`. The final merged model loads through the
normal `load_model(..., checkpoint=...)` interface and has no judge dependency.
The common `evaluate_checkpoints` transfer path can consume this run with
`methods=["ua_rl"]` and `rounds=[5]` (or the configured final round). Earlier
rounds retain adapters and native MBPP evaluation; only the final round has a
full merged checkpoint for transfer. Missing earlier merged checkpoints are
reported as unavailable, never silently replaced by the final model.

To resume automatically from the latest integrity-checked optimizer checkpoint,
use the same command and add `--resume`. Before the first optimizer checkpoint
exists, this can restart the initial epoch only if no saved round student or
later completed stage exists. To identify the checkpoint explicitly, add:

```bash
--resume-from-checkpoint runs/ua_rl_adapted_mbpp_seed43/trainer/checkpoint-291
```

The protocol must match exactly. Resume checkpoints must belong to this run;
optimizer, RNG, adapter and trainer state are verified against saved hashes. An
older checkpoint is rejected when a later completed optimizer checkpoint exists.
Evaluation identity includes the actual adapter tensor values (and the immutable
base identity), so an unchanged round number cannot reuse evaluations from
different weights. Existing round students are checked before they are overwritten.
Completed evaluations are checked by file hashes;
partial generation uses the shared deterministic generation cache. No training,
GPU evaluation, external judge call, or package installation was performed while
preparing this implementation. Run this experiment before replacing the `x` row
in the paper with measurements.
