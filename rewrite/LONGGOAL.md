# LONGGOAL — SPECTRUM ICLR 2027 submission

**Set:** 2026-09-18 · **Paper deadline:** 2026-09-25 AoE
**Rule:** drive every goal to a verified end state. No goal is "done" because it was attempted;
it is done when the stated check passes. Report failures as failures.

| # | Goal | Done when (check) | Status |
|---|---|---|---|
| G1 | Main text fits the ICLR 2027 limit | Main text ends at or before 9.0 pages of body; measured from the compiled PDF with the official ruler, not estimated | **DONE** — 8.911 pages counted / 8.994 strict, 4.8 ruler lines headroom, `measure_pages.py` exit 0 |
| G2 | Every number in `main.tex` traces to a stored result file | An independent checker re-derives each numeric claim from `results/` and reports zero unexplained values | **DONE, with two named gaps** — 3 audit passes; all findings fixed; see below |
| G3 | Every figure is correct and legible at final print size | All 5 figures inspected at rendered size; no label collision, no clipped element, no fabricated value | **DONE** — visually inspected + `check_figures.py`: 0 clipped, 0 colliding, all 5 |
| G4 | Template and anonymity compliance | style/bst byte-identical to official release; no author-identifying string; AI-use statement present | **DONE** — byte-identical to the official archive (md5 + git blob SHA-1); anonymity sweep clean; AI statement present |
| G5 | Deliverables written | BRIEF, claim–evidence matrix, compliance note, change map exist and agree with the manuscript | **DONE** — `BRIEF.md`, `CLAIM_EVIDENCE.md`, `COMPLIANCE.md`, `CHANGE_MAP.md` |
| G6 | Honest-reporting red line held | The failed pass@1 noninferiority result appears in the main text plainly, once in results and once in limitations, never as "trade-off" or "noninferior" | **DONE** — §5.4, §6, and the abstract; both forbidden words absent |

## Verification log

| Pass | Scope | Outcome |
|---|---|---|
| 1 | Full numeric sweep of `main.tex` vs `results/` | Findings fixed |
| 2 | Re-verify pass-1 corrections + full sweep + `make_figures.py` constants | 12/12 prior corrections confirmed correct; 6 new numeric findings + 4 tier/precision flags, all fixed |
| 3 | Re-verify the newly-applied corrections + full independent sweep | All four consistency notes resolved; **no new numeric defect found**. Pass 3 also corrected the *length instrument* (below), not the paper. G2 re-closed. |
| 4 | Figure-geometry pass: rendered-size review + `check_figures.py` over all five PDFs | 4 figure defects found and fixed (see `CHANGE_MAP.md` §2, items 7–10); all five now clean |

**Pass 3 outcome — the four notes it carried in, and their resolutions:**

1. The `+0.042` / `-0.131` control-flow values were unlabelled by tier. Verified from `report.json`:
   `eval64/comparisons_compact.json` has **no control-flow block**, so those values can only be
   per-round-tier. Now labelled as such in §5.5.
2. Fig 4 put $D_4$ and $C_{64}$ on one shared x-axis. Their effects span 0.64 and 5.38 AST classes,
   so the $D_4$ intervals — about 0.09 wide — would have rendered as single dots on a shared axis.
   Rebuilt as a 1×3 row, one axis per endpoint.
3. The $D_4$ eligible-$n$ range $236$–$246$ was described as if it belonged to one comparison. It is
   the **union across three arms**; \method-vs-base alone is $236$–$245$. Corrected in the caption
   and in the in-figure footnote.
4. §5.4's phrasing "required the interval's lower bound to reach $-1$ pp" was loose. The criterion is
   that the lower bound be *no lower than* $-1$ pp; it comes in at $-1.89$. Reworded.

**Pass 3 also found the ruler wrong, not the paper.** The instrument was measuring at the
`REFERENCES` heading — one line *past* the last main-text line — and counting the footer page
number as body text. Both are fixed; see `COMPLIANCE.md` §1. The corrected reading is 8.911 pages
counted (8.994 strict), so the paper was never over the limit; the old 9.004 "naive" figure was an
artifact. Removing 143 characters of prose proved this independently: the heading did not move,
because page 9 is float-packed and LaTeX reflows a float into the freed space.

## Named gaps (stated, not hidden)

1. **The paired bootstrap was not re-run.** The shipped bundle contains hashes only, no per-task
   jsonl, so the intervals cannot be recomputed from it. They are reported as stored. This is stated
   in `CLAIM_EVIDENCE.md` §5 and must not be implied otherwise. **This is a real gap in G2**: every
   *transcribed* number is verified against the stored files, but the *statistics that produced*
   those files could not be independently recomputed.
2. **Pass 3's control-flow block rests on the per-round tier only.** The 64-sample tier carries no
   control-flow measurement, so the coarse-fingerprint claim cannot be checked at the budget the
   rest of the paper's headline results use. Labelled in §5.5 rather than dropped.
3. **Mechanism controls unrun.** Matched-blend / random-eigenvector / isotropic controls are
   implemented but not executed. Declared in §3.3 and Appendix F.
4. **Algorithm-level diversity is not claimed** anywhere, because `strategy_annotation_status` is
   empty in every record. All coverage claims are about AST implementation-*structure* classes.

## Known hard constraints (do not relax)

- Single training seed (43); pilot seed 42. No seed-level uncertainty exists — never draw it.
- `strategy_annotation_status` is empty in every record: **no algorithm-level diversity claim is permitted.**
  All coverage statements are about AST implementation-structure classes.
- The paired bootstrap is **not recomputable** from the shipped bundle (hashes only, no per-task jsonl).
  State this; never imply it was re-run.
- 16-sample tier and 64-sample tier are different evaluations. Never mix them inside one claim.
- `C_k` (coverage at a k-sample budget) and `D_b` (coverage in b correct draws) are different endpoints.
  Never on one axis.
- Mechanism controls (matched blend / random eigenvectors / isotropic) were implemented and **not run**.
- Rounding: ROUND_HALF_EVEN throughout — 2 dp for pass@1, 1 dp for retention. Nine per-round-tier
  pass@1 values are exact ties.
- Only one declared deviation from the template: `\textfloatsep`/`\intextsep`/`\floatsep` = 9 pt in
  the manuscript preamble. Declared in `COMPLIANCE.md` §3. Reverting costs ~3.5 lines and puts the
  paper over the limit.

## Resolved during this session

- The `-0.0143` vs `-0.0118` pass@1 discrepancy was **not** an error: `-0.01434` is the 64-sample tier,
  `-0.01175` the 16-sample tier. Both correct. Both now labelled by tier wherever they appear.
- Figure 5(b) had been plotting unpaired level differences against a caption declaring paired
  intervals. Fixed at the source, not in the caption.
- Figure 3's footnote collided with panel (a)'s xlabel `λ_max` subscript; the cutoff line struck
  through both panel (b) labels. Both fixed and re-verified.
- Figure 4's caption claimed the \method–SPD-hard pass@1 interval "lies entirely below" the $-1$ pp
  noninferiority line. It does not — the interval is $[-1.89,-0.98]$ pp and straddles it. The
  conclusion was right and the sentence was wrong; both figure and caption now say straddles. This
  one flattered our own arm, so it is worth naming.
- Figures 4 and 5 were rendered at ~4.3 pt effective type because a long in-figure footnote, not the
  plots, was setting the canvas width under `bbox_inches="tight"`. Rebuilt wide-and-short with
  explicit margins and short footnotes: 5.35 / 5.64 pt rendered, and the five figures occupy *less*
  page height than before.
- The length instrument itself was wrong (measured at the `REFERENCES` heading, counted the footer
  page number). Fixed; see `COMPLIANCE.md` §1. The paper was never over the limit.
