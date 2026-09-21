# 换卡备份状态

代码、配置、29项后续实验任务、紧凑结果和恢复说明保存在 GitHub。SSD 权重、原始答案、准备后的数据和完整迁移包已上传到私有 Hugging Face 仓库，并逐文件校验完成。下载链接、固定 revision 和校验结果见 [HUGGINGFACE_BACKUP.md](HUGGINGFACE_BACKUP.md)。

## 已完成的评估

- SSD 全量 MBPP 五轮。
- 历史模型 HumanEval+ 四组、APPS Intro 四组。

## 尚未完成

- CodeContests：保存232个基座答案。
- LiveCodeBench：保存288个基座答案。
- 新64样本评估、模型扩展、UA-RL尚未启动。

目前所有GPU实验进程已停止。停止不代表评估完成。

GitHub 上原有的软件包、暂停状态包与 run_task_snapshots 分片保留；其他大包的旧分片仍不完整。全部完整迁移包从 Hugging Face 下载，SHA256 已与 ARCHIVES.json 核对。源文件保留，本次未重启任何实验。
