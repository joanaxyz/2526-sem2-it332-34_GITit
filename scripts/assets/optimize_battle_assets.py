#!/usr/bin/env python3
"""Shrink the images a level downloads before its workspace opens.

The tier workspace stays behind its loading screen until every battle image
has decoded, so on a learner's first visit to a level the download size is the
level start time. Two kinds of image dominate it:

* Battle backgrounds are painted, full-colour art saved as PNG (about 2 MB
  each). The lossless master moves to ``backgrounds/battle/raw/`` and the
  runtime image becomes a WebP encoded from it (about 200 KB).
* Skill effect sheets are RGBA PNGs (0.5 to 0.9 MB each). They are palette
  optimized in place exactly like ``compact_actor_sheets.py`` does for actor
  sheets: same size, same grid, no crop, so frame registration is unchanged.

Raw sources, references, samples and diagnostics are never modified. Run it
again after regenerating effect sheets or adding a background.

Requires Pillow:
    python -m pip install --user Pillow

Preview projected savings:
    python scripts/assets/optimize_battle_assets.py

Write the optimized runtime images:
    python scripts/assets/optimize_battle_assets.py --apply
"""

from __future__ import annotations

import argparse
import io
import os
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "frontend" / "public" / "cosmetics"
BACKGROUND_QUALITY = 85
SKIPPED_DIRS = {"_raw", "raw", "references", "samples"}


def background_masters() -> list[Path]:
    """Lossless masters, moving any runtime PNG that has none yet into raw/."""
    masters = []
    for battle in sorted(PUBLIC.glob("story-worlds/*/backgrounds/battle")):
        names = {p.name for p in battle.glob("chapter-*.png")} | {p.name for p in battle.glob("raw/chapter-*.png")}
        masters.extend(battle / "raw" / name for name in sorted(names))
    return masters


def effect_sheets() -> list[Path]:
    patterns = ("companion/*/effects/*/*.png", "story-worlds/*/monsters/*/effects/*.png")
    sheets = [p for pattern in patterns for p in PUBLIC.glob(pattern)]
    return sorted(p for p in sheets if not p.name.startswith("_") and not SKIPPED_DIRS & set(p.parts))


def webp_background(source: Path) -> bytes:
    with Image.open(source) as opened:
        output = io.BytesIO()
        opened.convert("RGB").save(output, format="WEBP", quality=BACKGROUND_QUALITY, method=6)
        return output.getvalue()


def palette_sheet(source: Path) -> bytes | None:
    """The 256-colour encoding, or None when the sheet is already a palette PNG."""
    with Image.open(source) as opened:
        if opened.mode == "P":
            return None
        image = opened.convert("RGBA").quantize(
            colors=256,
            method=Image.Quantize.FASTOCTREE,
            dither=Image.Dither.FLOYDSTEINBERG,
        )
        output = io.BytesIO()
        image.save(output, format="PNG", optimize=True, compress_level=9)
        return output.getvalue()


def write_atomic(path: Path, payload: bytes) -> None:
    temporary = path.with_name(f".{path.name}.optimizing")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the optimized runtime images")
    args = parser.parse_args()

    before = after = 0
    for master in background_masters():
        runtime_png = master.parent.parent / master.name
        runtime_webp = runtime_png.with_suffix(".webp")
        payload = webp_background(master if master.exists() else runtime_png)
        current = runtime_png if runtime_png.exists() else runtime_webp
        old = current.stat().st_size if current.exists() else 0
        before += old
        after += len(payload)
        print(f"{master.relative_to(PUBLIC).as_posix()}: {old // 1024} KB -> {len(payload) // 1024} KB WebP")
        if args.apply:
            if not master.exists():
                master.parent.mkdir(exist_ok=True)
                os.replace(runtime_png, master)
            write_atomic(runtime_webp, payload)

    for sheet in effect_sheets():
        payload = palette_sheet(sheet)
        if payload is None:
            continue
        old = sheet.stat().st_size
        before += old
        after += len(payload)
        print(f"{sheet.relative_to(PUBLIC).as_posix()}: {old // 1024} KB -> {len(payload) // 1024} KB")
        if args.apply:
            write_atomic(sheet, payload)

    print(f"total: {before / 1048576:.1f} MB -> {after / 1048576:.1f} MB" + ("" if args.apply else " (dry run)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
