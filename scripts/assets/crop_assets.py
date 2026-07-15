#!/usr/bin/env python3
"""Crop source asset PNGs to their exact visible pixel bounds.

Defaults are intentionally scoped to the Vite app's source assets:

  input:  frontend/src/assets/raw/images
  output: frontend/src/assets/images

The script only processes PNG files under frontend/src/assets. It will not touch
frontend/public/cosmetics or any monster art.

Usage:
    python scripts/crop_assets.py
    python scripts/crop_assets.py --dry-run
    python scripts/crop_assets.py --padding 2

Requires: Pillow.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[2]
ASSETS_ROOT = REPO_ROOT / "frontend" / "src" / "assets"
DEFAULT_SOURCE_DIR = ASSETS_ROOT / "raw" / "images"
DEFAULT_OUTPUT_DIR = ASSETS_ROOT / "images"


@dataclass(frozen=True)
class CropResult:
    source: Path
    destination: Path
    original_size: tuple[int, int]
    output_size: tuple[int, int]
    bbox: tuple[int, int, int, int] | None
    copied: bool


def is_inside(path: Path, parent: Path) -> bool:
    path = path.resolve()
    parent = parent.resolve()
    return path == parent or path.is_relative_to(parent)


def require_assets_path(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not is_inside(resolved, ASSETS_ROOT):
        raise SystemExit(f"{label} must be inside {ASSETS_ROOT}: {resolved}")
    return resolved


def visible_bbox(image: Image.Image, alpha_threshold: int) -> tuple[int, int, int, int] | None:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A").point(lambda value: 255 if value > alpha_threshold else 0)
    return alpha.getbbox()


def padded_bbox(
    bbox: tuple[int, int, int, int],
    size: tuple[int, int],
    padding: int,
) -> tuple[int, int, int, int]:
    left, top, right, bottom = bbox
    width, height = size
    return (
        max(0, left - padding),
        max(0, top - padding),
        min(width, right + padding),
        min(height, bottom + padding),
    )


def crop_png(
    source: Path,
    destination: Path,
    alpha_threshold: int,
    padding: int,
    dry_run: bool,
) -> CropResult:
    with Image.open(source) as image:
        bbox = visible_bbox(image, alpha_threshold)
        original_size = image.size

        if bbox is None:
            output_size = image.size
            copied = True
            if not dry_run:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            return CropResult(source, destination, original_size, output_size, bbox, copied)

        crop_box = padded_bbox(bbox, image.size, padding)
        cropped = image.convert("RGBA").crop(crop_box)
        output_size = cropped.size
        copied = output_size == original_size and crop_box == (0, 0, original_size[0], original_size[1])

        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if copied:
                shutil.copy2(source, destination)
            else:
                cropped.save(destination, optimize=True)

    return CropResult(source, destination, original_size, output_size, bbox, copied)


def iter_pngs(source_dir: Path) -> list[Path]:
    return sorted(path for path in source_dir.rglob("*.png") if path.is_file())


def print_result(result: CropResult, source_root: Path) -> None:
    rel = result.source.relative_to(source_root)
    action = "copied" if result.copied else "cropped"
    bbox = "empty" if result.bbox is None else ",".join(str(value) for value in result.bbox)
    print(
        f"{action:7} {rel.as_posix()} "
        f"{result.original_size[0]}x{result.original_size[1]} -> "
        f"{result.output_size[0]}x{result.output_size[1]} bbox={bbox}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE_DIR, help="raw PNG directory")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT_DIR, help="cropped PNG output directory")
    parser.add_argument(
        "--alpha-threshold",
        type=int,
        default=0,
        help="alpha values at or below this are treated as transparent (default: 0)",
    )
    parser.add_argument("--padding", type=int, default=0, help="transparent pixels to keep around the crop")
    parser.add_argument("--dry-run", action="store_true", help="report crops without writing files")
    args = parser.parse_args(argv)

    source_dir = require_assets_path(args.source, "--source")
    output_dir = require_assets_path(args.out, "--out")

    if args.alpha_threshold < 0 or args.alpha_threshold > 254:
        raise SystemExit("--alpha-threshold must be between 0 and 254")
    if args.padding < 0:
        raise SystemExit("--padding must be 0 or greater")
    if not source_dir.exists():
        raise SystemExit(f"Raw asset directory does not exist: {source_dir}")
    if source_dir == output_dir or is_inside(output_dir, source_dir):
        raise SystemExit("--out must be separate from --source")

    pngs = iter_pngs(source_dir)
    if not pngs:
        print(f"No PNG files found in {source_dir}", file=sys.stderr)
        return 1

    for source in pngs:
        relative = source.relative_to(source_dir)
        destination = output_dir / relative
        result = crop_png(source, destination, args.alpha_threshold, args.padding, args.dry_run)
        print_result(result, source_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
