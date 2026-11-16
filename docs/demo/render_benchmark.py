#!/usr/bin/env python3
"""Draws docs/benchmark-k562-{light,dark}.svg, the benchmark chart shown in README.md.

Run from anywhere:  python3 docs/demo/render_benchmark.py
The numbers are the medians in docs/benchmark-k562.md (STAR 2.7.11b vs the
historical Tachyon 0.4 build; 5,000,000 K562 read pairs, 16 threads, warm cache).
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent

THEMES = {
    "light": dict(surface="#fcfcfb", ink="#0b0b0b", ink2="#52514e", muted="#7a7973",
                  grid="#e4e3df", star="#2a78d6", tachyon="#eb6834"),
    "dark": dict(surface="#1a1a19", ink="#f0efec", ink2="#c3c2b7", muted="#9a998f",
                 grid="#33332f", star="#3987e5", tachyon="#d95926"),
}

# (panel title, subtitle, unit formatter, rows)  rows: (label, STAR value, Tachyon value)
PANELS = [
    ("Wall time", "seconds, lower is better", lambda v: f"{v:,.1f} s",
     [("Alignment of 5M read pairs", 113.59, 24.345)]),
    ("Throughput", "read pairs per second, higher is better", lambda v: f"{v:,.0f}",
     [("Read pairs per second", 44018, 205381)]),
    ("Memory", "GiB, lower is better", lambda v: f"{v:.2f} GiB",
     [("Peak RSS (includes mapped index pages)", 32.92, 37.63),
      ("Private anonymous memory", 32.87, 5.05)]),
]

W = 860
LEFT, RIGHT = 24, 24
BAR_X, BAR_MAX = 24, 600          # bars start at BAR_X, longest bar is BAR_MAX px
BAR_H, GAP = 22, 4
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"


def bar(x, y, w, h, r=4):
    """Horizontal bar: square at the baseline (left), rounded data end (right)."""
    r = min(r, w / 2)
    return (f"M{x:.1f},{y:.1f} H{x + w - r:.1f} Q{x + w:.1f},{y:.1f} {x + w:.1f},{y + r:.1f} "
            f"V{y + h - r:.1f} Q{x + w:.1f},{y + h:.1f} {x + w - r:.1f},{y + h:.1f} H{x:.1f} Z")


def render(mode):
    t = THEMES[mode]
    parts, y = [], 0
    # header
    parts.append(f'<text x="{LEFT}" y="34" font-size="20" font-weight="600" fill="{t["ink"]}">'
                 f'Tachyon vs STAR 2.7.11b: 4.7× faster on the same RNA-seq input</text>')
    parts.append(f'<text x="{LEFT}" y="56" font-size="13" fill="{t["ink2"]}">'
                 f'ENCODE K562, first 5 million read pairs, GRCh38 + Ensembl 115, 16 threads, warm cache, median of 2 runs</text>')
    # legend
    lx = LEFT
    for name, col in (("STAR 2.7.11b", t["star"]), ("Tachyon 0.4", t["tachyon"])):
        parts.append(f'<rect x="{lx}" y="72" width="12" height="12" rx="3" fill="{col}"/>')
        parts.append(f'<text x="{lx + 18}" y="83" font-size="13" fill="{t["ink2"]}">{name}</text>')
        lx += 150
    y = 108
    for title, sub, fmt, rows in PANELS:
        parts.append(f'<line x1="{LEFT}" y1="{y - 12}" x2="{W - RIGHT}" y2="{y - 12}" stroke="{t["grid"]}" stroke-width="1"/>')
        parts.append(f'<text x="{LEFT}" y="{y + 8}" font-size="15" font-weight="600" fill="{t["ink"]}">{title}</text>')
        parts.append(f'<text x="{LEFT + len(title) * 9 + 12}" y="{y + 8}" font-size="12" fill="{t["muted"]}">{sub}</text>')
        y += 22
        scale = BAR_MAX / max(max(r[1], r[2]) for r in rows)
        for label, star, tach in rows:
            parts.append(f'<text x="{LEFT}" y="{y + 12}" font-size="12" fill="{t["ink2"]}">{label}</text>')
            y += 18
            for val, col in ((star, t["star"]), (tach, t["tachyon"])):
                w = max(val * scale, 3)
                parts.append(f'<path d="{bar(BAR_X, y, w, BAR_H)}" fill="{col}"><title>{fmt(val)}</title></path>')
                parts.append(f'<text x="{BAR_X + w + 8:.1f}" y="{y + 15}" font-size="13" font-weight="600" fill="{t["ink"]}">{fmt(val)}</text>')
                y += BAR_H + GAP
            y += 10
        y += 14
    parts.append(f'<text x="{LEFT}" y="{y - 2}" font-size="11.5" fill="{t["muted"]}">'
                 f'Author-run historical benchmark of Tachyon 0.4 (not 0.4.1); STAR reference runs were reused. Tachyon used Mmap and a 4 GiB auxiliary index table.</text>')
    parts.append(f'<text x="{LEFT}" y="{y + 15}" font-size="11.5" fill="{t["muted"]}">'
                 f'Output matched STAR: alignment records and splice junctions (fingerprints, 2/2 runs). Details: docs/benchmark-k562.md</text>')
    h = y + 30
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" '
           f'font-family="{FONT}" role="img" aria-labelledby="t d">\n'
           f'<title id="t">Tachyon vs STAR 2.7.11b benchmark on ENCODE K562</title>\n'
           f'<desc id="d">STAR: 113.59 s, 44,018 read pairs/s, 32.92 GiB peak RSS, 32.87 GiB anonymous. '
           f'Tachyon 0.4: 24.345 s, 205,381 read pairs/s, 37.63 GiB peak RSS, 5.05 GiB anonymous.</desc>\n'
           f'<rect width="{W}" height="{h}" rx="8" fill="{t["surface"]}"/>\n' + "\n".join(parts) + "\n</svg>\n")
    (OUT / f"benchmark-k562-{mode}.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    for m in THEMES:
        render(m)
