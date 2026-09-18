# Figure 2 — Pipeline Figure Design

Figure number: **2** · Role: method overview · Section: Method (after the opening paragraph that names inputs, outputs, and novelty) · Intended width: full text width (7.0 in), height ≈ 2.4–2.7 in.

## A. Fact Lock

| Item | Content | Status |
|---|---|---|
| Setting | One model $\theta_t$ per round; one merged student $\theta_{t+1}$; no adapter pool, no teacher | `CONFIRMED` (`paper/README.md`, `src/improving/`) |
| Calibration loss | Completion-masked reference cross-entropy, per example, normalized by its own masked-token count | `CONFIRMED` |
| Gradient site | Native K/V linear-layer **output** activations, before RoPE and before key normalization | `CONFIRMED` |
| Gradient positions | **Every nonpadding position**, including prompt positions; masking the loss and selecting positions are different operations | `CONFIRMED` |
| Second moment | $C_\ell=\frac{1}{M_\ell}\sum_{i,u\ \text{nonpad}} g^{(\ell)}_{iu} g^{(\ell)\top}_{iu}$, per selected module $\ell$; $M_\ell$ counts all included positions including zero-gradient ones | `CONFIRMED` |
| Normalization | $\bar C_\ell = C_\ell/\lambda_{\max}(C_\ell)$; requires $\lambda_{\max}>0$ | `CONFIRMED` |
| Modules | Both K and V at decoder layers $\lfloor L/2\rfloor$ and $L-1$ | `CONFIRMED` |
| Operator | $T_{\ell,\tau}=[\mathbf{I}+\tau(\mathbf{I}-\bar C_\ell)]^{-1}$, eigenvalues $1/[1+\tau(1-\mu_j)]$ | `CONFIRMED` |
| Default strength | $\tau=1$; gains lie in $[1/2,1]$; **no direction is zeroed at finite $\tau$** | `CONFIRMED` |
| Folding | $W'=T^\top W$, $b'=T^\top b$, computed in float32, applied temporarily, then the **exact saved native values are restored** | `CONFIRMED` |
| Generation | One raw completion per training prompt under the folded policy | `CONFIRMED` |
| Training | Ordinary LoRA initialized from the **saved native $\theta_t$**, not from the transformed generator; loss covers **all** nonpadding targets; wrong and empty completions enter the corpus | `CONFIRMED` |
| Evaluation | Merged native $\theta_{t+1}$, no transform at inference | `CONFIRMED` |
| Recurrence | Next round recalibrates $C$ from the merged native checkpoint | `CONFIRMED` |
| Contrast with SPD | SPD keeps the pipeline but replaces the continuous gain with a hard top-$r$ projector ($r$ = half the directions in this reconstruction) | `CONFIRMED` (`docs/`, `paper/main.tex`) |
| Numeric results | none in this figure | — |

Everything above is `CONFIRMED` from the repository. No `TO CONFIRM` item remains that changes the topology.

## B. Three-second claim

*"We do not add a training loss. We change the distribution the data is drawn from, using a full-rank continuous filter built from correctness gradients, and then train normally."*

**Visual center:** the *fold-and-restore* gate — the point where the operator enters the generator and is guaranteed to leave it. This is the paper's novelty boundary: the intervention is temporary and the student never sees the transform.

## C. Design route and production route

- **Design route:** `designing-pipeline-figures`. Topology is `dual-lane-feedback-loop` with a `lifecycle` split: an upper generation/calibration lane and a lower training lane, joined by the corpus, with an outer recurrence returning to the exact native checkpoint.
- **Production route:** editable vector diagram. In this repository: matplotlib with explicit coordinates (`paper/support/make_figures.py` pattern), exported to vector PDF. Not `imagegen` — every label and equation is exact.

## D. Three candidates

### Candidate A — Dual-lane with an explicit restore gate (recommended)

**Macro-topology.** Two lanes. Upper lane, left→right: `native θ_t` → `reference calibration` → `soft spectral transform` → `fold into generation weights` → `generate one raw completion per prompt`. A vertical drop labelled **"raw completions (all of them)"** carries the corpus into the lower lane. Lower lane, right→left is avoided; instead it reads left→right again: `restore native θ_t` → `ordinary LoRA (all nonpadding targets)` → `merge` → `native θ_{t+1}`. The **restore gate** is drawn as an explicit small diamond/valve on the arrow from the upper lane's fold step down to the lower lane's LoRA start, labelled "saved native state, not the transformed generator". A thin outer recurrence arrow leaves `native θ_{t+1}` and returns to the *calibration* box (not to the whole system), labelled "recompute $\bar C$ from the merged native checkpoint".

**Emphasis:** the gate. **Compresses:** the LoRA hyperparameters. **Risk:** the two lanes can read as two separate methods; the vertical corpus arrow must be visually the heaviest connector.

**Third-second check:** the reader should see one temporary detour and one permanent path.

### Candidate B — Single-line timeline with an inset operator

**Macro-topology.** One horizontal left→right path: `θ_t → calibrate C → apply T → generate → restore → LoRA → θ_{t+1}`, with the restore step drawn as an explicit inverse-arrow that snaps back to `θ_t` before the LoRA box. A rounded inset above the path expands the operator: eigenvalue axis μ, the gain curve $1/[1+\tau(1-\mu)]$ with the τ=1 curve drawn, and the note "floor 1/2 at μ=0".

**Emphasis:** the operator's shape and the linearity of the process. **Compresses:** the fact that evaluation uses the native model. **Risk:** a linear layout understates the round-to-round recurrence; the inset competes with Figure 4's analytic gain panel.

### Candidate C — Contrast layout: SPD-hard above, SPECTRUM below, shared stages collapsed

**Macro-topology.** A two-row contrast. Both rows share drawn-through stages `calibrate → intervene → generate → LoRA`; the **intervene** stage is the only one that differs, expanded for each row: SPD-hard shows `top-r projector, gains ∈ {0,1}`, SPECTRUM shows `full-spectrum proximal map, gains ∈ [1/(1+τ), 1]`. A vertical brace spans the shared stages labelled "identical".

**Emphasis:** the scientific comparison is one component, not a whole pipeline. **Compresses:** the recurrence. **Risk:** it is really a mechanism figure; it duplicates Figure 3's comparison and reads as a rebuttal to a specific prior paper.

**Recommendation: Candidate A.** It states the method's actual novelty boundary (temporary intervention, native student) in one reading path and does not duplicate the comparison figure. Candidate C is the better figure if the paper later narrows to a pure mechanism claim.

## E. Standalone vector-diagram specification (Candidate A)

> **Figure 2, ICLR camera-ready style.** Canvas 7.0 in × 2.5 in, white background, 8 pt sans-serif, all text horizontal. Reading path: upper lane left→right, then down, then lower lane left→right.
>
> **Upper lane (y ≈ 0.72 of height), six boxes** left→right with 2 px arrows: (1) `Native θ_t`; (2) `Reference calibration` with the two-line formula $C_\ell=\frac{1}{M_\ell}\sum_{i,u}g^{(\ell)}_{iu}g^{(\ell)\top}_{iu}$ and $\bar C_\ell=C_\ell/\lambda_{\max}$; (3) **`Soft spectral transform`** — this box carries the teal/blue accent fill `#2a78d6` at 10% opacity with a 1.5 px `#2a78d6` border, and contains $T_{\ell,\tau}=[\mathbf{I}+\tau(\mathbf{I}-\bar C_\ell)]^{-1}$, $\tau=1$; (4) `Fold temporarily` with $W'=T^\top W,\ b'=T^\top b$; (5) `Generate 1 raw completion / prompt`. Below box (3), muted 7 pt text: "gain $1/[1+\tau(1-\mu_j)]$ · no direction zeroed".
>
> **Vertical connector.** From box (5) down to the lower lane, a heavy `#2a78d6` arrow labelled `raw completions — kept, including wrong and empty ones`. This is the visually dominant connector (2 px, the only colored connector).
>
> **Restore gate.** At the lower lane's entry, a small hexagon labelled `restore native θ_t` in neutral `#52514e`, connected to box (1) by a thin dotted vertical line labelled `saved state`. Caption-side note: "LoRA starts from the saved native weights, not from the folded generator."
>
> **Lower lane (y ≈ 0.22), four boxes** left→right: `Ordinary LoRA` (sub-label `all nonpadding targets`), `merge`, `native θ_{t+1}`, and a detached box `native evaluation` reached by a **dashed** arrow labelled `no transform at inference`. Dashed style = evaluation branch only.
>
> **Recurrence.** A thin `#52514e` arrow leaves `native θ_{t+1}` and travels along the bottom back to **box (2) `Reference calibration`** — annotate `next round: recompute C from the merged native checkpoint`. Do not point it at the whole upper lane.
>
> **Legend.** None; a small key at bottom-right names the two connector styles: solid = generation and training path, dashed = evaluation, dotted = saved-state restore.
>
> **Negative constraints.** Do not draw RoPE, attention internals, or per-layer stacks — the intervention point is "K/V linear output", stated in text. Do not add a loss box in the upper lane. Do not draw the hard-projection baseline here. Do not put numbers in the diagram. Do not use more than one accent color. Do not let any arrow point at a whole lane.

## F. Caption draft

> **Figure 2: SPECTRUM changes the data distribution, not the training objective.** Reference-completion loss supplies gradients of the native K/V linear outputs at every nonpadding position; their normalized second moment defines a full-rank continuous gain profile $T_{\ell,\tau}$ that is folded into the generation weights **temporarily**. Every raw completion — including wrong and empty ones — enters the corpus. LoRA then starts from the saved native $\theta_t$ and trains on all nonpadding targets, so the student never inherits the transform. The merged native $\theta_{t+1}$ is evaluated without any transform and is the checkpoint the next round recalibrates from. Solid arrows are the generation and training path; the dashed arrow is the evaluation branch; the dotted path is saved-state restoration.

## G. QA

- [ ] Every equation in the figure matches `paper/main.tex` notation exactly.
- [ ] The restore gate is visible without reading the caption.
- [ ] The recurrence arrow lands on the calibration box, not the lane.
- [ ] Text legible at 7.0 in; no label under 7 pt.
- [ ] One accent color only; the accent marks exactly the novelty box.
- [ ] No invented modules, losses, or numbers.

## H. Unresolved

1. Whether to show $\bar C$ normalization inside box (2) or move it to the equation in the text — the figure is dense at 7.0 in if both formulas stay.
