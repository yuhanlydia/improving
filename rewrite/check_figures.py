#!/usr/bin/env python3
"""Check the generated figures for clipped and colliding text.

Two failure modes, both of which the eye misses at print size but a reviewer
does not:

  clipping  a text run whose bbox falls outside the page's media box, i.e. text
            that matplotlib drew but the PDF does not show.
  collision two text runs whose bboxes overlap, i.e. one label printed on top of
            another.

Both are read off the compiled PDF rather than the matplotlib objects, because
the PDF is what the manuscript includes; a layout that is correct in the figure
script can still be wrong once the canvas is cropped to its tight bbox.

Thresholds.  pdftotext reports each word separately, and a word's bbox is the
full glyph box -- ascender to descender -- not the ink.  Two consequences:

  * Adjacent words on one line can touch by a fraction of a point (kerning).
  * Consecutive lines of one wrapped label overlap by about 11% of the glyph
    height at matplotlib's default linespacing of 1.2, because the upper line's
    empty descender space sits under the lower line's empty ascender space.
    Measured on these figures: baseline gaps of 6.6--8.0 pt under glyph boxes of
    7.5--9.3 pt, i.e. overlaps of 19--30% of the smaller box.

So a bbox overlap is *not* by itself a defect, and a threshold near zero would
fail every multi-line label in every figure.  A real collision has the two runs
sharing a baseline (dy near 0) and therefore overlapping by most of their
height.  The rule below is dimension-based rather than area-based for the same
reason: a collision is reported only when the runs overlap by at least
COLLIDE_FRAC of the smaller run's height *and* width, with an absolute floor.
Anything in the TIGHT band between the two is printed as a warning -- too close
to be comfortable, not overlapping -- and does not fail the check.

Usage:  python3 check_figures.py [figures_dir]      # exit 0 = no collisions
"""
import glob
import os
import re
import subprocess
import sys
import tempfile

FIGDIR = sys.argv[1] if len(sys.argv) > 1 else "figures"
COLLIDE_FRAC = 0.35       # overlap as a share of the smaller glyph box
COLLIDE_MIN_PT = 1.5      # ...and never call a sub-1.5 pt touch a collision
TIGHT_FRAC = 0.15         # below COLLIDE_FRAC but worth reporting
EDGE_TOL = 0.5            # pt of slack before calling text clipped

WORD = re.compile(
    r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>'
)


def page_size(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    m = re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", out)
    return float(m.group(1)), float(m.group(2))


def words(pdf, page):
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as fh:
        xml_path = fh.name
    try:
        subprocess.run(
            ["pdftotext", "-bbox", "-f", str(page), "-l", str(page), pdf, xml_path],
            check=True, capture_output=True,
        )
        xml = open(xml_path, encoding="utf-8", errors="replace").read()
    finally:
        os.unlink(xml_path)
    return [
        (float(a), float(b), float(c), float(d), e)
        for a, b, c, d, e in WORD.findall(xml)
    ]


def n_pages(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    return int(re.search(r"Pages:\s+(\d+)", out).group(1))


def overlap(a, b):
    """(overlap width, overlap height, overlap area) of two bboxes."""
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    if w <= 0 or h <= 0:
        return 0.0, 0.0, 0.0
    return w, h, w * h


def check(pdf):
    """(clipped runs, collisions, tight pairs) for one figure."""
    W, H = page_size(pdf)
    clipped, collisions, tight = [], [], []
    for page in range(1, n_pages(pdf) + 1):
        ws = words(pdf, page)
        for x0, y0, x1, y1, t in ws:
            if (x0 < -EDGE_TOL or y0 < -EDGE_TOL
                    or x1 > W + EDGE_TOL or y1 > H + EDGE_TOL):
                clipped.append((t, x0, y0, x1, y1))
        for i in range(len(ws)):
            for j in range(i + 1, len(ws)):
                a, b = ws[i], ws[j]
                w, h, _ = overlap(a, b)
                if w <= 0 or h <= 0:
                    continue
                ha, hb = a[3] - a[1], b[3] - b[1]
                wa, wb = a[2] - a[0], b[2] - b[0]
                fh, fw = h / min(ha, hb), w / min(wa, wb)
                if fh >= COLLIDE_FRAC and fw >= COLLIDE_FRAC and h >= COLLIDE_MIN_PT:
                    collisions.append((a[4], b[4], w, h, fh))
                elif fh >= TIGHT_FRAC and h >= COLLIDE_MIN_PT:
                    tight.append((a[4], b[4], w, h, fh))
    return clipped, collisions, tight


def main():
    pdfs = sorted(glob.glob(os.path.join(FIGDIR, "*.pdf")))
    if not pdfs:
        print(f"no figures in {FIGDIR}")
        return 2
    bad = 0
    for pdf in pdfs:
        W, H = page_size(pdf)
        clipped, collisions, tight = check(pdf)
        name = os.path.basename(pdf)
        note = f"{W / 72:.2f} x {H / 72:.2f} in"
        if not clipped and not collisions:
            tail = f"{len(tight)} tight pair(s), no ink collision" if tight else "no overlaps"
            print(f"OK    {name:24s} {note:18s} 0 clipped, 0 colliding; {tail}")
            for ta, tb, w, h, fh in sorted(tight, key=lambda r: -r[4])[:4]:
                print(f"        tight: {ta!r} over {tb!r}  "
                      f"{fh * 100:.0f}% of glyph height ({h:.1f} pt)")
            continue
        bad += 1
        print(f"FAIL  {name:24s} {note:18s} "
              f"{len(clipped)} clipped, {len(collisions)} colliding")
        for t, x0, y0, x1, y1 in clipped:
            print(f"        clipped: {t!r} bbox=({x0:.1f},{y0:.1f})-({x1:.1f},{y1:.1f})")
        for ta, tb, w, h, fh in collisions[:12]:
            print(f"        collide: {ta!r} x {tb!r}  "
                  f"({w:.1f} x {h:.1f} pt = {fh * 100:.0f}% of glyph height)")
    print(f"\n{len(pdfs) - bad}/{len(pdfs)} figures clean")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
