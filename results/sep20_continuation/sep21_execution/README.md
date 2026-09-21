# September 21 execution update

The user authorized all remaining runs, including independent 64-sample evaluations. Ten n64 evaluations are queued with seed43, sequence batch8 and a 5120 MiB CUDA allocator cap. Existing n16 runs remain separate.

The stalled HumanEval+ process was stopped after preserving its partial output. Longest-prompt CodeContests and LiveCodeBench batch8/1024-token diagnostics passed. Both n16 migration retries have started. Large-model training remains resource-gated; queued does not mean started. UA-RL still requires an external judge configuration.

Existing n16 multi-answer metric exports were published at commit 84d89bccea8aa2048753f4779d23563898190512.
