#!/usr/bin/env python3
"""
Hand-authored neofetch-style info card SVG.

Lines fade and slide in on a short stagger so the panel looks like it
is printing next to the portrait.

    python scripts/make_info_card.py
    STATIC=1 python scripts/make_info_card.py   # frozen frame

Writes info-card.svg
"""

import os
from xml.sax.saxutils import escape

OUT = "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

W = 490
PAD = 18
FONT = 11.5
LINE_H = 17.5
TITLE_H = 30

KEY = "#39d353"
VAL = "#c9d1d9"
DIM = "#7d8590"
ACCENT = "#58a6ff"
RULE = "#30363d"

STAGGER = 0.07
FADE = 0.45

# (key, value) — None key means a full-width continuation line
LINES = [
    ("role", "Product Engineer · Agentic AI"),
    ("focus", "Multi-agent systems, RAG, correctness"),
    ("edu", "B.Tech CS & Applied Math, IIIT Delhi"),
    ("loc", "New Delhi, India"),
    (None, ""),
    ("stack", "Python · FastAPI · LangGraph · LangChain"),
    (None, "Qdrant · pgvector · Redis · MongoDB"),
    (None, "Celery · Socket.IO · Docker · AWS"),
    (None, "Playwright · PyTest · PyTorch"),
    (None, ""),
    ("building", "NL -> executable workflow engine"),
    (None, "Multi-agent delegation w/ HITL takeover"),
    (None, "Three-tier retrieval orchestrator"),
    (None, "LLM correctness + grounding test suites"),
    (None, ""),
    ("also", "Founder, CrescoCare (social welfare NGO)"),
    ("open to", "AI / product engineering conversations"),
]

KEY_W = 62


def build() -> str:
    body_h = len(LINES) * LINE_H
    h = int(TITLE_H + body_h + PAD * 2 + 10)

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
        f'viewBox="0 0 {W} {h}" role="img" aria-label="Profile info card">',
        "<style>",
        "  .m{font-family:'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace}",
        f"  .k{{fill:{KEY};font-weight:600}}",
        f"  .v{{fill:{VAL}}}",
        f"  .d{{fill:{DIM}}}",
        f"  .a{{fill:{ACCENT};font-weight:600}}",
    ]

    if STATIC:
        p.append("  .ln{opacity:1}")
    else:
        p += [
            "  .ln{opacity:0;animation:in var(--f) ease-out both;animation-delay:var(--t)}",
            "  @keyframes in{from{opacity:0;transform:translateX(-6px)}"
            "to{opacity:1;transform:translateX(0)}}",
        ]

    p += [
        "</style>",
        '<rect width="100%" height="100%" fill="none"/>',
    ]

    # title bar
    p.append(
        f'<text class="m a" x="{PAD}" y="{PAD + 12}" font-size="{FONT + 1}">'
        f"naman@github</text>"
    )
    p.append(
        f'<text class="m d" x="{PAD + 92}" y="{PAD + 12}" font-size="{FONT + 1}">'
        f"~ $ neofetch</text>"
    )
    p.append(
        f'<line x1="{PAD}" y1="{PAD + 20}" x2="{W - PAD}" y2="{PAD + 20}" '
        f'stroke="{RULE}" stroke-width="1"/>'
    )

    y0 = PAD + TITLE_H + 8

    for i, (key, val) in enumerate(LINES):
        if not key and not val:
            continue

        y = y0 + i * LINE_H
        delay = round(i * STAGGER, 3)
        style = "" if STATIC else f' style="--f:{FADE}s;--t:{delay}s"'

        p.append(f'<g class="ln"{style}>')
        if key:
            p.append(
                f'<text class="m k" x="{PAD}" y="{y:.1f}" font-size="{FONT}">'
                f"{escape(key)}</text>"
            )
        p.append(
            f'<text class="m v" x="{PAD + KEY_W}" y="{y:.1f}" font-size="{FONT}">'
            f"{escape(val)}</text>"
        )
        p.append("</g>")

    p.append("</svg>")
    return "\n".join(p)


if __name__ == "__main__":
    with open(OUT, "w") as f:
        f.write(build())
    print(f"wrote {OUT}{' (static)' if STATIC else ''}")
