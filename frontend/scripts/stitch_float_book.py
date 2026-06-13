"""One-shot compositor: overlay book.png onto float.png frame grid.

Both sheets are 1280x1280, 5x5 grid of 256px frames, authored as a pair, so a
whole-sheet alpha composite lines the book up with the float pose in every
cell. Produces float_book.png next to the sources.

Usage: python frontend/scripts/stitch_float_book.py
"""
from pathlib import Path

from PIL import Image

BLUE = Path(__file__).resolve().parent.parent / "src" / "assets" / "sprites" / "character" / "blue"

base = Image.open(BLUE / "float.png").convert("RGBA")
book = Image.open(BLUE / "book.png").convert("RGBA")
if base.size != book.size:
    raise SystemExit(f"size mismatch: float {base.size} vs book {book.size}")

out = Image.alpha_composite(base, book)
out.save(BLUE / "float_book.png", optimize=True)
print(f"wrote {BLUE / 'float_book.png'} ({out.size[0]}x{out.size[1]})")
