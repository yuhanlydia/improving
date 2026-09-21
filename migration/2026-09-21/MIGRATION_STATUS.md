# Migration backup in progress

Source repository: yuhanlydia/improving. Backup date: 2026-09-21 UTC.

The user requested all current results and future experiments be backed up before changing GPUs. GPU generation has been stopped deliberately, with completed atomic shards preserved. Scheduler dispatch is paused. A failed exit caused by this planned stop is not a completed evaluation.

Main evaluation policy: pass@16/pass@64 and correct implementation coverage@16/@64; pass@1 retained in appendix/raw records. New unstarted expansion configurations use eval64, train16, seed43, five rounds. All 29 scheduled tasks and runtime dependencies are included in the migration package.

This status is provisional: do not delete the original machine until the final remote verification manifest states all required files are uploaded and verified. Model weights, raw results, and task snapshots require the binary backup chunks, not only previously published compact results.
