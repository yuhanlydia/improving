# Cross-model baseline matrix status

Snapshot: 2026-09-22 06:02 UTC. The active four-model by five-benchmark matrix uses seed 43, 16 samples per task on the four transfer benchmarks, and the existing 64-sample MBPP baselines. The reported cross-model metric is Pass@16.

Models: Qwen2.5-Coder-1.5B-Instruct, DeepSeek-Coder-6.7B-Instruct, Gemma-3-4B-IT, and Qwen3-8B. Benchmarks: MBPP, HumanEval+, APPS Intro, CodeContests, and LiveCodeBench.

Eighteen of twenty model-benchmark cells have completed generation and verification. The remaining cells are DeepSeek × LiveCodeBench (280/800 generation batches) and Gemma 3 × LiveCodeBench (297/800 batches). The Gemma task uses eager attention after SDPA failed on an attention-bias alignment error; its new output directory is `runs/matrix_gemma3_4b_livecodebench_seed43_n16_eager`.

Authoritative local state is `runs/a6000_control/queue.json`, `runs/a6000_control/status.json`, and each run's `matrix_complete.json` or `baseline_only_complete.json`. The `runs/` tree is excluded from Git because it contains generated data and model artifacts; consult the private Hugging Face backup for large archived artifacts. This snapshot does not claim that the full training-method experiment is complete.
