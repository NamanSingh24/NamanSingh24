#!/usr/bin/env python3
"""
Turn source-prepped.png into a self-typing monochrome ASCII SVG.

Each row is wrapped in a clip that wipes left to right, with a small
block cursor riding the wipe edge. Rows are staggered top to bottom.
Plays once on load and freezes. SMIL-free (pure CSS keyframes), which
GitHub renders inside an <img>-embedded SVG.

    python scripts/make_ascii_svg.py
Writes naman-ascii.svg
"""

import os
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image

SRC = "source-prepped.png"
OUT = "naman-ascii.svg"

COLS = 100
ROWS = 53

# bright (sparse) -> dark (dense). Leading space clears the background.
RAMP = " .`:-=+*cs#%@"

CH_W = 6.02        # character advance for the font size below
CH_H = 10.6        # line height
FONT_SIZE = 10
PAD = 14

INK = "#c9d1d9"    # one color. Rainbow ASCII reads as static.
CURSOR = "#39d353"
BG = "none"

ROW_DUR = 0.42     # seconds for one row to wipe
ROW_STAGGER = 0.035


def to_ascii(path: str) -> list[str]:
    img = Image.open(path).convert("L")

    # characters are taller than wide, so squash vertically to keep
    # the portrait's aspect ratio
    img = img.resize((COLS, ROWS), Image.LANCZOS)
    arr = np.array(img).astype(np.float32) / 255.0

    # gamma nudge so midtones land in the middle of the ramp
    arr = np.clip(arr ** 1.05, 0.0, 1.0)

    idx = ((1.0 - arr) * (len(RAMP) - 1)).round().astype(int)
    return ["".join(RAMP[i] for i in row) for row in idx]


def build_svg(rows: list[str]) -> str:
    w = int(COLS * CH_W + PAD * 2)
    h = int(ROWS * CH_H + PAD * 2)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="ASCII portrait">',
        "<style>",
        f"  .a{{font-family:'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace;"
        f"font-size:{FONT_SIZE}px;fill:{INK};white-space:pre;letter-spacing:0}}",
        "  .wipe{transform-origin:left center;animation:wipe var(--d) steps(60,end) both;"
        "animation-delay:var(--t)}",
        "  .cur{fill:" + CURSOR + ";opacity:0;animation:cur var(--d) linear both;"
        "animation-delay:var(--t)}",
        "  @keyframes wipe{from{transform:scaleX(0)}to{transform:scaleX(1)}}",
        "  @keyframes cur{0%{opacity:1}92%{opacity:1}100%{opacity:0}}",
        "</style>",
        f'<rect width="100%" height="100%" fill="{BG}"/>',
    ]

    row_w = COLS * CH_W

    for i, line in enumerate(rows):
        y = PAD + (i + 1) * CH_H
        delay = round(i * ROW_STAGGER, 3)
        cid = f"c{i}"

        parts.append(
            f'<clipPath id="{cid}"><rect class="wipe" '
            f'style="--d:{ROW_DUR}s;--t:{delay}s" '
            f'x="{PAD}" y="{y - CH_H}" width="{row_w:.1f}" height="{CH_H}"/></clipPath>'
        )
        parts.append(
            f'<text class="a" clip-path="url(#{cid})" x="{PAD}" y="{y:.1f}">'
            f"{escape(line)}</text>"
        )

        # cursor block rides the wipe edge
        parts.append(
            f'<rect class="cur" style="--d:{ROW_DUR}s;--t:{delay}s" '
            f'x="{PAD}" y="{y - CH_H + 2:.1f}" width="{CH_W:.1f}" height="{CH_H - 3:.1f}">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + row_w:.1f}" '
            f'dur="{ROW_DUR}s" begin="{delay}s" fill="freeze"/></rect>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    if not os.path.exists(SRC):
        raise SystemExit(f"{SRC} not found. Run prep_photo.py first.")
    svg = build_svg(to_ascii(SRC))
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"wrote {OUT}")
