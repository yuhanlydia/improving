# ICLR 2027 template provenance

Retrieved 2026-09-15 from the official ICLR sources.

- Author guidelines: https://iclr.cc/Conferences/2027/AuthorGuidelines
- Official archive linked by that guide: https://media.iclr.cc/Conferences/ICLR2027/iclr-2027-style-files.zip
- Official repository: https://github.com/ICLR/Master-Template
- Pinned commit: https://github.com/ICLR/Master-Template/commit/46ed6f4c6cef5b175dde23639e77d44c3463b230
- Commit description: `2027 template`; date: 2026-09-01.

All seven files in the downloaded official archive match the Git blob SHA-1 values of the pinned repository files. `UPSTREAM_MANIFEST.json` records each path, hash, and immutable source URL. Files were copied without changes. The historical `iclr2024.bst` comment inside the 2027 bibliography style is present upstream and has been retained.

The official submission limit is nine pages of main text. References are excluded; appendices follow the bibliography. The guide gives ten pages for discussion/rebuttal and camera-ready versions. Anonymous review is required. A mandatory AI use statement is excluded from the main-text limit; the template places it before the references and limits it to one page.

Use `\documentclass{article}` and `\usepackage{iclr2027_conference,times}`. Leave `\iclrfinalcopy` absent or commented out for anonymous review. Use `\bibliographystyle{iclr2027_conference}`. The style selects author-year citations with round parentheses and loads `natbib`, `fancyhdr`, and `eso-pic`. Do not change the conference style to achieve a page count. `math_commands.tex` is optional and can be omitted if the manuscript defines its own notation.

For a compact paper source bundle, include `main.tex`, its bibliography file, `iclr2027_conference.sty`, and `iclr2027_conference.bst`; use the normal TeX-distribution installations of `natbib`, `fancyhdr`, `eso-pic`, and `times`. The official template also provides bundled copies of `fancyhdr.sty` and `natbib.sty`. The bundled natbib file is version 8.31 and its header requests distribution with the original `natbib.dtx`; it is therefore simplest to use the TeX installation's natbib package rather than redistribute that standalone generated file. No changes to the conference style are needed.

The original copyright and license notices are retained inside the support files. `license_sources/lppl.txt` is the unmodified LPPL 1.3c text downloaded from https://www.latex-project.org/lppl/lppl-1-3c.txt. The conference bibliography style and fancyhdr/natbib notices permit LPPL version 1 or later. The repository does not present a separate root LICENSE file in its file listing.
