# Paragraph-level narrative blueprint

This reverse blueprint maps the completed main text to its evidence-bearing first sentences. The section-level purposes, figure/table placements, interpretation boundaries, and transitions are specified in `PAPER_AUDIT.md`. Read the sequence as problem → identifiable endpoints → loop and information budget → operator → native-student evidence → scope.

| Paragraph | Section / role | Topic-sentence anchor | Evidence / citation anchors |
|---|---|---|---|
| P01 | Abstract | \begin{abstract} A model that learns from its own outputs inherits more than their correctness: it inherits which solutions it produces. | local definitions / archived measurements |
| P02 | Introduction | This distinction matters beyond code. | local definitions / archived measurements |
| P03 | Introduction | Our experiments expose this separation during repeated learning (Figure~\ref{fig:motivation}). | local definitions / archived measurements |
| P04 | Introduction | Iterative self-distillation itself has precedents. | rao2023iterative,zhang2025scoder,he2026sdzero,sang2026crisp,nicolicioiu2026diversity |
| P05 | Introduction | We formulate this study as \emph{Looped Self-Distillation}: an outer learning process that repeatedly constructs a generation policy, samples a corpus, and updates one native student. | local definitions / archived measurements |
| P06 | Introduction | The resulting student retains substantially more correct implementation breadth. | local definitions / archived measurements |
| P07 | What should a self-distillation loop retain? | \begin{proposition}[Correctness does not identify correct-solution breadth] \label{prop:breadth} For fixed $a>0$, pass@$k=1-(1-a)^k$ is independent of $q$. | local definitions / archived measurements |
| P08 | What should a self-distillation loop retain? | We use descriptive names: \emph{correct AST richness@$k$} for $C_k$ and \emph{correct-count-matched AST richness@$b$} for $D_b$. | hurlbert1971nonconcept |
| P09 | What should a self-distillation loop retain? | For a sequence of students $\theta_0,\ldots,\theta_T$, the \emph{retention profile} records $(\mathrm{pass@}k,C_k,D_b)$ under a common evaluation protocol. | local definitions / archived measurements |
| P10 | Looped Self-Distillation with a fixed reference anchor | \paragraph{Why loop?} A one-round evaluation measures a teacher--student transition. | dehghani2019universal |
| P11 | Looped Self-Distillation with a fixed reference anchor | \paragraph{Where supervision enters.} \method\ repeatedly uses the \emph{same} reference anchor to recalibrate the evolving model. | local definitions / archived measurements |
| P12 | SPECTRUM: proximal spectral modulation | High sensitivity indicates that the reference loss responds strongly to a direction. | local definitions / archived measurements |
| P13 | SPECTRUM: proximal spectral modulation | \begin{proposition}[Local distinguishability and calibration stability] \label{prop:prox} For $\Cbar\succeq0$ with eigenvalues in $[0,1]$ and finite $\tau\ge0$, Equation~\eqref{eq:prox} has a unique solution. | local definitions / archived measurements |
| P14 | Experiments | All native students use common evaluation decoding: temperature $0.8$, top-$p$ $0.95$, and no top-$k$ truncation. | local definitions / archived measurements |
| P15 | Experiments | We ask four questions: \textbf{RQ1}, does spectral generation improve breadth retained by a native student? | local definitions / archived measurements |
| P16 | Experiments | The accuracy profile explains what this retention buys. | local definitions / archived measurements |
| P17 | Experiments | The 16-sample trajectory connects this endpoint to repeated learning. | local definitions / archived measurements |
| P18 | Experiments | The budget curves reveal complementary behavior. | local definitions / archived measurements |
| P19 | Experiments | For a decoding-based comparator, we loop SSD's temperature/truncation recipe \citep{zhang2026ssd}: training generation uses temperature $1.5$, top-$p$ $0.8$, and top-$k$ 20; evaluation returns to the common decoder. | zhang2026ssd |
| P20 | Experiments | On HumanEval+, \method\ matches Plain's pass@16 and has a paired $D_4$ advantage of $0.080$ classes $[0.021,0.142]$ on 111 tasks. | local definitions / archived measurements |
| P21 | Related work | \paragraph{Diversity and recursive data.} \citet{nicolicioiu2026diversity} analyze diversity loss from demonstration-conditioned self-distillation and trace it to biased teacher feedback. | nicolicioiu2026diversity,hu2026uarlacl,shumailov2024collapse,gerstgrasser2024accumulating |
| P22 | Related work | \paragraph{Spectral generation control.} Spectral activation editing provides a means to alter model behavior \citep{qiu2024sea}; capability-selective self-policy distillation applies reference-gradient subspaces to generation \citep{hao2026spd}. | qiu2024sea,hao2026spd,parikh2014proximal |
| P23 | Discussion and conclusion | The evidence is strongest for one 1.5B model and one training seed, with two frozen-student transfer sets. | local definitions / archived measurements |
