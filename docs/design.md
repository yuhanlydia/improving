# Coding self-distillation: implementation contract

The user authorized implementing and pushing a coding-only research repository on 2026-09-14. The remote repository was empty. This is an experimental implementation, not evidence of improved benchmark performance.

## Scope

Study correct implementations and algorithms for the SAME coding task before generation interventions and after repeated self-distillation. No cross-domain experiment, external teacher, manual training selection, prompt ensemble, strategy adapter pool, or claim that geometry guarantees algorithm diversity.

## Implemented hypothesis

For pre-RoPE K/V linear-output gradient covariance C, define Cbar=C/lambda_max(C). The candidate operator is T_tau=(I+tau*(I-Cbar))^-1. It is the minimizer of 0.5||z-h||^2+tau/2*z^T(I-Cbar)z. Every eigenvalue lies in [1/(1+tau),1]. It preserves information in this local linear map, NOT necessarily in the complete model. This is classical spectral shrinkage used as an unvalidated candidate; no novelty theorem or advantage is claimed. Tau=0 is identity.

Controls: ordinary raw self-training; SSD-style decoding with matched budget; SPD-style hard top-r projector P; residual blend P+rho(I-P); random rank-matched hard projection. Hard/soft operators are folded into temporary native Linear weights before generation. A reference hard hook path is OPTIONAL solely for equivalence tests/baseline, never needed by the candidate. Gradient capture uses temporary explicit modules + autograd.grad, not hook registration. Folding is equivalent ONLY to pre-RoPE/pre-key-normalization linear-output intervention, which is our documented SPD reconstruction assumption.

Calibration uses training-split reference solutions, completion-token NLL by default; optional explicit character spans allow a supplied correctness-span protocol. This differs from SPD's underspecified assertion-relevant spans. Gradients from ALL nonpadding positions contribute to C. C is accumulated on CPU float64, eigenbasis saved with counts/metadata. No reference or tests from heldout tasks enters training. No correctness filtering in training.

## Data interfaces (plain dictionaries serialized as JSONL)

Task: task_id:str, prompt:str, reference:str (optional except calibration), tests:str (optional except builtin verification), entry_point:str (optional), source:str, split:str. Optional calibration_spans:list[[start,end]] are character intervals in reference. Identifiers are namespaced. Split assignment is deterministic; prompt fingerprints across splits are checked. Real dataset downloads are opt-in commands, never import side effects.

Completion: task_id:str, sample_id:int, completion:str, optional prompt_tokens:int, generation_tokens:int, seed:int, round:int, method:str, finish_reason:str. Persist every sample including invalid/wrong/empty completions. Duplicate (task_id,sample_id) keys are errors.

Verified completion: completion record plus code:str, correct:bool, status:str; optional strategy_id:str comes from independent evaluation annotation, never training. AST hash is named implementation proxy, never algorithm diversity. Algorithms require externally audited labels.

Metrics: unbiased hypergeometric pass@k; expected number of distinct correct strategy IDs / AST fingerprints in k draws WITHOUT replacement from n samples; same metric at fixed correct-count budget; entropy over correct labels; task macro averages and task-bootstrap CIs; sample budget validity, zero-correct and unavailable labels explicit. Compare runs with identical task IDs, sampling budgets and protocol. Cross-round retention uses stable labels only. No adaptive stopping on favorable seeds.

## Execution

Python package `improving`, modules data.py (I/O + dataset prep), verification.py (explicit subprocess/docker plus EvalPlus bridge), metrics.py (pure statistics), spectral.py (operators/folding), calibration.py (gradient collection), modeling.py (HF load + tokenization), generation.py, training.py, pipeline.py, cli.py. Config YAML supports model, paths, methods, rounds, generation, calibration, train, evaluation and seed. Parent owns all modules except delegated file groups below.

The default profile is Qwen2.5-Coder-1.5B-Instruct, BF16 on compatible CUDA, LoRA r8, batch1 + gradient accumulation, lengths configurable. No GPU job is launched by this development task. CPU tests use tiny random models and fixtures; those are correctness tests, not research results.

## File ownership

Data worker: data.py, verification.py, tests/test_data.py, tests/test_verification.py only.
Metrics worker: metrics.py, tests/test_metrics.py only.
Spectral worker: spectral.py, calibration.py, tests/test_spectral.py, tests/test_calibration.py only.
Root: all other files, integration, docs, configuration, remote push.

## Validation

Analytic spectral limits and covariance eigenvalues; real linear-output versus folded-weight logits on a tiny model; masked token shift and padding; gradient collection with frozen parameters; exact enumerated finite-sample coverage; invalid programs/timeouts; split contamination and incomplete sample groups; tiny end-to-end calibration/generation/LoRA update/checkpoint reload. GPU performance and semantic-label quality remain unmeasured.
