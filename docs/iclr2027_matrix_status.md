# Cross-model baseline matrix status

Final matrix status: 2026-09-22 12:26 UTC. The four-model by five-benchmark matrix uses seed 43, 16 samples per task on the four transfer benchmarks, and the existing 64-sample MBPP baselines. The reported cross-model metric is Pass@16. The 20-cell result table with 95% bootstrap intervals is in [iclr2027_matrix_pass16.csv](iclr2027_matrix_pass16.csv).

Models: Qwen2.5-Coder-1.5B-Instruct, DeepSeek-Coder-6.7B-Instruct, Gemma-3-4B-IT, and Qwen3-8B. Benchmarks: MBPP, HumanEval+, APPS Intro, CodeContests, and LiveCodeBench.

All twenty model-benchmark cells have completed generation and verification. The Gemma × LiveCodeBench task used eager attention after SDPA failed on an attention-bias alignment error; its successful output directory is `runs/matrix_gemma3_4b_livecodebench_seed43_n16_eager`. MBPP metrics are Pass@16 estimates from 64 samples per task; transfer metrics use 16 samples per task. HumanEval+ uses official EvalPlus verification; the other transfer benchmarks use the prepared native adapted verifiers.

Authoritative local state is `runs/a6000_control/queue.json`, `runs/a6000_control/status.json`, and each run's `matrix_complete.json` or `baseline_only_complete.json`. The `runs/` tree is excluded from Git because it contains generated data and model artifacts; consult the private Hugging Face backup for large archived artifacts. This snapshot does not claim that the full training-method experiment is complete.
