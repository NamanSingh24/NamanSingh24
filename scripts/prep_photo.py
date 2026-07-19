#!/usr/bin/env python3
"""
Prep a portrait photo for ASCII conversion.

  1. Strip the background with rembg so only the subject remains.
  2. Boost local contrast with CLAHE. A flatly-lit face otherwise
     converts to an unreadable dark blob.
  3. Composite onto pure white so the background maps to the blank
     end of the ASCII ramp (white -> spaces).

Run once per photo:
    python scripts/prep_photo.py source-photo.jpg
Writes source-prepped.png
"""

import sys
import io

import cv2
import numpy as np
from PIL import Image
from rembg import remove

OUT = "source-prepped.png"
MAX_DIM = 1400


def main(path: str) -> None:
    raw = Image.open(path)

    # HEIC support if the input came straight off an iPhone
    if raw.mode not in ("RGB", "RGBA"):
        raw = raw.convert("RGBA")

    raw.thumbnail((MAX_DIM, MAX_DIM), Image.LANCZOS)

    buf = io.BytesIO()
    raw.save(buf, format="PNG")

    # 1. background removal
    cut = Image.open(io.BytesIO(remove(buf.getvalue()))).convert("RGBA")

    # 3a. composite onto white before contrast work
    white = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    flat = Image.alpha_composite(white, cut).convert("L")

    # 2. CLAHE for local contrast
    arr = np.array(flat)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    arr = clahe.apply(arr)

    # 3b. push the near-white background all the way to white so it
    # resolves to the space glyph rather than a faint dot
    alpha = np.array(cut.getchannel("A"))
    arr[alpha < 24] = 255

    Image.fromarray(arr).save(OUT)
    print(f"wrote {OUT}  ({arr.shape[1]}x{arr.shape[0]})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python scripts/prep_photo.py <photo>")
    main(sys.argv[1])
