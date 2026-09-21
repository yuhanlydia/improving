# September 20 execution protocol

The requested scope is SSD on full MBPP for five rounds, four transfer benchmarks,
Qwen 3B / Qwen 7B / DeepSeek 6.7B expansion, and UA-RL. The later request to finish
all experiments supersedes the initial twelve-hour scheduling window. This file
records execution choices, not completed experimental results.

The initial MBPP protocol used seed 43, 16 training candidates, 16 evaluation samples, and
five rounds. The September 21 update in EVALUATION_POLICY.md uses n64 for new
evaluations and unstarted expansion runs; existing runs retain their frozen budgets. Prepared MBPP splits are 291 train / 50 calibration / 30 validation /
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
revisions, file identities and recovery metadata. For new DeepSeek single-method
runs, base tensors can be repacked into matching shard layouts without changing
tensor bytes, then used as delta references. The reference manifest and frozen
recovery tools are retained beside the archive, and a cold reference rebuild and
full byte verification must succeed before pruning. Existing gzip archives remain
supported. This path has CPU fixture coverage; real DeepSeek memory and compression
measurements are still pending. Restoring an archive requires verifying every
reconstructed file before evaluating it.

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

UA-RL dependencies and a real local CPU Qwen7B semantic judge have been validated.
The judge is loaded on demand; training admission must respect the actual 31 GB
cgroup memory limit and GPU capacity. Its measured small-request CPU latency was
107.95 seconds, so readiness does not imply fast completion.

## APPS batch adaptation after measured SSD memory growth

Before any APPS research output was generated, its generation batch was reduced
from 64 to 8. The new run is `sep20_transfer_apps_intro_seed43_n16_b8`;
all 200 tasks, 16 samples per task, seed 43, checkpoints, decoding parameters and
1024-token generation limit remain unchanged. All four APPS arms use batch 8.

SSD round-two SFT peaked at 4,320,920,064 allocated CUDA bytes but retained
15,814,623,232 reserved bytes. The scheduler therefore could not safely admit
the original APPS allocation alongside it. A separate stress test used the longest
prepared APPS prompt (1353 tokens) and forced 1024 generated tokens per sequence;
these forced outputs are not research samples. Under a 4608 MiB allocator cap,
batch 8 completed in 45.924 seconds with a sampled process peak of 4676 MiB.
Batch 16 exhausted that allocator cap and exited without stopping SSD.

The APPS process uses the same 4608 MiB allocator cap through
`run_with_cuda_cap.py`. This cap excludes some CUDA allocations; the scheduler
budgets 5120 MiB for the process and retains 3500 MiB of SSD growth headroom.
PID sampling can miss subsecond peaks. Evidence and wrapper identity are recorded
in `resource_preflights/sep20_apps_batch.json`; the frozen experiment implementation
was not edited. Historical-cache cleanup now waits for this new APPS output.
