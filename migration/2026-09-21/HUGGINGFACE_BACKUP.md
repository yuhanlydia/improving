# 大文件 Hugging Face 备份

- 仓库：[humanlong/improving-backup-20260921](https://huggingface.co/datasets/humanlong/improving-backup-20260921)（私有，使用有权限的 Hugging Face 账号登录）。
- 已校验 revision：`b13e9e2b672c8c2149041623a306eb059e8aa80b`。
- 对应代码提交：`5bc6575bd0cf1aa7c4d05e60e3a41ac77fbd12c1`。
- 校验时间：2026-09-21T06:43:30.806617+00:00。
- 实验载荷：9,312 个文件，18,050,046,827 字节（按路径计，包含硬链接的重复逻辑大小）。
- 连同 README、清单和校验文件，远程核对 9,315 个文件；路径、大小与内容哈希全部匹配。

## 文件分工

GitHub 保存代码、配置、论文、文档、紧凑结果和本索引。Hugging Face 保存 `project/runs/` 与 `project/data/` 的实验载荷及恢复所需的伴随文件：SSD 五轮无损权重归档、仍保留的完整检查点、原始生成结果、评估分片、准备后的数据集、冻结运行代码、控制状态和完整迁移包。

不上传本机凭据、Git 内部文件、虚拟环境和可重建缓存。外部 EvalPlus oracle/timing cache 已包含在 `extra_reproducibility.tar.gz`；公开基座模型按 `DOWNLOAD_PINNED_RESOURCES.sh` 的固定 revision 重新下载。

旧 GitHub `chunks/` 仍有未完成的大包分片。完整大文件以这里的 Hugging Face revision 为准。备份完成不代表 CodeContests、LiveCodeBench 或尚未启动的新实验已完成；已有暂停记录保持原样。

## 下载和检查

```bash
hf auth login
hf download humanlong/improving-backup-20260921 --repo-type dataset --revision b13e9e2b672c8c2149041623a306eb059e8aa80b --local-dir improving-backup
cd improving-backup
sha256sum -c SHA256SUMS
```

从 GitHub 获取上述代码提交，再将备份的 `project/runs/` 和 `project/data/` 恢复到项目目录。`BACKUP_MANIFEST.json` 保存原始 mode 和硬链接关系；需要时恢复可执行权限和硬链接。恢复环境、权重及暂停任务分别参见 `RESTORE_SOFTWARE.md`、`MODEL_DATA_RECOVERY.md` 和 `RESTORE_PAUSED_JOBS.md`。本次没有重启 GPU 实验，也没有删除源文件。

## 已校验的完整迁移包

这些文件位于 Hugging Face 的 `project/runs/migration_sep21/` 下，SHA256 同时与 GitHub 原有 `ARCHIVES.json` 一致。

| 文件 | 字节 | SHA256 |
|---|---:|---|
| `extra_reproducibility.tar.gz` | 88,826,773 | `776fce4838f40a70b5dcb361899ca999406f7b01fd3d07e421bf2f76306644ed` |
| `paused_execution_state.tar.gz` | 28,097 | `c4f97f60003f064bf0b79518d83cf6ba9e72a79bd07f1af190821da66749f1ba` |
| `results_and_prepared_data.tar.gz` | 1,007,288,356 | `dab52bd4d64fa5c132fe45583f3cfb8bb01699762ca9290aa4f730fcd1f46d89` |
| `run_task_snapshots.tar.gz` | 10,811,115 | `7b507d30d5985fadb6800a17b4c8b8790c285343e92a1dd33053d0ba5d4a6871` |
| `software_and_future_experiments.tar.gz` | 1,157,607 | `777d15fcb8235f79d7ed725f3ba83fefb1c723d49dcab6dd5e63dc5dd399b666` |
| `ssd_five_round_checkpoints.tar` | 1,317,386,240 | `543f88c1442d505739804aaac300949a32154a42a0c00cbe02c3070152f5dd56` |
