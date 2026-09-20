# September 20 execution protocol

The requested scope is SSD on full MBPP for five rounds, four transfer benchmarks,
Qwen 3B / Qwen 7B / DeepSeek 6.7B expansion, and UA-RL. The later request to finish
all experiments supersedes the initial twelve-hour scheduling window. This file
records execution choices, not completed experimental results.

All new MBPP runs use seed 43, 16 training candidates, 16 evaluation samples, and
five rounds. Prepared MBPP splits are 291 train / 50 calibration / 30 validation /
500 evaluation tasks. Existing historical checkpoints provide the initial Plain,
SPECTRUM and Projection transfer arms. New SSD round-five checkpoints are queued
for the same four transfer benchmarks. Transfer task counts are HumanEval+ 164,
APPS Intro 200, CodeContests 165, and LiveCodeBench 200, with 16 samples each.

## Model expansion and disk scheduling

Qwen 3B runs Plain, SSD and SPECTRUM together using
`configs/sep20_scale_qwen3b_seed43_eval16.yaml`.

Qwen 7B and DeepSeek use one complete five-round run per method, in the order
Plain, SSD, SPECTRUM. The corresponding configuration names are:

- `configs/sep20_scale_qwen7b_{plain,ssd,spectral_soft}_seed43_eval16.yaml`
- `configs/sep20_scale_deepseek6.7b_{plain,ssd,spectral_soft}_seed43_eval16.yaml`

These configurations differ from the initial grouped configuration only in
`methods` and `output_dir`. Seeds, datasets, sampling, training and calibration
settings remain identical. Each method run generates and evaluates its own base
samples. Base computation is repeated; no base results are copied or fabricated.
The original grouped 7B and DeepSeek configurations remain as initial protocol
references and are not scheduled in addition to the single-method runs.

Before starting the next method, the completed final checkpoint is archived,
actually decoded and compared against every original file SHA256, then pruned
through the pipeline's existing checkpoint-retention bookkeeping. All results and
original checkpoint hashes remain available. Archives record immutable base
revisions, file identities and recovery metadata. DeepSeek checkpoints whose
shard names differ from the base use lossless gzip instead of a delta. Restoring
an archive requires verifying the reconstructed files before evaluating it.

Launch thresholds include two simultaneous checkpoint generations, five rounds
of calibration artifacts where applicable, and 5 GiB of additional disk space.
They are approximately 33.4 GiB for Qwen 7B, 30.1 GiB for DeepSeek Plain/SSD, and
37.6 GiB for DeepSeek SPECTRUM. Actual free space is checked before dispatch.
Only reproducible, pinned Hugging Face download caches may be rotated after
all dependent evaluation or archival tasks have finished.

Generation batches are sized for the local 24 GB GPU. Concurrent jobs are only
launched when measured free GPU memory and disk space satisfy their gates.
Completed base evaluations, rounds, and benchmark parts are published separately
after evidence validation. Generated programs, model weights and raw datasets
are kept out of Git result bundles.

UA-RL dependencies are installed, but an explicit semantic-judge service
configuration is still required before that method can start.
