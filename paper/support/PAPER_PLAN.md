# SPECTRUM — one manuscript plan

Title: **SPECTRUM: Diverse Correct Code through Soft Spectral Self-Distillation**.
Code identifier remains `spectral_soft`; the manuscript name changes no algorithm.

## Contribution sentence

SPECTRUM replaces rank truncation of correctness-gradient K/V directions with a full-spectrum proximal filter; a one-round coding pilot finds increased correctness-matched implementation coverage after ordinary self-distillation, with a small accuracy change.

## Causal spine

Nearly identical single-sample correctness coexists with different implementation coverage → correctness alone does not specify which correct implementations survive → hard capability selection introduces a representation bottleneck → continuous spectral weights provide a bounded alternative → raw-data distillation transfers the changed generation distribution → correctness-conditioned coverage measures the outcome → matched controls and longitudinal evaluation test the mechanism.

## Claims and evidence

| Claim | Evidence | Manuscript treatment |
|---|---|---|
| Accuracy and conditional implementation coverage are different objectives | Exact distributional construction; pilot descriptive ranking | Introduction, Section 2, Figure 1 |
| Finite-tau operator retains every linear direction | Closed-form eigenvalues and norm bounds | Method proposition and Figure 3, explicitly local |
| Map is stable to perturbations of normalized covariance | Resolvent identity | Method derivation |
| After one LoRA round, conditional AST diversity improves against SSD in pilot | Uploaded seed-42 paired summary | Results table with exact intervals |
| Post-LoRA multi-seed advantage over hard projection | Not yet available | Prospective experiment slots, no numerical claims |
| Gains arise from learned spectrum rather than generic attenuation | Matched controls implemented; no results | Prospective mechanism table |
| Algorithm-family diversity / long-horizon retention / transfer | No results | Pending experiment plan and bounded hypotheses |

## Layout

One `main.tex`; official unmodified ICLR2027 style; 9 pages through Conclusion; references and AI-use disclosure afterward. No alternate titles, abstracts, section files, or duplicate manuscript versions.

Opening uses the measured observation rather than claiming an unprecedented phenomenon. Method begins by pages 2–3. Tables preserve all comparator scores. Missing measurements are visibly `Pending` in their prospective section. The three included vector figures are measured or explicitly analytic; future figure prompts never manufacture data.

## Writing rules adopted

ARIS `paper-write` / `writing-principles`, pinned at f1bd907b58f653131ebe6807c482e2554e07f9b9: one narrative, evidence-matched direct claims, no generic openings or stacked hedges, specific boundaries collected in Limitations, no fictional completed experiments. User requirement of a single `main.tex` overrides modular-file guidance.
