> Historical planning record. The active September 20 experiment and evidence matrix is in `experiments/iclr2027/README.md`; the current manuscript is `paper/iclr2027/main.tex`.

# SPECTRUM：待完成实验与执行顺序

## 当前状态与固定协议

本文的 **SPECTRUM 对应代码 `spectral_soft`**。目前完成的只有 seed 42、1.5B、64 道 MBPP 题、单轮 pilot；它不进入正式确认的汇总。下列实验全部待跑，`main.tex` 的 `tab:pending` 不代表已有分数。本清单依据 improving 的 `origin/main` 提交 `d8a50903de671cdb7e5c23a28ff43de1c32c16b5`、`docs/formal_protocol.md` 与配置文件。

主线使用 `configs/formal_16gb.yaml`：Qwen2.5-Coder-1.5B-Instruct，291 道合成训练题、50 道校准题、30 道预留验证题、500 道 MBPP 测试题；实际数量以数据 manifest 为准。`data_seed=42` 固定题目划分，正式训练种子为 43–47。冻结 τ=1、hard rank fraction=0.5、`first_fence`、每题64个评估样本及统一后训练解码。每轮每道训练题只采一个原始回答，错误和空回答也进入相同 LoRA 流程。一次训练的5个 epoch 不等于5轮自蒸馏。

## 核心实验：先完成这四项

以下新图表标签是预留位置，尚未生成；完成后替换 `tab:pending` 对应行。

| 顺序／问题 | 固定比较 | 支持条件与否证方向 | 结果位置 |
|---|---|---|---|
| 1．效果能否复现？ | 43–47五种子、单轮；Plain、SSD、SPD-hard、SPECTRUM，另评估原始模型 | 对 Plain 和 SPD-hard 分别满足：配对 ΔD₄ 区间下界>0，且全题 pass@1 差值下界≥−0.01。若未同时满足，确认未通过；区间明确显示下降则支持相应反方向 | `tab:confirm`、`fig:confirm`：效果量、区间、每种子与合格题数 |
| 2．是否来自谱结构？ | 43–45三种子增加 `matched_blend`、`random_soft`、`isotropic_soft`，与确认阶段相同种子的 SPECTRUM 比较 | 对 random 的优势支持学习到的方向；对 blend 的优势支持连续增益；对 isotropic 的优势支持结构化过滤。区间无法区分则该机制未获支持，不能把“不显著”写成等效 | `tab:mechanism`、`fig:mechanism`：三种对照的配对效果 |
| 3．能否跨轮保留？ | 43–45三种子；Plain、SPD-hard、SPECTRUM；原始模型及1–3轮 | 稳定共同题集上的优势持续且准确率满足约束，支持三轮内保留；优势消失或明确逆转则削弱该命题。逐轮题集变化不能冒充同题多样性衰减 | `fig:retention`：准确率、D₄和题集规模随轮次变化 |
| 4．能否迁移到新题？ | 43–47五种子的原始模型与四个确认末轮模型；全164道 HumanEval+，每题64样本，官方 EvalPlus 0.3.1 | 按预先固定的准确率约束与配对覆盖率规则检验方向；失败则将结论限定于 MBPP。此项是第二基准证据，不能替代确认主检验 | `tab:transfer`、`fig:transfer`：base/plus正确率与条件覆盖率 |

确认的两种比较×两个端点构成四项主检验：使用 Bonferroni 校正的98.75%单项双侧区间，种子与题目交叉重采样并保留方法配对。SSD、D₈/D₁₆、pass@8/32/64等为次要结果；控制和迁移的区间不冒用主检验的家族保证。

每轮还配置了干预生成策略的128题×32样本诊断，用于区分“生成时出现”和“LoRA后保留”。它不能替代500题末轮评估，也不能报告 pass@64。SSD干预阶段的解码不同，解读时保留这一条件。

## 在 GPU 机器上执行

在固定版本的 improving 仓库根目录执行；需要 BF16 CUDA、Python 3.10+ 和 Docker。以下是交给操作者的命令，本次写作未运行模型。

```bash
python -m pip install -e '.[train,test,analysis]'

# 核对数据、配置和候选数量；首次可能准备数据。
bash scripts/run_formal.sh configs/formal_16gb.yaml validate

# 默认只跑确认；先检查其结果，再继续其余核心阶段。
bash scripts/run_formal.sh configs/formal_16gb.yaml confirm
bash scripts/run_formal.sh configs/formal_16gb.yaml mechanism
bash scripts/run_formal.sh configs/formal_16gb.yaml retention
bash scripts/run_formal.sh configs/formal_16gb.yaml transfer

# 只重建报告和证据包，不运行模型。
bash scripts/run_formal.sh configs/formal_16gb.yaml report
bash scripts/run_formal.sh configs/formal_16gb.yaml export
python -m improving formal --config configs/formal_16gb.yaml \
  --stage export --resume --include-programs
```

Retention从原始模型独立启动三轮轨迹，第一轮在该轨迹内重跑，不追加到已经封存的确认目录。运行期间固定代码、配置、解码 batch 与输出目录；改协议另开目录。当前配置全套上限为2,652,072个候选，并非实际生成 token 或耗时估计。先跑确认，避免直接启动 `all`。

## 尚需人工完成的两项协议

**稳定跨轮题集分析尚未自动化。** 从逐题结果构建同一种子、所比较方法、全部比较轮次均有至少4个正确样本的交集；若包括base，也要求base合格。报告交集ID、题数、每轮进入／退出数，并同时展示逐轮交集结果。保留空交集和缺失值，不能填零。该分析填入 `fig:retention`，之后才能判断同题覆盖率是否流失。

**盲法算法标注尚未自动化。** 建议新增有界协议：固定种子43，从测试题中预先抽取40题；SPECTRUM、Plain、SPD-hard每题各抽至多8个正确程序，最多960个程序。抽题和程序抽样规则在揭示方法前固定，不足4个正确样本的配对记为不合格并报告题数。去除方法／种子标签，两名标注者按计算策略、数据结构与复杂度独立标注，再裁决分歧。导出程序后可借助已有 `annotate`／`metrics` 接口计算算法标签D₄，但标签必须来自实际标注。预留 `tab:algorithm`；若AST差异没有对应算法差异，保留“结构多样性”的结论。单种子标注是语义解释的探索性证据，不替代五种子确认。标注不改变训练样本或模型。

## 必须回收的证据与后续边界

每个种子／方法／轮次／题目保存样本总数n、正确数c、正确AST类计数cⱼ、原始程序及执行标签。每个配对、每个正确预算都需导出共同合格题目的**ID与数量**；旧pilot README缺少这些分母，单独的均值和哈希不足以复算区间。还需报告种子效应、配置／数据／模型标识、实际token、耗时与峰值显存。主要产物在 `runs/formal_spectral_16gb_v1/report/`；分享 `evidence/compact.tar.gz`，标注另用 `evidence/programs.tar.gz`。

交付前逐项对照运行状态：缺失种子或轮次仍标待完成，不能以零分代替；逐题文件必须能重算配对效果和共同分母。完成这一批固定比较后据结果改写论文，不因结果不理想反复换种子、指标或抽样规则。

先完成核心，再决定扩展：3B配置 `formal_24gb.yaml` 已有但未跑；5轮和10轮的 `retention_5round_32gb_local.yaml`、`retention_10round_32gb_local.yaml` 也是未跑的探索性设置，使用本地执行后端，不能与Docker正式结果混合。输出KL或激活幅度匹配对照尚未实现，只在核心对照留下明确歧义时考虑；现有匹配仅是逐模块算子到单位阵的Frobenius距离。无需把这些扩展变成完成首轮结论的前置条件。
