#!/usr/bin/env python3
"""Downscale and palette-optimize static runtime avatars from lossless raw art.

Sprite sheets are intentionally excluded. The source artwork under each
asset's ``raw`` directory is never modified.

Requires Pillow:
    python -m pip install --user Pillow

Preview projected savings:
    python scripts/assets/optimize_static_avatars.py

Write optimized runtime PNGs:
    python scripts/assets/optimize_static_avatars.py --apply
"""

from __future__ import annotations

import argparse
import io
import os
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "frontend" / "public" / "cosmetics"


@dataclass(frozen=True)
class Target:
    source: Path
    destination: Path
    maximum_size: tuple[int, int]


def targets() -> list[Target]:
    items = [
        Target(
            source=portrait.parent / "raw" / portrait.name,
            destination=portrait,
            maximum_size=(256, 256),
        )
        for portrait in sorted((PUBLIC / "story-worlds").glob("*/monsters/*/portrait.png"))
    ]
    items.extend(
        [
            Target(
                PUBLIC / "companion" / "blue" / "raw" / "avatar.png",
                PUBLIC / "companion" / "blue" / "avatar.png",
                (256, 256),
            ),
            Target(
                PUBLIC / "companion" / "blue" / "raw" / "battle_portrait.png",
                PUBLIC / "companion" / "blue" / "battle_portrait.png",
                (384, 288),
            ),
            Target(
                PUBLIC / "companion" / "blue" / "raw" / "portrait.png",
                PUBLIC / "companion" / "blue" / "portrait.png",
                (576, 768),
            ),
            Target(
                PUBLIC / "companion" / "black" / "raw" / "portrait.png",
                PUBLIC / "companion" / "black" / "portrait.png",
                (576, 768),
            ),
            Target(
                PUBLIC / "companion" / "white" / "raw" / "white.png",
                PUBLIC / "companion" / "white" / "white.png",
                (576, 768),
            ),
        ]
    )
    return items


def optimized_png(source: Path, maximum_size: tuple[int, int]) -> tuple[bytes, tuple[int, int]]:
    with Image.open(source) as opened:
        image = opened.convert("RGBA")
        image.thumbnail(maximum_size, Image.Resampling.LANCZOS)
        image = image.quantize(
            colors=256,
            method=Image.Quantize.FASTOCTREE,
            dither=Image.Dither.FLOYDSTEINBERG,
        )
        output = io.BytesIO()
        image.save(output, format="PNG", optimize=True, compress_level=9)
        return output.getvalue(), image.size


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="replace runtime copies; raw source artwork remains untouched",
    )
    args = parser.parse_args()

    before_total = 0
    after_total = 0
    optimized = 0
    for target in targets():
        if not target.source.is_file() or not target.destination.is_file():
            parser.error(f"missing source or runtime asset: {target.destination}")

        original_size = target.destination.stat().st_size
        payload, dimensions = optimized_png(target.source, target.maximum_size)
        before_total += original_size
        after_total += len(payload)
        optimized += 1

        relative = target.destination.relative_to(ROOT)
        print(
            f"{relative}: {original_size:,} -> {len(payload):,} bytes "
            f"({dimensions[0]}x{dimensions[1]})"
        )
        if args.apply:
            temporary = target.destination.with_suffix(".optimized.tmp.png")
            temporary.write_bytes(payload)
            os.replace(temporary, target.destination)

    savings = before_total - after_total
    percentage = savings / before_total if before_total else 0
    action = "Optimized" if args.apply else "Would optimize"
    print(
        f"{action} {optimized} static assets: {before_total:,} -> "
        f"{after_total:,} bytes ({percentage:.1%} smaller)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
