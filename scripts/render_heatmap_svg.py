#!/usr/bin/env python3
"""
Render data/contributions.json as a 53-week x 7-day calendar of rounded
boxes with a diagonal slide-down reveal that plays once and freezes.

    python scripts/render_heatmap_svg.py
Writes contrib-heatmap.svg
"""

import json
from datetime import datetime

SRC = "data/contributions.json"
OUT = "contrib-heatmap.svg"

BOX = 11
GAP = 3
R = 2.5
PAD_L = 30
PAD_T = 26
PAD_B = 44
PAD_R = 16

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

LABEL = "#7d8590"
BRIGHT = "#c9d1d9"
RULE = "#30363d"

STEP = 0.012      # per-diagonal stagger
DUR = 0.34

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def level(count: int, p90: int) -> int:
    if count <= 0:
        return 0
    if p90 <= 0:
        return 3
    frac = count / p90
    if frac <= 0.25:
        return 1
    if frac <= 0.50:
        return 2
    if frac <= 0.80:
        return 3
    if frac <= 1.10:
        return 4
    return 5


def main() -> None:
    with open(SRC) as f:
        data = json.load(f)

    days = data["days"]
    counts = sorted(d["count"] for d in days if d["count"] > 0)
    p90 = counts[int(len(counts) * 0.90)] if counts else 1

    # bucket into weeks starting Sunday
    first = datetime.strptime(days[0]["date"], "%Y-%m-%d").date()
    lead = (first.weekday() + 1) % 7   # Python Mon=0; calendar wants Sun=0

    grid: list[list[dict | None]] = []
    week: list[dict | None] = [None] * lead

    for d in days:
        week.append(d)
        if len(week) == 7:
            grid.append(week)
            week = []
    if week:
        week += [None] * (7 - len(week))
        grid.append(week)

    weeks = len(grid)
    w = PAD_L + weeks * (BOX + GAP) + PAD_R
    h = PAD_T + 7 * (BOX + GAP) + PAD_B

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="Contribution activity">',
        "<style>",
        "  .m{font-family:'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace}",
        "  .c{opacity:0;animation:pop var(--d) ease-out both;animation-delay:var(--t)}",
        "  @keyframes pop{from{opacity:0;transform:translateY(-5px)}"
        "to{opacity:1;transform:translateY(0)}}",
        "</style>",
        '<rect width="100%" height="100%" fill="none"/>',
    ]

    # month labels
    seen = set()
    for wi, wk in enumerate(grid):
        for d in wk:
            if not d:
                continue
            dt = datetime.strptime(d["date"], "%Y-%m-%d").date()
            if dt.day <= 7 and dt.month not in seen:
                seen.add(dt.month)
                x = PAD_L + wi * (BOX + GAP)
                p.append(
                    f'<text class="m" x="{x}" y="{PAD_T - 8}" font-size="9" '
                    f'fill="{LABEL}">{MONTHS[dt.month - 1]}</text>'
                )
            break

    # weekday labels
    for di, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = PAD_T + di * (BOX + GAP) + BOX - 2
        p.append(
            f'<text class="m" x="0" y="{y}" font-size="9" fill="{LABEL}">{name}</text>'
        )

    # boxes, diagonal reveal
    for wi, wk in enumerate(grid):
        for di, d in enumerate(wk):
            if not d:
                continue
            x = PAD_L + wi * (BOX + GAP)
            y = PAD_T + di * (BOX + GAP)
            lv = level(d["count"], p90)
            delay = round((wi + di) * STEP, 3)
            p.append(
                f'<rect class="c" style="--d:{DUR}s;--t:{delay}s" '
                f'x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="{R}" ry="{R}" '
                f'fill="{PALETTE[lv]}">'
                f'<title>{d["count"]} on {d["date"]}</title></rect>'
            )

    # footer
    fy = PAD_T + 7 * (BOX + GAP) + 20
    p.append(
        f'<line x1="{PAD_L}" y1="{fy - 12}" x2="{w - PAD_R}" y2="{fy - 12}" '
        f'stroke="{RULE}" stroke-width="1"/>'
    )
    p.append(
        f'<text class="m" x="{PAD_L}" y="{fy + 6}" font-size="10" fill="{BRIGHT}">'
        f'{data["total"]:,} contributions in the last year</text>'
    )
    p.append(
        f'<text class="m" x="{PAD_L}" y="{fy + 21}" font-size="9" fill="{LABEL}">'
        f'current streak {data["current_streak"]}d  ·  longest {data["longest_streak"]}d'
        f'  ·  best day {data["best_day"]["count"]}</text>'
    )

    # legend
    lx = w - PAD_R - (len(PALETTE) * (BOX + GAP)) - 62
    p.append(
        f'<text class="m" x="{lx - 26}" y="{fy + 6}" font-size="9" fill="{LABEL}">Less</text>'
    )
    for i, c in enumerate(PALETTE):
        p.append(
            f'<rect x="{lx + i * (BOX + GAP)}" y="{fy - 4}" width="{BOX}" height="{BOX}" '
            f'rx="{R}" ry="{R}" fill="{c}"/>'
        )
    p.append(
        f'<text class="m" x="{lx + len(PALETTE) * (BOX + GAP) + 4}" y="{fy + 6}" '
        f'font-size="9" fill="{LABEL}">More</text>'
    )

    p.append("</svg>")

    with open(OUT, "w") as f:
        f.write("\n".join(p))
    print(f"wrote {OUT}  weeks={weeks}")


if __name__ == "__main__":
    main()
