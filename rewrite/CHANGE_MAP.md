# Change map — SPECTRUM ICLR 2027 rewrite

What changed, why, and what deliberately did not. Operation was **restructure + revise**: the
evidence base and the claims are the authors'; the ordering, prose, figures, tables, and every
transcribed number were reworked here.

---

## 1. Structural change: problem-first ordering

| Was | Is | Why |
|---|---|---|
| Method described before the phenomenon it addresses | §2 *Correctness does not identify implementation coverage* comes first and establishes the gap arithmetically | The paper's contribution is a measurement gap, so the gap must be visible before the fix. Task papers should open on the problem. |
| Novelty argued at the end | Contribution claimed in §1 in four running lead-ins, then discharged section by section | Reviewers should not have to reconstruct the claim set. |
| Related work early | §6, after the results | The comparison is empirical; it reads better once the reader has the numbers. |

New: a single-sentence thesis structure in §1 (importance → gap → failure → worse → response →
evidence → implication), and an explicit **two-endpoint** distinction ($D_b$ vs $C_k$) and
**two-tier** distinction (16-sample per-round vs 64-sample final) stated before any number appears.

## 2. Figures — all five rebuilt from source

The upstream `support/make_figures.py` was replaced by `rewrite/make_figures.py`, which reads every
value from the stored result files and carries the provenance in its module docstring.

| Fig | Content | Note |
|---|---|---|
| 1 | Coverage erodes in every arm while pass@1 rises | Two panels on **different denominators**, disclosed in the caption |
| 2 | SPECTRUM's data-generation pipeline, temporary weight folding | Schematic; no data |
| 3 | The soft gain vs the hard projector | Analytic; caption says so explicitly |
| 4 | Paired round-5 effects, 64-sample tier | Includes the pre-declared noninferiority line the result fails |
| 5 | Compounding advantage + saturation | Panel (b) rebuilt as paired differences |

Palette validated with the `dataviz` skill's `validate_palette.js`
(`#2a78d6, #eb6834, #1baf7a` → ALL CHECKS PASS, worst all-pairs CVD ΔE 9.2). Colour is never the only
identity channel: every series carries a direct label or a legend entry.

**Figure defects found and fixed during review:**

1. Fig 5(b) plotted **unpaired level differences** while its own caption and panel (a) declared
   *paired* intervals — regenerated from the paired `comparisons_compact.json` values.
2. Fig 5(b) legend sat inside the plot over the marks; endpoint labels overlapped; bars misaligned
   with ticks — rewritten as a line chart with staggered endpoint labels.
3. Fig 2 had a text label colliding with a box border — removed; the caption and the dotted restore
   gate carry the meaning.
4. Fig 3(b) had the cutoff line striking through both labels (the word "rank" cut by the line, and
   "hard top-$r$ projection" straddling it so its left third sat inside the *discarded* region it does
   not describe) — both repositioned wholly on their own side.
5. Fig 3's footnote sat on panel (a)'s xlabel baseline, with `λ_max`'s descender meeting the word
   "spectra" — footnote moved clear.
6. Fig 3's τ=2 label was anchored at `1/2.76` instead of the true curve value `1/1.76` at μ=0.62.
7. Fig 4 put **$D_4$ and $C_{64}$ on one shared x-axis**. Their effects span 0.64 and 5.38 AST
   classes respectively, so on a shared axis the $D_4$ intervals — about 0.09 wide — collapsed to
   single dots. Rebuilt as a 1×3 row with a separate axis per endpoint.
8. Fig 4's marker key was global but true only of one panel: the diamond meant $D_4$ in (a) and
   pass@1 in (c). Key scoped to "(c):".
9. Fig 4's footnote stated that the \method–SPD-hard pass@1 interval "lies entirely below" the
   $-1$ pp line. It does not: the interval is $[-1.89,-0.98]$ pp, which **straddles** the line. What
   fails is the criterion on its lower bound. Caption and figure now both say straddles — this is
   the paper's own adverse result, so the imprecision flattered us and had to go.
10. Fig 5(b)'s legend, unframed at the top of the panel, had the zero reference line running through
    its last row. The line spans the full width and an unframed legend cannot occlude it, so the
    legend moved to the empty lower-left corner — which also let the range top drop from $0.30$ to
    $0.12$ and gave the data more vertical resolution.

**Rendered size.** Every figure is included at `\textwidth`, so its on-page height is
$5.5 \times h/w$ and its type is scaled by $5.5/w$ — widening the canvas shortens the figure on the
page *and* enlarges the type. The constraint is that with `bbox_inches="tight"` a long in-figure
footnote becomes the widest object and sizes the canvas to the **text** rather than the plots. Fig 4's
canvas had been inflated to 9.00 in that way, scaling every label by 0.611, and fig 5's to 8.44 in
(0.652). Both now use an explicit wide-and-short canvas with `subplots_adjust` margins instead of the
defaults, and footnotes short enough not to set the width:

| Figure | Canvas before → after | Type scale before → after | Rendered type now |
|---|---|---|---|
| 4 | 9.00 → 8.01 in | 0.611 → 0.687 | 4.87–6.04 pt (from 7.1–8.8 pt stated) |
| 5 | 8.44 → 7.61 in | 0.652 → 0.723 | 5.71–6.58 pt (from 7.9–9.1 pt stated) |

The five figures' total on-page height *fell* over the same change, 8.773 → 8.454 in: the wider
canvas pays for the larger type several times over.

**Automated check.** `rewrite/check_figures.py` reads the compiled figure PDFs back with
`pdftotext -bbox` and reports clipped text and colliding text runs. All five are clean: **0 clipped,
0 colliding**. Reproduce with:

```
cd rewrite && python3 check_figures.py        # exit 0 = no collisions
```

The check's discriminating rule needs a word of justification, because the obvious version is
wrong. pdftotext gives each word the full glyph box — ascender to descender — not the ink, so
consecutive lines of an ordinary wrapped label overlap by 19–30% of the type height at matplotlib's
default linespacing (measured here: baseline gaps of 6.6–8.0 pt under glyph boxes of 7.5–9.3 pt).
An area-overlap test flags every multi-line label in every figure. A real collision instead shows
the two runs sharing a baseline, so the rule is dimension-based: an overlap of at least 35% of the
smaller box in **both** dimensions, with a 1.5 pt floor. Pairs between 15% and 35% are printed as
`tight` warnings rather than failures. Under that rule the only remaining warnings are subscripts
tucked under their base ($D_4$, $C_{64}$, $\lambda_{\max}$), which overlap vertically but only
partially in x — exactly the case the width test exists to exclude.

One such warning was a genuine defect and was fixed rather than argued away: fig 5's footnote sat
6.6 pt below a series end-label, crowding it, and was dropped 3 pt.

## 3. Tables

- Captions rewritten to carry the protocol (tier, sample budget, seed, pairing rule, $n$) rather than
  leaving it in the body text.
- Table 3's $D_{64}$ row is retained but captioned as resting on only 18–30 paired tasks and not to
  be read as equal-quality evidence.
- Three rounding-convention defects corrected so every percentage uses ROUND_HALF_EVEN (see
  `COMPLIANCE.md` §6).
- Table 4's caption corrected: it claimed intervals for all levels when only the undistilled row has
  them.

## 4. Numeric corrections across three audit passes

Three independent audit passes re-derived every number from source. The material defects found and
fixed are tabulated below; the two that flattered our own arm are the ones that matter most. (Each
pass verified the previous pass's corrections before looking for new ones, so a later pass finding a
defect is not evidence the earlier one was wrong — only that it had not looked there yet.)

| # | Was | Is | Severity |
|---|---|---|---|
| 1 | "second of four on pass@1" | "**third** of four" | Rank claim contradicted by our own Table 1 |
| 2 | plain pass@1 "41.5%" | "**41.4%**" | 1-dp double-rounding |
| 3 | $D_8$ retention "91.0%" | "**91.1%**" | Pre-rounded the ratio from 3-dp table values |
| 4 | Table 4 `38.43` / `39.77` | `38.42` / `39.78` | Mixed rounding conventions |
| 5 | Intro paired 64-tier retentions with per-round-tier deltas, unlabelled | Tiers named | Tier mixing |
| 6 | Statistics gave $D_b$ eligible-$n$ ranges without a tier | "on the 64-sample tier" | Tier mixing |
| 7 | Appendix A derived "met against neither comparator" from the 16-tier alone | Now cites the 64-tier plain comparison | Logically impossible in that tier |

The full list of verified values is in `CLAIM_EVIDENCE.md`.

## 5. Honest-reporting changes

- The failed pass@1 noninferiority criterion is stated **once plainly in §5.4**, **once in §6
  (Limitations)**, and in the abstract as a cost, not a trade-off. The words "trade-off" and
  "noninferior" are never applied to it.
- Every claim touching diversity is held at the **implementation-structure** level, because
  `strategy_annotation_status` is empty in every record. The manuscript says this in §2 and in the
  Figure 1 caption.
- The mechanism controls (matched blend / random eigenvectors / isotropic) are declared
  **implemented but not run**, in §3.3 and in Appendix F — not quietly omitted.
- No seed-level uncertainty is claimed or drawn anywhere: one training seed.

## 6. Length

The main text measured **9.065 pages** against a 9.00 limit. Closing it:

- Whole-line structural cuts (contribution list flattened, duplicated sentences removed, captions
  compressed) — necessary but not sufficient.
- `\textfloatsep` / `\intextsep` / `\floatsep` set to 9 pt in the manuscript preamble — the decisive
  change. **Not** a style-file edit; see `COMPLIANCE.md` §3 for the declaration.
- Figures rebuilt wide-and-short (see §2): their total on-page height fell 8.773 → 8.454 in, which is
  worth about two ruler lines.

Result: **8.911 pages counted**, 4.8 ruler lines of headroom — or 8.994 / 2.5 lines if the AI use
statement is counted in, which the guidelines do not. Measured from the compiled PDF using the
official template's own line-number ruler (`rewrite/measure_pages.py`).

The intermediate figure of **8.929 pages** that appeared here earlier was produced by the first
version of that instrument, which measured at the `REFERENCES` heading (one line *past* the main
text) and counted the footer page number as a body line. The current numbers are not a change in the
paper — the paper's length moved by less than a line — but a correction to the ruler.

## 7. What was deliberately NOT changed

- The empirical claims, the metric definitions, the protocol, and the adverse result. The rewrite
  re-orders and re-words; it does not re-argue the evidence.
- The style files, bibliography style, and page geometry — byte-identical to the official archive.
- The single-seed scope and the AST-proxy scope. Neither was softened.
- `paper/FILE_MANIFEST.sha256`. It is the **upstream bundle's integrity record**, and it was
  deliberately left unmodified rather than regenerated: its continued agreement on
  `iclr2027_conference.sty` / `.bst` is the proof that the style files came through the rewrite
  untouched (see `COMPLIANCE.md` §2). It now verifies 22/30 — the three mismatches (`main.tex`,
  `main.pdf`, `figures/fig2_method.pdf`) and five missing entries (upstream figure filenames we no
  longer use) are all expected consequences of the rewrite, not corruption. Anyone re-running
  `sha256sum -c FILE_MANIFEST.sha256` should expect exactly those eight lines.
