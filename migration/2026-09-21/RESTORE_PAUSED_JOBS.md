# Migration pause and restart

All research and known mutating controller/cache/archive/publisher workers are stopped. GPU dispatch remains zero. No files were deleted. See processes_before.json for verified original PIDs/argv, final_status.json for original exit records, preserved_parts.json for completed atomic shard hashes, and tasks_all_29.json for the full executable queue and dependencies. CC/LCB exit -15 is the requested migration interruption, not a new experiment failure.

## Restore safely

1. Restore repository, all operational scripts, frozen runtime snapshots, datasets, historical checkpoint patches, SSD round5 checkpoint, results including evaluation.jsonl.parts manifests and shards, configs and pinned environments. Git source alone does not contain local model/data/results artifacts. Verify backup hashes. Retain exact task IDs, original selected tasks, seeds, 16/64 sample counts and existing batch8 shape when resuming shards.
2. Keep settings.max_gpu_processes=0. Verify the actual new GPU and cgroup RAM/disk; old measured 3090 budgets do not establish a new GPU batch recommendation. All absolute argv/marker paths assume /root/improving; restore there or consistently translate every queue, manifest and worker configuration. Never copy old live PID identities into new machine checks.
3. Preserve final_status.json as immutable attempt history. status.resume_proposal.json deliberately removes ONLY the two intentionally interrupted b8 CC/LCB records so the controller can dispatch their existing --resume commands. The scheduler skips ANY task ID already in status.tasks, including failed/interrupted: simply restarting it would not resume these jobs. Validate all completed markers and file hashes on the destination before installing this proposal as status.json. Other prior failed b64 attempt records stay preserved and are not queued.
4. Clear/neutralize obsolete PIDs in ssd_launch.json, archive launch records, judge service records and controller state on the destination AFTER recording originals; reused OS PIDs are not experiment identity. SSD is already completed, so no external SSD reservation should be live. The sample proposal neutralizes scheduler record PIDs but is NOT a blanket replacement for checking all launch files. Cache release workers require task completion and exited identities; do not delete cache merely because a historical machine PID appears absent.
5. Run dependency audit and read-only gpu_queue.py --once. Three model configuration_ready markers require genuine batch-probe report/config-hash review on the target hardware. Scale research configs now eval64 although compatible paths retain eval16; probes remain separate16. Preserve historical weights through five historical64 evaluations, SSD round5 through five SSD64 evaluations, and Qwen7B base through all three model runs plus UA completion/judge exit.
6. Restore CPU judge on demand through ua_managed_runner.py, not as a permanent competing service. RAM gates use the container limit. Restart archive/cache services only after validating destination paths and completion state. Publisher must use .venv/bin/python to retain deterministic gzip bytes. Git CLI authorization currently fails; reauthorize securely or use the connector fallback. Do not upload credentials.
7. Only after validation choose target GPU concurrency, set settings.max_gpu_processes accordingly and launch one controller. Resume publication from publisher_status.json; only real complete/hash-verified stages can be published as complete. Partial shards are migration evidence, never completed benchmark results.

## Queue snapshot

| Task | Migration state | Priority | Missing prerequisites |
|---|---|---:|---:|
| transfer_humanevalplus_b64 | completed_verified | 10 | 0 |
| transfer_apps_intro_b8 | completed_verified | 11 | 0 |
| transfer_codecontests_b8 | paused_resumable | 12 | 0 |
| transfer_livecodebench_b8 | paused_resumable | 13 | 0 |
| scale_qwen3b | pending | 30 | 1 |
| transfer_ssd_humanevalplus_b8 | pending | 20 | 0 |
| transfer_ssd_apps_intro_b8 | pending | 21 | 0 |
| transfer_ssd_codecontests_b8 | pending | 22 | 0 |
| transfer_ssd_livecodebench_b8 | pending | 23 | 0 |
| scale_qwen7b_plain | pending | 31 | 3 |
| scale_qwen7b_ssd | pending | 32 | 1 |
| scale_qwen7b_spectral_soft | pending | 33 | 1 |
| scale_deepseek6_7b_plain | pending | 34 | 3 |
| scale_deepseek6_7b_ssd | pending | 35 | 1 |
| scale_deepseek6_7b_spectral_soft | pending | 36 | 1 |
| batch_probe_qwen3b | pending | 29.5 | 0 |
| batch_probe_qwen7b | pending | 30.5 | 2 |
| batch_probe_deepseek6_7b | pending | 33.5 | 2 |
| eval64_historical_mbpp_b8 | pending | 40 | 1 |
| eval64_historical_humanevalplus_b8 | pending | 41 | 1 |
| eval64_historical_apps_intro_b8 | pending | 42 | 1 |
| eval64_historical_codecontests_b8 | pending | 43 | 1 |
| eval64_historical_livecodebench_b8 | pending | 44 | 1 |
| eval64_ssd_mbpp_b8 | pending | 45 | 1 |
| eval64_ssd_humanevalplus_b8 | pending | 46 | 1 |
| eval64_ssd_apps_intro_b8 | pending | 47 | 1 |
| eval64_ssd_codecontests_b8 | pending | 48 | 1 |
| eval64_ssd_livecodebench_b8 | pending | 49 | 1 |
| ua_rl_adapted_seed43_eval64 | pending | 30.1 | 0 |
