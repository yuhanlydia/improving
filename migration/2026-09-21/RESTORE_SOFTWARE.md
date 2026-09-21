# September 21 experiment migration: code, configuration, and evidence

This is the preparation bundle for continuing all 29 scheduled tasks. It does **not** contain model weights, benchmark snapshots, generated programs, optimizer state, or completed experiment result archives. Those state/data packages must be restored separately before any GPU work resumes. No experiment completion is implied by a configuration or readiness record.

## Contents

- `repository_overlay/`: source-relative files to restore under `/root/improving`; current source, tests, scripts, configs, docs, control tools, and six frozen execution runtimes.
- `repository_overlay/runs/sep20_control/`: GPU controller, RAM guard, managed UA launcher, real CPU judge, independent n64 evaluator, publisher/API publication helper, checkpoint archive/reconstruction tools, cache rotation and dependency audits, and their tests. Control settings remain paused as copied; no queue was changed during packaging.
- `evidence/control_snapshot/`: CPU audits, old task status/launch records, probe evidence, retention requirements and prior configuration changes. **Old PIDs, locks and service-ready records are not valid on a new machine.** These are evidence, not files to blindly reinstate as live process state.
- `evidence/ua_judge_real_smoke_cache/`: actual Qwen7B semantic partition response to a synthetic public problem. No credentials are present.
- `TASKS_29.json`: exact queue snapshot, including commands, output directories, dependency paths, completion checks, and resource thresholds.
- `core_dependencies_observed.json`, `ua_dependencies_observed.json`: package versions observed on the source host. The UA environment is separate because its Transformers/PEFT/TRL versions differ from core training.
- `FILES_MANIFEST.json`: byte sizes and SHA256 for each payload file. Frozen runtime content receives the same per-file checksums; its original implementation checksum files are also preserved where available.
- `SECRET_SCAN.json`: allowlist/exclusion and secret-pattern scan evidence. Logs, `.env`, auth stores, environment dumps, raw process command lines, bootstrap logs, virtualenvs and model caches were excluded.

## Restore without accidentally dispatching work

1. Clone the GitHub repository and restore this overlay at **`/root/improving`**. Preserve this path if possible: queue commands, wrappers, frozen runtime imports, source manifests, archive references and cache locations contain absolute `/root/...` paths. The publication checkout is `/root/improving-result-publisher`; Hugging Face models use `/root/.cache/huggingface/hub`.
2. Verify every payload file against `FILES_MANIFEST.json` before copying. Restore the separately supplied benchmark/task snapshots, experiment directories, evaluation `.parts`, manifests/completion records, saved checkpoints and lossless archives. Archive tools are included but this bundle is not itself a checkpoint archive.
3. Recreate Python 3.11 environments. In `/root/improving`, create `.venv` and install the core package with its train/evalplus/test extras, respecting `core_dependencies_observed.json` and the installed Torch/CUDA compatibility. Create `.venv-ua-rl` separately, install `requirements-ua-rl.txt`, then `pip install --no-deps -e .`. Do not install UA packages over the core environment. Provision ordinary `git`, `nvidia-smi`, and optional authenticated `gh` separately; no credentials are in this package.
4. Restore/redownload the exact model revisions referenced by task configs and manifests. Qwen1.5B base is `2e1fd397ee46e1388853d2af2c993145b0f1098a`; historical students are `humanlong/improving-self-evolution-mbpp@4f56c88502ebba3a1ad856fc59831ace3d9b53ee`. Qwen7B judge/base is `c03e6d358207e414f1eca0bb1891e29f1db0e242`. Use the scale configs for Qwen3B/DeepSeek revisions. Offline-mode tasks require all weight shards and tokenizer/config files locally.
5. Keep `settings.json` dispatch paused (`max_gpu_processes: 0`) until dependency and state audits pass. Do not start the old handoff script: it refers to source-host PIDs. Keep source `status.json`, service/launch records, locks and archive watcher records in the evidence directory. Reconstruct fresh scheduler state from verified result/completion markers, not from whether an old PID number happens to exist.
6. Audit each task's `requires_paths`, completion checks and disk/RAM needs. Some dependencies are operational archive/probe markers: verify or rebuild their actual artifacts before restoring the marker. A stale readiness JSON must not stand in for a live service. Existing same-protocol generation chunks can be resumed with their original frozen runtime and command. Do not alter frozen sampling settings or implementation hashes for an existing output directory; use a new output directory for any new protocol.
7. Re-run CPU checks and hardware probes as applicable. Only then unpause and launch `runs/sep20_control/gpu_queue.py`. Start one controller per actual supported scheduling design, as detailed below. Start archival/cache workers only after their dependencies are audited. Publishing requires a newly authenticated GitHub connection or Git CLI credentials; `publish_part_connector.js` is a Codex connector orchestration snippet, not a standalone Node program.

If `/root/improving` cannot be retained, first inventory all absolute paths in queue, configs, Python launch wrappers, manifests and archive references. Create an explicit old-to-new path mapping and review every change. Preserve historical provenance unmodified in evidence. Resume validators may reject edited manifests/protocols; do not bypass these checks. Merely editing the queue `cwd` is insufficient.

## Task coverage and scientific settings

The 29-task queue includes eight n16 transfer tasks (historical/base and SSD/base across four benchmarks), seven scale training tasks, three scale throughput probes, ten independent n64 evaluation tasks, and one UA-RL task. The task names ending `b64` historically referred to sequence batch size, **not** samples per problem; inspect `--samples` and output population names.

The ten new n64 tasks use independent `n64_b8` output directories, seed43, five-round final students and real base evaluations. MBPP uses prompt1024/completion512; transfer uses prompt4096/completion1024. Do not concatenate n16 outputs into n64 as if they were one matched sampling run. Raw metrics retain pass@1; the current report source places pass@16/pass@64, correct AST coverage@16/@64, and fixed-correct diversity in the main presentation. Frozen execution/report code remains unchanged to preserve in-flight protocols.

UA uses 291 train tasks, 16 candidates per group, five training epochs and 64 evaluation samples on 500 MBPP test tasks. Its genuine semantic judge uses all candidates and no correctness labels/tests. Actual CPU smoke passed (two equivalent formulas grouped, loop separated), with 275 input and21 output tokens in107.95 seconds. This establishes connectivity and one semantic sanity check, **not** broad judge quality or full16 throughput. CPU judging can dominate total runtime; no12-hour completion claim is made.

The UA final `complete.json` has `method`, `rounds`, and `final_model`, **no `status` field**. Its queue checks intentionally match that schema. Transfer completion markers have `status: completed`, `benchmark`, and `samples_per_task`; n64 completion checks require64. Keep these distinctions when rebuilding scheduler/publisher state.

## 4 x RTX4090

The copied controller is currently a **single-physical-GPU0 scheduler**. It calls `nvidia-smi --id=0`; changing `settings.gpu_index` or only setting `CUDA_VISIBLE_DEVICES` does not by itself turn it into a safe four-GPU scheduler. Four24GiB cards do not make a single model's address space96GiB, and UA explicitly rejects DDP.

Before using all four cards, implement and test explicit physical-device selection in both GPU telemetry queries and task launch environments. A practical adaptation is one controller per physical GPU with distinct control/status/lock/log directories and disjoint task lists, setting each task's `CUDA_VISIBLE_DEVICES` to that GPU. Every GPU process then sees its assigned device as logicalCUDA0. Alternatively implement one multi-GPU controller; this has not been done here. Do not run four copies sharing one `status.json` or leave all telemetry pointed atGPU0.

Suggested independent assignments, after dependencies are satisfied: one card for scale training; one for frozen-checkpoint evaluation; one for UA student training; one reserved for a separately validated GPU judge or more evaluations. The current judge is CPU-only; a GPU judge requires an actual serving implementation, memory preflight, identical documented semantic interface and a new judge identity/provenance. No GPU judge is included or asserted tested.

Shared RAM, disk and cache deletion remain global resources. Retain a single coordinated archive/cache/publisher owner, shared dependency evidence, and a global RAM admission rule across controllers. Re-probe memory/throughput on4090 before raising batches; previous3090 estimates are not guarantees.

## A100

Confirm whether the device is40GiB,80GiB or a MIG slice, and measure the container's actual memory limits. The current queue can continue its conservative single-GPU design on physicalGPU0 after state restoration. Do not automatically increase batch sizes inside existing output populations. New faster profiles need new output directories and recorded sampling/provenance because batch layout affects random generation.

Greater GPU memory can make isolated scale training and possibly a genuine co-resident judge feasible, but those combinations are not yet validated. Keep the CPU judge managed on demand until a replacement passes real tests. Check BF16/CUDA/driver compatibility with the pinned environments before launching training.

## Memory, disk and retention

The source host exposed about188GiB host RAM but its container cgroup limit was about31GiB. **Use `ram_guard_runner.py` cgroup measurements, not `free -h`, for admission.** The managed UA launcher loads CPU Qwen7B only on demand and stops its own judge after the attempt. Qwen7B cached shards must remain until UA finishes and the judge exits; memory-mapped deleted files may otherwise keep disk space occupied.

Historical model cache deletion is gated by the original transfer work plus five historical n64 tasks. SSD round5 must remain through its five n64 tasks; the intermediate archive worker handles only rounds1–4. Scale archiving has separate per-run gates. Do not bypass these to start later scale tasks.

LiveCodeBench's full prepared eval snapshot is about2.43GB. Existing identical snapshots may be safely hardlinked only after byte identity is established; generation outputs and manifests must not be merged. Each n64 LCB task currently requests10GiB free disk; other n64 tasks request4GiB. Keep training's larger safety margins. Provision substantially more disk than the source100GB if possible; downloaded bases, retained checkpoints, optimizer state, raw outputs and recoverable archives all count.

## Verification scope

Packaging verified the29-task count, allowed file types, absence of copied logs/credential stores, secret-pattern matches, structured credential fields, and per-file hashes. A JSON field called`authorization` in `SCALE_EVAL64_CONFIG_CHANGE.json` contains a narrative user-authorization note, not a credential. This package has not been boot-tested on the destinationGPU. Source-host readiness/service records are timestamped evidence, not destination validation.
