# Improving: coding self-distillation and correct-solution diversity

本仓库只研究 **同一道 coding 题的不同正确实现/算法，在自蒸馏后是否被保留**。
提供从数据准备、校准、生成、LoRA 微调到独立代码验证、同题覆盖统计、跨轮次报告的完整实验流程。

## Start here: formal Spectral-soft experiment

当前主线是 **提高同一道 coding 题的正确实现多样性，同时保持准确率同水平**。
正式版以 Spectral-soft 为候选方法；主指标是固定 4 个正确样本的 AST 覆盖，准确率采用绝对 1 个百分点的不劣容忍界。AST 是实现结构代理，不能直接当作算法类别。

```bash
git pull origin main
python -m pip install -e '.[train,test,analysis]'
bash scripts/run_formal.sh configs/formal_16gb.yaml
```

这条命令默认跑 **正式确认实验**：完整 MBPP 500 道测试题，5 个新训练 seed（43–47），每题 64 次采样，`plain / ssd / spd_hard / spectral_soft`，一轮 raw-output LoRA 自蒸馏。脚本准备缺失的标准 MBPP 数据和验证容器，支持断点续跑，结束后生成报告与可复算的紧凑结果包。

| 后续实验 | 命令最后一个参数 | 内容 |
|---|---|---|
| 机制对照 | `mechanism` | 3 seeds；等强度简单软投影、相同谱随机方向、各向同性收缩 |
| 跨轮保留 | `retention` | 3 seeds；plain / hard / soft 各 3 轮 |
| 外部评测 | `transfer` | 5 seeds 的 base + 4 个确认检查点；完整 HumanEval+、官方 EvalPlus |
| 全部执行 | `all` | 依次运行四个阶段并汇总 |

```bash
# 确认实验之后，直接接着跑全部剩余阶段；完整阶段会复用。
bash scripts/run_formal.sh configs/formal_16gb.yaml all

# 24GB / 3B 模型对应配置；16GB 配置使用 1.5B。
bash scripts/run_formal.sh configs/formal_24gb.yaml
```

正式设置、机制公式、统计规则与预算见 [formal protocol](docs/formal_protocol.md)，论文证据计划见 [ICLR roadmap](docs/iclr_roadmap.md)。默认确认阶段上限 **887,740 个候选**；`all` 为 **2,652,072 个候选**。这些是候选数上限，不是 GPU 时间估计。16/24GB 是目标配置，实际峰值与速度待机器实测；启动前也可将最后参数设为 `validate` 查看数据和预算。

结果默认在 `runs/formal_spectral_16gb_v1/report/summary.md`，可上传的紧凑包在 `evidence/compact.tar.gz`。紧凑包包含逐题指标与运行来源，不含权重；需要程序用于独立算法标注时执行 `python -m improving formal --config configs/formal_16gb.yaml --stage export --resume --include-programs`。

**已完成的实证仍是 [64 题、seed-42 的探索性 pilot](results/pilot_seed42_codecentric/README.md)。新的正式确认、机制、三轮保留和 HumanEval+ 结果需要运行后取得；本仓库不把代码测试计为 benchmark 成绩。**

### Five- and ten-round retention extensions

The preregistered study stops at three retention rounds. Separate exploratory
profiles extend the same local RTX 5090 protocol to five or ten rounds without
changing or pooling with that endpoint:

```bash
# Validate without loading a model or starting GPU work.
PYTHONPATH=src python -m improving formal \
  --config configs/retention_5round_32gb_local.yaml --stage validate
PYTHONPATH=src python -m improving formal \
  --config configs/retention_10round_32gb_local.yaml --stage validate

# Run one seed at a time; --resume reuses sealed rounds and atomic chunks.
PYTHONPATH=src python -m improving formal \
  --config configs/retention_5round_32gb_local.yaml \
  --stage retention --job-id retention_seed43 --resume
PYTHONPATH=src python -m improving formal \
  --config configs/retention_10round_32gb_local.yaml \
  --stage retention --job-id retention_seed43 --resume
```

Replace `43` with `44` or `45` for the other planned seeds. A full 500-task
method-round generates up to 36,387 candidates, so these profiles are
multi-day experiments on one GPU and need substantial checkpoint storage.
Their output directories are distinct from formal v1.

For a short functional check only, the following profiles use four evaluation
tasks, four samples, eight training tasks, one SFT epoch and no generation-policy
diagnostic. They verify that five/ten sequential rounds and resume work; they
cannot report pass@8/32/64 and are not research evidence:

```bash
PYTHONPATH=src python -m improving validate \
  --config configs/retention_smoke_5round_32gb_local.yaml
PYTHONPATH=src python -m improving run \
  --config configs/retention_smoke_5round_32gb_local.yaml --resume

PYTHONPATH=src python -m improving validate \
  --config configs/retention_smoke_10round_32gb_local.yaml
PYTHONPATH=src python -m improving run \
  --config configs/retention_smoke_10round_32gb_local.yaml --resume
```

The smoke runtime is a target, not a guarantee; hardware contention and program
test time can move it beyond twenty minutes.

独立的冻结模型 [solution-subspace geometry study](docs/geometry_protocol.md) 保留，运行入口是 `scripts/run_geometry.sh`。它用于检查正确实现的子空间相似、包含、插值和共同张成关系，是可选机制诊断，不是本次 Spectral-soft 正式实验的前置阶段。

## Existing self-distillation pipeline

| Arm | Generation policy | SFT | Interpretation |
|---|---|---|---|
| `plain` | Original model; common sampling | One LoRA, raw outputs | Ordinary self-training control |
| `ssd` | Temperature 1.5, top-p .8, top-k 20 | Same LoRA budget | SSD decoding-recipe adaptation; not official large-scale reproduction |
| `spd_hard` | Top-r capability-gradient projector | Same LoRA budget | Paper-based SPD reconstruction with explicit insertion/span assumptions |
| `spectral_soft` | Full-spectrum proximal attenuation | Same LoRA budget | Candidate with exploratory pilot evidence; formal confirmation pending |
| `residual_blend` | `P + rho (I-P)` | Same LoRA budget | Simple soft-projector control |
| `random_hard` | Seeded rank-matched random projector | Same LoRA budget | Legacy geometric control |
| `matched_blend` | Two-level soft projector matched to soft operator distance from identity | Same LoRA budget | Formal mechanism control |
| `random_soft` | Same soft eigenvalue spectrum with independent Haar directions | Same LoRA budget | Formal direction control |
| `isotropic_soft` | Uniform shrinkage matched to soft operator distance from identity | Same LoRA budget | Formal isotropic control |

All arms train on **every raw generated completion**, including incorrect or empty outputs. No correctness filtering, algorithm labels, prompt ensembles, or strategy adapter pool enters training. Every round saves one merged model. The candidate uses no activation hooks in calibration, generation, SFT or inference. The hard reconstruction uses the same hook-free execution path; folding itself is an implementation equivalence, not a research contribution.

We read [SPD](https://arxiv.org/abs/2605.22675) and the [official SSD code](https://github.com/apple-aiml-research/ml-ssd/tree/2637d2021f1bc523385b48a1f88ea9aa4812b0a9). No official SPD code was found. No Apple-licensed code was copied. See [upstream audit](docs/upstream_audit.md) for the exact differences.

## Candidate mathematics and limits

From calibration completion NLL, collect **all nonpadding token gradients** of the native K/V linear outputs. For one selected module,

\[
C=\frac1M\sum_t g_tg_t^\top,\qquad \bar C=C/\lambda_{\max}(C),
\qquad T_\tau=[I+\tau(I-\bar C)]^{-1}.
\]

This is the classical quadratic proximal map

\[
\widetilde h=\arg\min_z\tfrac12\|z-h\|^2+
\tfrac\tau2 z^\top(I-\bar C)z.
\]

Its eigenvalues lie in `[1/(1+tau), 1]`; `tau=0` is identity. Unlike a hard rank cutoff, this map has no exact nullspace at finite tau in exact arithmetic. **Invertibility of this local map does not prove semantic algorithm diversity or whole-model information preservation.** Novelty and performance remain research questions; the operator alone is classical.

For row activations `h = x W.T + b`, we temporarily fold `h @ T` into `W' = T.T @ W`, `b' = T.T @ b`. Original weights are restored before SFT. This equivalence applies to the **linear output before RoPE and key normalization**. SPD does not specify its exact insertion point, so this is a declared reconstruction, not a proven match to unseen official code. GQA dimensions come from each actual `Linear.out_features`.

Default calibration supervises full reference completions. SPD's assertion-relevant span extraction is not sufficiently specified to reproduce; use `span_mode: explicit` with valid `calibration_spans` to evaluate a supplied span protocol. Do not describe the default as identical to SPD.

## Install and first run

From a CUDA machine with Python 3.10+ and Docker:

```bash
git clone https://github.com/yuhanlydia/improving.git
cd improving
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[train,test]'
improving doctor
python -m pytest -q
docker pull python:3.11-slim
improving prepare --dataset mbpp --output-dir data/mbpp --seed 42
improving validate --config configs/pilot_16gb.yaml
bash scripts/run_pilot.sh configs/pilot_16gb.yaml
improving report --run-dir runs/pilot_16gb_seed42
```

For 24 GB use `configs/pilot_24gb.yaml` (Qwen2.5-Coder-3B-Instruct). The 16 GB profile uses the 1.5B model. Both use BF16, generation batch 4, SFT microbatch 1 with accumulation 16 and nonreentrant gradient checkpointing. Quantized weights and FP16 training are deliberately unsupported by this tested path. Use a BF16-capable GPU; CPU fallback is for small correctness tests only.

The pilot takes a **fixed random subset of 128 training and 64 evaluation tasks**, with 64 completions per evaluation task. The selection seed `data_seed=42` stays fixed when training seeds change; selected tasks are saved under `runs/.../tasks/`. Calibration and validation come from disjoint official training examples. This is a pilot subset, not a full-benchmark score. Remove `data_limits` for the full prepared datasets.

MBPP preparation uses official **full** train/test splits, not sanitized MBPP or MBPP+. To specify the function interface, a fixed prompt includes only a signature stub derived mechanically from the reference AST, never its implementation or evaluation assertions. Original prompts and protocol provenance are retained. This is task specification shared by all arms, not a diversity prompt. Pin a dataset revision with `prepare --revision COMMIT` for later reproducibility. Downloaded split fingerprints are saved even if the revision is omitted.

Preparation removes exact normalized training-prompt overlaps with held-out prompts **before** splitting the training pool, while preserving the full test set. On the checked snapshot this removes training IDs 602, 704 and 872; final prepared counts are 291 train, 50 calibration, 30 validation and 500 evaluation. Every exclusion and its matching ID is recorded in `preparation_manifest.jsonl`. This hygiene applies equally to every arm and uses no outcome/strategy filtering.

Model execution occurs in the geometry generation/extraction stages and when you invoke `run`, `generate`, `calibrate` or `train`. `pytest` uses tiny randomly initialized models and explicitly trusted programs; its numbers are not benchmark results.

## What one round does

1. Evaluate the base model once and save all completions.
2. For each arm, calibrate on training references if needed; construct a temporary generation policy.
3. Generate one raw training completion per task. Also evaluate the generating policy on held-out prompts for diagnosis; these results never enter training or parameter selection.
4. Restore original weights, train one LoRA on the raw corpus, merge it, save the checkpoint atomically.
5. Evaluate the resulting model under common sampling settings.

Each additional round starts from the previous merged checkpoint and recomputes calibration. `epochs: 5` is five SFT epochs **within** a round; `rounds: 5` is five generate–train cycles. They are different quantities.

The SSD generating-policy diagnostic uses SSD's higher-temperature decoder. Its post-SFT evaluation uses the common decoder. Reports flag comparisons with different sampling protocols as incomparable; do not attribute that decoding difference to SFT alone.

Generated sample counts, maximum lengths, calibration access, LoRA rank and epochs are matched. **Actual token counts and FLOPs are not guaranteed equal**, since completion lengths differ; report saved token budgets, stage times and GPU memory alongside performance. The pilot uses much smaller data/context/training budgets than the original SSD paper.

## Resume and outputs

```bash
improving run --config configs/pilot_16gb.yaml --resume
```

Generation uses atomic per-batch chunks and deterministic batch seeds. A completed chunk is reused; a partially written chunk is regenerated. Changing batch size changes sampling streams and requires a new run directory. SFT restarts an interrupted round from its previous complete model; **mid-optimizer-step resume is not implemented**. Checkpoint and calibration publication are atomic. Complete rounds verify file hashes before reuse. Model shards, tokenizer/config, data and implementation provenance prevent silently mixing changed artifacts. Remote model revision is resolved and pinned within a run.

Important outputs:

```text
runs/pilot_16gb_seed42/
  manifest.json                 # configuration, code/data provenance, chosen tasks
  tasks/{train,calibration,validation,eval}.jsonl
  base/evaluation.jsonl         # every sample, never only the best
  base/evaluation.metrics.json
  spectral_soft/round_1/
    calibration.pt             # gradient second moments/eigenbasis/counts
    operator_diagnostics.json
    train.jsonl                # unfiltered raw completions used by SFT
    generation_policy.jsonl    # before distillation, with generating intervention
    evaluation.jsonl           # after distillation, native model
    evaluation.verified.jsonl
    evaluation.metrics.json
    model/                     # merged model/tokenizer/training_stats.json
    *.resources.json           # stage times and CUDA allocated/reserved peaks
    complete.json              # integrity hashes
  report.json
  report.md
```

Set `evaluation.backend: none` if Docker verification must be performed elsewhere. Samples are still saved and report entries remain pending. This does not fabricate zero scores. The default verifier executes candidates in restricted Docker containers without network; infrastructure failure stops the run instead of scoring every candidate wrong. Local execution requires an explicit trust flag and is only for trusted fixtures; it is not a security sandbox. Code extraction is part of the recorded evaluation protocol: `strict` accepts only a standalone fence, while the pilot configs use `first_fence` to evaluate the first Python/py/untagged block even when the model adds surrounding prose or omits the closing fence.

## Correctness versus algorithm diversity

`pass@k` estimates whether at least one sample is correct. It cannot count distinct correct algorithms. With `n` samples, `c` correct, and correct strategy counts `n_j`, the implemented finite-sample estimators are

\[
\widehat{pass@k}=1-\frac{\binom{n-c}{k}}{\binom nk},\qquad
\widehat{coverage@k}=\sum_j\left[1-\frac{\binom{n-n_j}{k}}{\binom nk}\right].
\]

Coverage is also computed at a **fixed number of correct samples**, so more correct samples alone cannot masquerade as greater strategy diversity. Eligible-task denominators, missing labels, zero-correct tasks and insufficient sampling budgets are explicit. CIs resample tasks; multiple training seeds remain necessary.

The default pilot records fixed-correct coverage at budgets 2, 4 and 8, with 4
as the primary pilot budget. Metric JSON also includes exact-program and
control-flow proxy coverage, unique fraction, effective label count, Simpson
diversity, and pairwise Python-token Jaccard distance. These are complementary
implementation proxies; reporting more proxies does not turn them into audited
algorithm identities.

Automatic AST fingerprints are labeled **implementation proxies**, never true algorithm classes. True algorithm coverage requires independent, audited `strategy_id` annotations. They are evaluation-only and never used to group/filter training samples. Keep labels consistent across models/rounds for observed strategy-retention analysis; absence in 64 draws does not prove a strategy has zero probability.

```json
{"task_id":"Mbpp/601","sample_id":0,"strategy_id":"hash-map"}
```

The ID above illustrates the annotation schema; it does not assign that algorithm to a real benchmark solution. Use one fixed rubric to distinguish algorithm changes from variable/style edits; do not infer semantic difference from subspace orthogonality or AST distance.

```bash
improving annotate --samples runs/pilot_16gb_seed42/spectral_soft/round_1/evaluation.verified.jsonl \
  --annotations annotations.jsonl --output analyses/annotated.jsonl
improving metrics --samples analyses/annotated.jsonl \
  --tasks runs/pilot_16gb_seed42/tasks/eval.jsonl --expected-samples 64 \
  --output analyses/algorithm_metrics.json
```

This separate analysis preserves the immutable original round files. `metrics.strategy_retention` provides observed stable-label retention and its finite-sampling limitations.

## HumanEval+ and external evaluation

Install the optional bridge with `python -m pip install -e '.[evalplus]'`. It imports/exports the **inspected EvalPlus 0.3.1 format** and rejects dropped/misaligned samples. Preparing HumanEval only creates original checks; extended HumanEval+ correctness must come from official EvalPlus results.

An offline container wrapper is included. Build-time downloads contain only dependencies and versioned evaluation data. Runtime candidate execution has no network. See [EvalPlus instructions](docs/evalplus.md) for the exact baked task snapshot and complete export/import commands. Docker is unavailable in the development environment, so the container itself has not been run here.

```bash
docker build -f docker/EvalPlus.Dockerfile -t improving-evalplus:0.3.1 .
bash scripts/evalplus_docker.sh prepare humaneval data/humaneval-plus
```

```bash
improving prepare --dataset humaneval --output-dir data/humaneval
improving generate --config configs/pilot_16gb.yaml \
  --checkpoint runs/pilot_16gb_seed42/spectral_soft/round_1/model \
  --tasks data/humaneval/eval.jsonl --samples 64 --output runs/humaneval/samples.jsonl
improving evalplus-export --tasks data/humaneval/eval.jsonl \
  --samples runs/humaneval/samples.jsonl --output runs/humaneval/evalplus.jsonl
```

Run the official evaluator in an isolated environment and then import its results:

```bash
bash scripts/evalplus_docker.sh evaluate humaneval runs/humaneval/evalplus.jsonl runs/humaneval/official
improving evalplus-import --tasks data/humaneval/eval.jsonl \
  --samples runs/humaneval/samples.jsonl --results runs/humaneval/official/samples_eval_results.json \
  --manifest runs/humaneval/evalplus.jsonl.manifest.jsonl --output runs/humaneval/verified.jsonl
improving metrics --samples runs/humaneval/verified.jsonl --tasks data/humaneval/eval.jsonl \
  --expected-samples 64 --output runs/humaneval/metrics.json
```

Full MBPP and MBPP+ have different task sets. Do not submit all full-MBPP IDs and silently score only the accepted subset. A native LiveCodeBench adapter is **not implemented**; use a frozen official release externally and only compare matching task IDs and protocols.

## Legacy custom sweeps

The frozen formal suite above is the main experiment. The original [pilot protocol](docs/experiment_protocol.md) and custom sweep generator remain available for separate exploratory runs:

```bash
python scripts/make_sweep.py --base configs/pilot_16gb.yaml \
  --rounds 5 --seeds 42 43 44 --controls --full-data
improving run --config configs/generated/rounds5_seed42.yaml
```

This writes configs only; it never starts an unrequested job. Validation tasks are reserved for prospective hyperparameter selection; the current default tau is fixed, and the pipeline does not optimize on evaluation outcomes. Do not call one favorable seed or structural proxy a successful algorithm-diversity paper.

## Code map and validation

- `data.py`, `verification.py`: split integrity, task interfaces, controlled execution and EvalPlus bridge.
- `calibration.py`, `spectral.py`: real gradients, covariance/eigenbasis, proximal controls and reversible native weight folding.
- `modeling.py`, `generation.py`, `training.py`: consistent serialization, retained sample streams and raw LoRA SFT.
- `metrics.py`, `reporting.py`: exact finite-sample statistics, eligibility and paired protocol-checked reports.
- `pipeline.py`, `cli.py`: stage lifecycle, provenance, resumability and commands.
- `formal_study.py`: frozen formal protocol, phase compilation and seed jobs.
- `formal_statistics.py`: paired multi-seed diversity and correctness inference.
- `formal_reporting.py`: formal reports and evidence exports.
- `formal_transfer.py`: official held-out HumanEval+ evaluation.

Tests cover exact combinatorial enumeration, frozen-model gradients, pre-RoPE full-model logit equivalence, positional padding/EOS masks, real tiny-model LoRA updates/reload, interrupted writes, resume integrity, trusted-fixture timeouts and official-format sample mapping. GitHub Actions runs CPU tests only, not expensive research experiments.
