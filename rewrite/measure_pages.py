#!/usr/bin/env python3
"""Measure the ICLR main-text length from the compiled PDF.

The official iclr2027_conference.sty draws a line-number ruler in the left
margin (\\makevruler).  The ruler is continuous across the document and each
page carries a fixed number of slots (textheight / baselineskip), so a ruler
value is a line number and dividing it by the slots per page gives pages.

Three quantities are reported, because they answer three different questions:

  strict   the line on which the last main-text line sits, i.e. where the main
           text actually ends.  This is the number to compare against the limit.
  naive    the ruler position of the "REFERENCES" heading.  The heading is the
           first line *after* the main text, so this over-reports by one line;
           it is what a reader who simply looks for the heading would measure.
  counted  the strict end with the AI use statement excluded, which is what the
           ICLR 2027 guidelines count (that statement is excluded from the
           nine-page limit).

Exit code 0 if the counted length is within LIMIT, 1 otherwise.

Usage:  python3 measure_pages.py [main.pdf]
"""
import re
import subprocess
import sys
import tempfile
import os

LIMIT = 9.0
PDF = sys.argv[1] if len(sys.argv) > 1 else "main.pdf"
WORD = re.compile(
    r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>'
)


def words_of_page(pdf, page):
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


def ruler_geometry(ws):
    """(y of the first ruler slot, its value, pt per ruler line, slots)."""
    slots = sorted(
        (y, int(t)) for x0, y, x1, y1, t in ws
        if x0 < 80 and re.fullmatch(r"\d{3}", t)      # left margin only
    )
    if len(slots) < 5:
        return None
    (y0, n0), (y1, n1) = slots[0], slots[-1]
    return y0, n0, (y1 - y0) / (n1 - n0), n1 - n0 + 1


def text_lines(ws):
    """Body lines of one page as (ruler position, text), top to bottom."""
    geo = ruler_geometry(ws)
    if geo is None:
        return None, None
    y0, n0, pt_per_line, n_slots = geo
    # Cluster words into text lines by y (small-caps headings emit each letter
    # as its own word at slightly different y, so exact equality is not enough).
    body = sorted(
        ((y, x0, t) for x0, y, x1, y1, t in ws if x0 > 85), key=lambda r: (r[0], r[1])
    )
    lines = []
    for y, x0, t in body:
        if lines and y - lines[-1][0] <= 3.0:
            lines[-1][1].append((x0, t))
        else:
            lines.append((y, [(x0, t)]))
    out = []
    for y, parts in lines:
        txt = " ".join(t for _, t in sorted(parts))
        pos = n0 + (y - y0) / pt_per_line
        # The footer page number sits below the ruler's last slot; it is not a
        # main-text line and would otherwise be read as the end of the text.
        if pos > n0 + n_slots:
            continue
        out.append((pos, txt))
    return out, (n0, n_slots)


def main():
    n_pages = int(re.search(
        rb"Output written on \S+ \((\d+) pages", open("main.log", "rb").read()
    ).group(1)) if os.path.exists("main.log") else None

    strict = naive = ai_start = per_page = None
    prev_last = None
    for page in range(1, 40):
        try:
            ws = words_of_page(PDF, page)
        except subprocess.CalledProcessError:
            break
        lines, rinfo = text_lines(ws)
        if lines is None:
            continue
        per_page = round(rinfo[1])
        for pos, txt in lines:
            flat = re.sub(r"[^A-Za-z]", "", txt).upper()
            if flat.startswith("REFERENCES") and naive is None:
                naive = pos
                strict = prev_last
            elif flat.startswith("AIUSESTATEMENT") and ai_start is None:
                ai_start = pos
            prev_last = pos
        if naive is not None:
            break
    if naive is None:
        print("could not locate the References heading")
        return 2

    counted = ai_start if (ai_start is not None and ai_start < naive) else strict
    print(f"ruler: {per_page} slots/page")
    if ai_start is not None and ai_start < naive:
        print(f"  AI use statement starts at ruler {ai_start:.1f} "
              f"(excluded from the limit by the ICLR 2027 guidelines)")
    print(f"  main text ends at ruler {strict:.1f}   -> {strict / per_page:.3f} pages (strict)")
    print(f"  REFERENCES heading at ruler {naive:.1f} -> {naive / per_page:.3f} pages (naive; "
          f"the heading is the first line after the main text)")
    print(f"MAIN TEXT = {counted / per_page:.3f} pages  [limit {LIMIT}]  -> "
          f"{'OK' if counted / per_page <= LIMIT else 'OVER'}")
    print(f"  headroom = {(LIMIT - counted / per_page) * per_page:.1f} ruler lines")
    if n_pages:
        print(f"  total PDF = {n_pages} pages")
    return 0 if counted / per_page <= LIMIT else 1


if __name__ == "__main__":
    sys.exit(main())
