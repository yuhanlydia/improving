# SPECTRUM

**Diverse Correct Code through Soft Spectral Self-Distillation**

ICLR 格式首稿：当前 PDF 为 **9页正文＋2页 AI 声明与参考文献**。论文中的 SPECTRUM 对应 improving 仓库的 `spectral_soft`。

## 研究思路与真实方法

**现象。** 单次答对率接近的代码模型，可能反复输出同一种正确实现，也可能覆盖更多正确结构。Pilot 中，四种自蒸馏策略的 pass@1 接近，但正确实现覆盖率的排序不同。

**思考。** 正确参考程序只展示一种解法。参考损失下能量较弱的方向，未必没有用；硬截断可能同时移除较少出现的正确实现所需的自由度。

**方法。** 在正确参考完成文本上计算 completion-masked 交叉熵，收集原生 K/V 线性层输出的激活梯度。损失只监督完成部分，二阶矩却累积所有非padding位置的梯度，包括能影响后续目标的提示位置：

\[
C=\frac1M\sum_{i,u} g_{iu}g_{iu}^\top,\qquad
T=\left[I+\tau\left(I-\frac{C}{\lambda_{\max}(C)}\right)\right]^{-1}.
\]

谱来自梯度二阶矩，不是预训练权重的分解。T 保留最大特征值方向，并对完整谱连续衰减；有限 τ 下每个方向仍有正增益。它最接近 SPD 的 K/V 子空间干预，区别在连续完整谱选择，以及以正确实现覆盖为目标的评估。

每轮临时将 T 折入生成权重与偏置，生成后恢复原权重；随后用**全部原始输出**做普通 LoRA，包含错误和空回答。合并后以原生模型评估，下一轮重新校准。每轮只有一个学生和一个合并模型，不构造 adapter 池。

## 证据与待完成项

主要指标 D₄ 是抽取四个正确样本时的期望 AST 类覆盖率；方法比较使用共同合格题集，并以准确率下降不超过1个百分点为正式确认约束。AST 类是结构代理，算法差异需盲法标注。

已完成证据仅为 seed 42、1.5B、64题、单轮 pilot。相对 SSD-style，配对 D₄ 增加0.0312，任务bootstrap 95%区间为[0.0095, 0.0550]；pass@1变化−0.244个百分点。多种子、机制对照、三轮保留和迁移实验仍为 **Pending**，局部线性界不证明多轮防坍缩。执行顺序、判定条件和证据需求见 `PENDING_EXPERIMENTS.md`。

## 文件导航

| 文件 | 用途 |
|---|---|
| `main.tex` / `main.pdf` | 唯一稿件 TeX 源码与编译预览 |
| `references.bib` | 参考文献 |
| `iclr2027_conference.sty` / `.bst` | 未修改的官方 ICLR 2027 样式 |
| `figures/fig1_observation.pdf` | Pilot 现象矢量图 |
| `figures/fig2_method.pdf` | 方法流程矢量图 |
| `figures/fig3_gain.pdf` | 解析增益曲线矢量图 |
| `figure_prompts/` | 六份绘图文档，每份三套方案；涵盖现象、方法、增益、正式比较、机制、跨轮保留 |
| `PENDING_EXPERIMENTS.md` | 未跑实验的有限执行计划 |
| `source-notes.md` | 文献定位与来源说明 |
| `support/` / `licenses/` | 绘图脚本、证据摘要、写作及模板来源与许可 |

## 编译与编辑

在包根目录运行：

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

或依次运行：

```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Overleaf 中选择“New Project → Upload Project”，上传 ZIP，将 `main.tex` 设为主文件，使用 pdfLaTeX 编译。

写作应用了 [ARIS paper-write](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/blob/f1bd907b58f653131ebe6807c482e2554e07f9b9/skills/skills-codex/paper-write/SKILL.md) 的贡献前置、证据匹配和集中陈述限制等规则。按用户要求，正文、符号、表格与证明集中在一个 `main.tex`，优先于技能的分节文件惯例。AI 声明须由作者按真实参与情况核对。编译和绘图不等于运行科研实验；未来结果图需获得真实数据后填写。
