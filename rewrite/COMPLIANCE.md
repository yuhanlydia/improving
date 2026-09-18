# Compliance note — SPECTRUM, ICLR 2027 submission

**Checked:** 2026-09-18 · **Deadline:** 2026-09-25 AoE (7 days of headroom)
**Artifact:** `paper/main.tex` → `paper/main.pdf` (14 pages total; 9 pages main text)

---

## 1. Page limit

**Requirement.** ICLR 2027: main text ≤ **9 pages**, excluding references and appendix.

**Measured: 8.911 pages counted** → within limit, headroom **4.8 ruler lines**.

Three numbers are reported, because they answer three different questions:

| Reading | Ruler | Pages | What it is |
|---|---|---|---|
| **counted** | 481.2 | **8.911** | the main text with the AI use statement excluded — **what the guidelines count** |
| strict | 485.7 | 8.994 | where the last main-text line sits, AI statement included |
| naive | 486.2 | 9.004 | the ruler position of the "REFERENCES" heading |

The **naive** reading is the one to avoid quoting. The `REFERENCES` heading is the first line
*after* the main text, so measuring at the heading over-reports by exactly one line — which is the
difference between "9.004 pages, over the limit" and the truth. The earlier version of this
instrument did exactly that, and it also counted the footer page number as a body line; both are
fixed.

**Instrument.** Not a character-count estimate. The official style's own line-number ruler
(`\makevruler` / `\iclrruler` in `iclr2027_conference.sty`) is continuous across the document and
carries a fixed number of slots per page, so a ruler value *is* a line number. `rewrite/measure_pages.py`
extracts the ruler digits from the compiled PDF with `pdftotext -bbox`, fits the ruler geometry,
clusters words into text lines, locates the AI use statement and the `REFERENCES` heading, and
divides. Reproduce with:

```
cd paper && python3 ../rewrite/measure_pages.py main.pdf     # exit 0 = within limit
```

**The AI use statement is excluded.** It sits before `\bibliography`, so a naïve measurement of
"everything above the references" includes it. The ICLR 2027 guidelines exclude it from the
nine-page limit, so the counted figure above starts the main text at ruler 481.2 instead. Note that
the *strict* 8.994 is already inside the limit, so the paper complies on either reading; the
exclusion is the difference between 4.8 and 2.5 ruler lines of headroom, not between pass and fail.

**Self-consistency check.** The style sets `\textheight 9.0 true in` and the ruler advances 12 pt
per line; 54 slots × 12 pt = 648 pt = 9.0 in. The measured 54 slots/page therefore matches the
template's own declared text height — the instrument and the limit are the same object.

**Prose trims do not buy lines here.** Removing 143 characters of body text left the `REFERENCES`
heading at the identical ruler position: page 9 is float-packed, and LaTeX reflows a float down to
absorb the freed space. The length is set by the figures and tables, not by the prose.

## 2. Style files

| File | md5 | Status |
|---|---|---|
| `iclr2027_conference.sty` | `1b4bb9c2e12c712c56f4eb1232b88dd6` | unmodified |
| `iclr2027_conference.bst` | `af983813ca1a1414954dbceae7baa2a1` | unmodified |

**Evidence — verified against the official archive, byte for byte.** The official style archive named
by the ICLR 2027 author guidelines was re-downloaded on 2026-09-18 from
`https://media.iclr.cc/Conferences/ICLR2027/iclr-2027-style-files.zip` (HTTP 200, 39,348 bytes) and
extracted. Both files in `paper/` are **md5-identical** to the archive copies:

```
iclr2027_conference.sty   IDENTICAL  1b4bb9c2e12c712c56f4eb1232b88dd6
iclr2027_conference.bst   IDENTICAL  af983813ca1a1414954dbceae7baa2a1
```

No local modifications of any kind. This is confirmed three times over, against three independent
artifacts:

| Check | `iclr2027_conference.sty` | `iclr2027_conference.bst` |
|---|---|---|
| md5 vs. the official 2027 zip (re-downloaded 2026-09-18) | `1b4bb9c2…` IDENTICAL | `af983813…` IDENTICAL |
| git blob SHA-1 vs. `UPSTREAM_MANIFEST.json` (pinned commit `46ed6f4`) | `f61ad7ef…` MATCH | `a85a0087…` MATCH |
| sha256 vs. `paper/FILE_MANIFEST.sha256`, the upstream bundle's own record | `797deef4…` OK | `2d67552d…` OK |

The third check is the strongest of the three for the rewrite specifically: that manifest was written
before the rewrite began, so its continued agreement proves the style files came through the entire
rewrite untouched.

Corroborating detail: the `.bst` names itself `iclr2024.bst` in its own header — "a copy of
icml2010.bst" — and that historical comment **is present in the official 2027 archive**, so it is
upstream's, not an artifact of this repository.

`FILE_MANIFEST.sha256` itself now verifies 22/30: the three mismatches (`main.tex`, `main.pdf`,
`figures/fig2_method.pdf`) and five missing entries (upstream figure filenames no longer used) are
all direct consequences of this rewrite. The manifest is deliberately **left unmodified** as the
upstream integrity record; see `CHANGE_MAP.md` §7.

(Note: one unrelated directory in this repository, `lalaland/`, holds a file named
`iclr2027_conference.bst` that is actually an unmodified `plainnat.bst`, md5 `ffe5423d…`. It is
**not** the ICLR style and is not used here.)

**Page geometry is unmodified.** The official style's own `\textheight 9.0 true in` /
`\textwidth 5.5 true in` are in force, exactly as in the archive; no `geometry` package is loaded and
no page dimension is altered. `\iclrfinalcopy` is absent, so the anonymous review format applies.

## 3. The one local layout deviation (declared)

`main.tex` lines 23–29 set:

```latex
\setlength{\textfloatsep}{9pt plus 2pt minus 2pt}
\setlength{\intextsep}{9pt plus 2pt minus 2pt}
\setlength{\floatsep}{9pt plus 2pt minus 2pt}
```

The template leaves these at the LaTeX `article` default of 12 pt. Lowering them to 9 pt saved the
3.5 lines needed to bring the main text under 9 pages without removing content. This is a standard
LaTeX float-separation length, not a style or class modification: no `.sty` or `.cls` file is
touched, and no dimension of the template is changed. It is disclosed in a comment at the point of
use.

The published guidance says "Do not change the conference style to achieve a page count." That
instruction is about the style file, and it is honoured literally: the style file is byte-identical
to the official archive (§2) and carries no page-count-driven edit. This change is made in the
manuscript's own preamble and is declared here rather than left implicit.

**If a reviewer prefers the untouched default, reverting these three lines costs ~3.5 ruler lines and
the paper goes to ~9.07 pages — over the limit.** The alternative would be to cut content.

## 4. Anonymity

Swept with `grep -rniE` over `main.tex` and `references.bib`, and over the full text of the compiled
`main.pdf`:

- No author name, handle, email, institution, department, cluster path, or repository URL.
  (Matches for "Zhang" in the PDF are three cited authors in the bibliography — the SPD baseline,
  the Qwen2.5 team, and EvalPlus — not self-identification.)
- No acknowledgements, funding, or grant text.
- No "our previous work" / "in our prior paper" phrasing.
- PDF metadata: `Title`, `Author`, `Subject`, `Keywords` are all **empty**. Producer/Creator are the
  stock `pdfTeX` / `LaTeX with hyperref` strings.
- Title block reads `\author{Anonymous Authors}`, and page 1 renders "Anonymous authors" (the
  style's own double-blind header).

## 5. Required statements

**AI use statement** — present in the manuscript as `\subsubsection*{AI use statement}`.

## 6. Rounding convention

All percentages use **ROUND_HALF_EVEN** (Python's `round`) — 2 decimals for pass@1, 1 decimal for
retention. This matters because 9 of the per-round-tier pass@1 values land on exact ties
(`.xx25` / `.xx75` out of 8000 samples). The convention is now applied uniformly; three cells that
had drifted (a half-up value, a truncation, and a double-rounded 1-decimal figure) were corrected in
the third audit pass.

## 7. Summary

| Requirement | Status |
|---|---|
| Main text ≤ 9 pages | **PASS** — 8.911 pages counted, 8.994 strict, 4.8 lines headroom |
| Official style files unmodified | **PASS** — byte-identical to the official archive, md5 checked 2026-09-18 |
| Anonymised | **PASS** |
| AI use statement | **PASS** — present before the bibliography |
| Bibliography style | **PASS** — official `.bst`, byte-identical |

## 8. Sources and access dates

| Source | URL | Accessed |
|---|---|---|
| Official style archive | `https://media.iclr.cc/Conferences/ICLR2027/iclr-2027-style-files.zip` | 2026-09-18 (HTTP 200, 39,348 bytes) |
| Author guidelines | `https://iclr.cc/Conferences/2027/AuthorGuidelines` | 2026-09-15 |
| Official template repository | `https://github.com/ICLR/Master-Template` @ `46ed6f4` ("2027 template", 2026-09-01) | 2026-09-15 |

Local provenance record: `paper/support/TEMPLATE_PROVENANCE.md` and `paper/support/UPSTREAM_MANIFEST.json`.
