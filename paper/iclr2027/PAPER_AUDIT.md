# SPECTRUM manuscript rewrite — 2026-09-24

State: **Complete with named evidence limits**. Operation: full-paper rewrite in AI-conference mode. Target: ICLR 2027 anonymous main-track submission; English manuscript. Only existing experimental records are used. No training, generation, or program-verification run was started for this revision.

## 核心主张与整篇文章的逻辑

论文现在讲的是：**模型反复学习自己的输出时，正确率提高仍可能伴随正确实现广度收缩；在固定参考锚点的条件下，SPECTRUM 改变每轮生成几何，使后续原生学生保留更多广度。**

Looped Self-Distillation 是本文明确研究的外循环设置；SPECTRUM 是其中的方法。引言第二段明确限定为 **fixed information budget**：每轮新生成的样本不接受用于训练的外部评分、奖励、排名或正确性筛选，也不增加新标注。固定的是最初给定的参考题与参考答案，随轮次更新的是当前模型以及从它计算出的几何。固定参考锚点属于初始外部监督，因此表述为“无生成后外部反馈进入训练”，而非“完全没有外部监督”。所有原始生成样本进入同一个学生。

### 正文顺序

1. **Introduction**：先讲“今天的学生会成为明天的教师”，从实验现象提出问题。Figure 1 展示准确率上升、正确 AST 广度下降，以及固定正确样本数后的收缩与正确输出的集中化。承认迭代自蒸馏和多样性损失已有研究，将缺口落在无样本筛选的外循环、生成结构干预与原生学生保留效果的结合上。
2. **What should a self-distillation loop retain?**：用 `P(correct,class)=P(correct)P(class|correct)` 区分成功概率和成功内部的分布。解释 pass@k、总预算 richness Ck、正确数匹配 richness Db 分别回答什么；不把基础概率恒等式包装成新的数学定理体系。
3. **Looped Self-Distillation with a fixed reference anchor**：定义“构造生成策略 → 生成完整数据集 → 单学生学习 → 重新生成”的学习循环，解释为何单轮不能回答后续保留问题。说明固定参考信息和不断变化的几何，并与推理内部的 looped transformer 区分。Figure 2 是这部分与方法部分共同的主图。
4. **SPECTRUM**：从 reference-completion loss 的 K/V 输出梯度二阶矩，推到近端目标、闭式谱增益、局部可逆性与稳定性，再回到临时权重折叠、全部原始样本、单 LoRA 和标准推理。新增方向导数解释、每轮重新估计几何的原因、三个特征值对应增益的计算例子，以及完整的学生交叉熵目标。最后解释 K/V 各自如何改变生成计算，和临时谱调制如何通过合成语料进入下一轮学生。局部性质解释设计，不替代输出分布实验。
5. **Experiments**：按 RQ1 保留结果、RQ2 成功数与采样预算解释、RQ3 生成设计取舍、RQ4 迁移范围排序。正文三个表只放已完成结果。Figure 3 把总预算与正确数匹配放在同一证据链里。
6. **Related work**：四个主题依次是迭代自训练与自蒸馏、反馈从哪里来、递归学习中的多样性、谱控制与学生保留。逐项比较 SCoder、2023 的迭代自蒸馏、SSD、SD-Zero、CRISP、sampled-demonstration diversity、UA-RL、递归数据坍缩与谱干预。不以是否会议录用来否认先前工作。
7. **Limitations**：独立说明证据范围和机制边界：单训练 seed/模型、AST 结构代理、固定参考监督预算、未隔离的方向与强度因素、token 数差异、局部算子结论和整体行为的区别，以及已报告的准确率与 APPS 代价。
8. **Conclusion and future work**：总结循环中“准确率与正确实现广度分离”的发现、SPECTRUM 的干预位置和 89.9% 保留结果；再给出生成到学生的传递分析、matched-token/固定几何/方向对照、跨模型与可验证推理任务的后续方向。未来方向不充当已经完成的证据。

最新排版：正文恰好 9 页（包含 Limitations 和 Conclusion and future work）；第 10 页起为声明与参考文献，第 13 页起为附录，完整 PDF 共 20 页。未改变官方模板的字号、页边距或行距。

引言引用进一步扩展为 15 篇相关研究，分布在 10 个引用组中，分别支撑自我改进背景、候选代码搜索、可执行评测、递归数据问题、迭代自蒸馏前作、原始样本学习以及方法组件归属。Figure 1 的 16 样本逐轮轨迹与 Table 1 的最终 64 样本结果在文字中分开交代。

### 实验如何读

- **Table 1 / RQ1**：五轮最终 MBPP n=64；SPECTRUM 的 C64 为 11.510，Plain 为 8.506；保留率 89.9% 对 66.4%。pass@64 提升 2.2 pp，pass@1 降低 1.12 pp。
- **Figure 1 / RQ1**：完整历史每轮仅有 n=16；不能把最终 n=64 数值拼成每轮 n=64 曲线。图中另外两部分依次说明“不是只少了正确样本”和“正确分布也更集中”。
- **Figure 3 / RQ2**：同一 n=64 池上的预算曲线，以及共同 eligible tasks 上的 Db 配对差异。D4 优势 +0.295 [0.249,0.343]，316 个共同可用题目。
- **Table 2 / RQ3**：SSD 已完成五轮并加入比较；它的多样性比 SPECTRUM 高，但 pass@1 更低。投影控制共享参考锚点，作为设计对照并给 SPD 文献归属。
- **Table 3 / RQ4**：HumanEval+、APPS Intro 的冻结学生结果均纳入。两者正确数匹配的配对增益为正；APPS 的总体成功和 C16 没有改善。两层结果并列说明条件多样性和任务覆盖的区别。
- **Figure 4 / Appendix**：用保存的真实 AST 频数展示“正确数量一样，内部实现分布不同”。正反两个例子都按同一最低 task-ID 规则选择；不伪造已从紧凑存档移除的代码文本。
- **Appendix tables**：全部轮次、配对置信区间、投影比较、完整设定与真实 token 成本。未完成的大模型、多 seed 和机制矩阵从结果表删除；并未假定其结果。

## Claim–evidence matrix

| ID | Claim | Evidence present | Scope and disposition | Location |
|---|---|---|---|---|
| C1 | Correctness cannot identify the distribution inside correct outputs | Probability factorization and occupancy calculation | Elementary statement under independent draws; not a priority claim | §2, App. A |
| C2 | Correctness can rise while correct AST breadth declines over repeated SD | Full MBPP n16 trajectories, independent n64 final pool | One backbone and training seed; show both quantities | Fig. 1, Table 1 |
| C3 | SPECTRUM retains more richness than Plain | C64 11.510 vs 8.506; paired +3.004 [2.568,3.494] | Does not preserve all initial richness; accuracy cost retained | RQ1 |
| C4 | The richness difference survives correct-count matching | D4/D8/D16 paired effects on 316/296/254 tasks | Conditional subsets, not full-task improvements | RQ2, Fig. 3 |
| C5 | Generation changes remain in native students after SFT | Native post-SFT endpoints, intervention absent | No generator-on/student-off transfer fraction; no paired generator diagnostic in this archive | Method, RQ1 |
| C6 | The operator preserves local distinguishability and depends continuously on normalized geometry | Positive Hessian and resolvent identity proofs | Classical proximal operator; no full-network semantic guarantee | Proposition 2, App. B |
| C7 | The choice of spectrum matters under matched anchor access | Projection control vs proximal gain | Spectrum and strength both differ; orientation causality not isolated | RQ3 |
| C8 | SPECTRUM dominates SSD | Contradicted by SSD's higher richness | Removed. Report different correctness/diversity operating points | Table 2 |
| C9 | Conditional richness transfers beyond MBPP | Derived paired D4 effects on HumanEval+ and APPS | 111/42 tasks; APPS overall performance decreases | RQ4, App. D |
| C10 | Repeated SD, no correctness filtering, or SD diversity loss is first discovered here | Existing papers contradict broad priority | Removed; literature credited explicitly | Intro, Related work, App. G |
| C11 | Every round receives no external information | Same external references are reused for recalibration | Replaced with fixed-reference guidance, no newly acquired labels or rollout judgments | Abstract, §3, Fig. 2 |
| C12 | Larger models, many seeds, random/isotropic/tau controls validate the method | No completed archive for these claims | Omitted from results; listed as scope boundaries | Limitations, future work, App. G |

## Evidence and derivations

Base snapshot: `ed35e52e5be4a979c87f95e803f90496750c194b`.

- Main archive: `results/retention_5round_train16_eval16_seed43/`.
- Final larger-budget supplement: its `eval64/` directory.
- SSD continuation: `results/sep20_continuation/sep20_ssd_5round_seed43_eval16_3090/`.
- Transfer: `sep20_transfer_humanevalplus_seed43_n16_b64/` and `sep20_transfer_apps_intro_seed43_n16_b8/` under the same continuation directory. Here `n16` is sample count, while `b64` / `b8` denotes batch settings, not 64/8 samples.
- `source-data/rewrite_sources.json` retains exact selected fields and SHA-256 hashes of source files. `analyze_existing.py --refresh-sources` extracts them from a repository checkout; default execution uses the bundled snapshot.
- New derived analyses: paired transfer bootstrap (2,000 task resamples, seed 20260924), sums of existing training budgets, and deterministic equal-correct-count examples. Exact rarefaction values are checked against saved per-task metrics. No programs are executed.
- Retention is a ratio of mean class counts, not set intersection with initial classes. The paired Db contrast is not subtraction of two marginal means.

## Visual and table manifest

| Item | Duty | Source | Production | Placement |
|---|---|---|---|---|
| Fig. 1 | Reveal correctness/breadth divergence and within-correct contraction | MBPP n16 aggregate and paired reports | Experiment-figure design; deterministic matplotlib | Intro |
| Fig. 2 | Explain fixed anchor, evolving geometry, full raw-data loop | Calibration, spectral folding, training implementation | Pipeline-figure design; vector shapes and equations | Framework/method |
| Fig. 3 | Show budget dependence and correct-count-matched gain | Final n64 aggregate + paired files | Experiment-figure design; deterministic matplotlib | RQ2 |
| Fig. 4 | Illustrate equal success with unequal class occupancy in both directions | Saved HumanEval+ per-task counts | Experiment-figure design; deterministic matplotlib | Appendix E |
| Tables 1–3 | Exact headline, SSD/control, and transfer values | Same committed evidence | Native monochrome booktabs LaTeX | Main |
| Tables 4–9 | Protocol, all rounds, paired effects, controls, resources | Configs and existing summaries | Native monochrome booktabs LaTeX | Appendix |

Every numbered non-table figure has three standalone alternatives under `figure-prompts/`. Each English prompt is under 5,000 characters. Quantitative prompts specify plotting/vector production rather than asking an image model to invent a chart.

## Change map

| Previous manuscript component | Action | Replacement and reason |
|---|---|---|
| Generic self-improvement opening | Rewrite | Begin with the student becoming the next teacher and the measured correctness/richness separation |
| Ambiguous supervision wording | Rewrite throughout | Explicit fixed reference anchor, recalculated geometry every round, no rollout judging |
| Implicit broad priority for looping | Rewrite | Operational framework with explicit iterative-SD precedents |
| Missing recent near-neighbor literature | Add | SCoder, Rao et al., CRISP, sampled-demonstration diversity analysis |
| Pending SSD row | Replace | Completed separate n16 continuation, including its stronger diversity/lower accuracy |
| Placeholder extension matrices | Cut from result tables | No new runs requested; evidence scope stated externally and in limitations |
| Transfer marked pending | Replace | Completed HumanEval+ and APPS results, plus reanalysis of saved task records |
| Colored/mixed table styles | Unify | Native booktabs, no colored table cells; monochrome figures |
| Old fourth trajectory figure | Replace | Actual equal-correct-count examples in appendix; retain trajectory in Figure 1 |
| Operator/probability appendix | Revise | Tight definitions, proofs, normalization conditions, full loss masks and information flow |

## Venue compliance

Checked 2026-09-24 against the official ICLR 2027 Author Guidelines:
<https://iclr.cc/Conferences/2027/AuthorGuidelines>

The official 2027 template is preserved without margin/font modifications. Submission main text must be at most nine pages; bibliography and appendices are excluded, and appendices follow references. AI-use and reproducibility statements follow the official placement. The manuscript is anonymous. The existing template provenance is recorded in `../support/TEMPLATE_PROVENANCE.md`; the official archive is <https://media.iclr.cc/Conferences/ICLR2027/iclr-2027-style-files.zip>.

Render and citation checks are recorded in `BUILD_REPORT.md`. This is a completed manuscript based on available evidence, not a claim that single-seed results or all submission requirements have been independently certified.

## Remaining evidence boundaries (no further runs scheduled)

1. Main mechanism/performance evidence is one trained seed and one backbone; task bootstrap does not remove this limitation.
2. No anchor-only SFT, orientation-matched, strength sweep, or fixed-geometry result isolates each component. Conclusions are scoped accordingly.
3. No semantic algorithm annotations; AST breadth is the operational diversity endpoint.
4. Native-student benefits are measured; generator-to-student transmission fraction and train-length causal mediation are not.
5. APPS transfer does not improve all-task accuracy/coverage. This remains visible in the main result table.
