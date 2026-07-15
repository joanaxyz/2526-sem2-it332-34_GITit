#!/usr/bin/env python3
"""Shift selected monster pose PNGs inside their current canvas.

This script is intentionally separate from padding. Run the padding script first
when you need a larger canvas, then use this script to nudge specific poses
left/right/up/down.

The first run for a pose copies the target PNG into that target folder's
_shift_raw staging folder and writes the shifted output back to the target.
Later runs reuse _shift_raw so the shift does not compound. Use
--refresh-source to replace _shift_raw from the current target file before
shifting.

Usage:
    python scripts/shift_monster_raw.py bone-lancer --poses idle --left 96
    python scripts/shift_monster_raw.py two-headed-hound --poses all --right 24
    python scripts/shift_monster_raw.py two-headed-hound --root --poses all --right 24
    python scripts/shift_monster_raw.py two-headed-hound --_raw --poses all --left 12
    python scripts/shift_monster_raw.py bone-lancer --poses idle --align-left
    python scripts/shift_monster_raw.py bone-lancer --poses idle attack --right 32 --dry-run

Requires: Pillow.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from PIL import Image
from PIL import ImageChops


REPO_ROOT = Path(__file__).resolve().parents[2]
STORY_WORLDS_ROOT = REPO_ROOT / "frontend" / "public" / "story-worlds"
SHIFT_SOURCE_DIR_NAME = "_shift_raw"


def repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(resolved)


def monster_folder_candidates(monster: str) -> list[str]:
    cleaned = monster.strip()
    normalized = cleaned.replace("-", "_")
    return [cleaned] if cleaned == normalized else [cleaned, normalized]


def monster_pose_dir(story_world: str, monster: str) -> Path:
    monsters_dir = STORY_WORLDS_ROOT / story_world / "monsters"
    candidates = [monsters_dir / folder / "pose" for folder in monster_folder_candidates(monster)]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def monster_raw_dir(story_world: str, monster: str) -> Path:
    return monster_pose_dir(story_world, monster) / "raw"


def monster_original_raw_dir(story_world: str, monster: str) -> Path:
    return monster_raw_dir(story_world, monster) / "_raw"


def monster_target_dir(story_world: str, monster: str, target: str) -> Path:
    if target == "root":
        return monster_pose_dir(story_world, monster)
    if target == "_raw":
        return monster_original_raw_dir(story_world, monster)
    return monster_raw_dir(story_world, monster)


def canvas_fill(image: Image.Image):
    if image.mode == "RGBA":
        return (255, 255, 255, 0)
    if image.mode == "LA":
        return (255, 0)
    if image.mode == "L":
        return 255
    return (255, 255, 255)


def visible_bbox(image: Image.Image, threshold: int) -> tuple[int, int, int, int] | None:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A").point(lambda value: 255 if value > 0 else 0)
    r, g, b = image.convert("RGB").split()
    min_channel = ImageChops.darker(ImageChops.darker(r, g), b)
    cutoff = 255 - threshold
    visible_color = min_channel.point(lambda value: 255 if value < cutoff else 0)
    return ImageChops.multiply(alpha, visible_color).getbbox()


def pose_filename(pose: str) -> str:
    return pose if pose.lower().endswith(".png") else f"{pose}.png"


def root_pngs(target_dir: Path) -> list[Path]:
    return sorted(path for path in target_dir.glob("*.png") if path.is_file())


def resolve_poses(target_dir: Path, poses: list[str] | None) -> list[str]:
    if poses and len(poses) == 1 and poses[0].lower() == "all":
        pngs = root_pngs(target_dir)
        if not pngs:
            raise SystemExit(f"No root pose PNGs found in {target_dir}")
        return [path.name for path in pngs]

    return poses or ["idle"]


def stage_shift_source(
    target_dir: Path,
    shift_source_dir: Path,
    pose: str,
    refresh_source: bool,
    dry_run: bool,
) -> Path:
    filename = pose_filename(pose)
    source = target_dir / filename
    staged = shift_source_dir / filename

    if not source.exists() and not staged.exists():
        raise SystemExit(f"Pose PNG does not exist: {source}")

    if refresh_source or not staged.exists():
        if not source.exists():
            raise SystemExit(f"Cannot refresh missing pose PNG: {source}")
        print(f"stage    {repo_relative(source)} -> {repo_relative(staged)}")
        if not dry_run:
            shift_source_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, staged)
        return source if dry_run else staged

    print(f"source   {repo_relative(staged)}")
    return staged


def paste_shifted(canvas: Image.Image, image: Image.Image, offset: tuple[int, int]) -> None:
    offset_x, offset_y = offset
    source_left = max(0, -offset_x)
    source_top = max(0, -offset_y)
    target_left = max(0, offset_x)
    target_top = max(0, offset_y)
    paste_w = min(image.width - source_left, canvas.width - target_left)
    paste_h = min(image.height - source_top, canvas.height - target_top)

    if paste_w <= 0 or paste_h <= 0:
        return

    crop = image.crop((source_left, source_top, source_left + paste_w, source_top + paste_h))
    canvas.paste(crop, (target_left, target_top))


def resolved_offset(
    image: Image.Image,
    base_offset: tuple[int, int],
    align_left: bool,
    align_right: bool,
    align_top: bool,
    align_bottom: bool,
    threshold: int,
) -> tuple[int, int]:
    offset_x, offset_y = base_offset
    if not (align_left or align_right or align_top or align_bottom):
        return base_offset

    bbox = visible_bbox(image, threshold)
    if bbox is None:
        raise SystemExit("Cannot align image with no visible pixels")

    left, top, right, bottom = bbox
    if align_left:
        offset_x -= left
    if align_right:
        offset_x += image.width - right
    if align_top:
        offset_y -= top
    if align_bottom:
        offset_y += image.height - bottom
    return offset_x, offset_y


def shift_png(
    source: Path,
    destination: Path,
    base_offset: tuple[int, int],
    align_left: bool,
    align_right: bool,
    align_top: bool,
    align_bottom: bool,
    threshold: int,
    dry_run: bool,
) -> tuple[tuple[int, int], tuple[int, int]]:
    with Image.open(source) as image:
        offset = resolved_offset(
            image,
            base_offset,
            align_left,
            align_right,
            align_top,
            align_bottom,
            threshold,
        )
        if dry_run:
            return image.size, offset

        canvas = Image.new(image.mode, image.size, canvas_fill(image))
        paste_shifted(canvas, image, offset)
        canvas.save(destination)
        return image.size, offset


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("monster", help="monster folder/species name, e.g. bone-lancer")
    parser.add_argument("--story-world", "--theme", dest="story_world", default="arcane-spire", help="story world slug (default: arcane-spire)")
    target_group = parser.add_mutually_exclusive_group()
    target_group.add_argument("--root", dest="target", action="store_const", const="root", help="shift pose/*.png")
    target_group.add_argument("--raw", dest="target", action="store_const", const="raw", help="shift pose/raw/*.png (default)")
    target_group.add_argument("--_raw", dest="target", action="store_const", const="_raw", help="shift pose/raw/_raw/*.png")
    parser.set_defaults(target="raw")
    parser.add_argument("--raw-dir", type=Path, help="override the resolved target directory (legacy name)")
    parser.add_argument("--poses", nargs="+", help="pose names to shift (default: idle); use 'all' for every root PNG")
    parser.add_argument("--left", type=int, default=0, help="pixels to shift left (default: 0)")
    parser.add_argument("--right", type=int, default=0, help="pixels to shift right (default: 0)")
    parser.add_argument("--up", type=int, default=0, help="pixels to shift up (default: 0)")
    parser.add_argument("--down", type=int, default=0, help="pixels to shift down (default: 0)")
    parser.add_argument("--align-left", action="store_true", help="shift visible pixels flush to the left edge")
    parser.add_argument("--align-right", action="store_true", help="shift visible pixels flush to the right edge")
    parser.add_argument("--align-top", action="store_true", help="shift visible pixels flush to the top edge")
    parser.add_argument("--align-bottom", action="store_true", help="shift visible pixels flush to the bottom edge")
    parser.add_argument("--threshold", type=int, default=24, help="channel drop below white that counts as visible (default: 24)")
    parser.add_argument("--refresh-source", action="store_true", help="refresh _shift_raw from the current target file")
    parser.add_argument("--dry-run", action="store_true", help="report shifted files without writing")
    args = parser.parse_args(argv)

    if min(args.left, args.right, args.up, args.down) < 0:
        raise SystemExit("Shift values must be 0 or greater")
    if args.align_left and args.align_right:
        raise SystemExit("Choose only one of --align-left or --align-right")
    if args.align_top and args.align_bottom:
        raise SystemExit("Choose only one of --align-top or --align-bottom")
    if args.threshold < 0 or args.threshold > 254:
        raise SystemExit("--threshold must be between 0 and 254")

    offset = (args.right - args.left, args.down - args.up)
    target_dir = (args.raw_dir or monster_target_dir(args.story_world, args.monster, args.target)).resolve()
    shift_source_dir = target_dir / SHIFT_SOURCE_DIR_NAME

    if not target_dir.exists():
        raise SystemExit(f"Target directory does not exist: {target_dir}")

    print(f"monster  {args.monster}")
    print(f"target   {args.target}")
    print(f"dir      {repo_relative(target_dir)}")
    print(f"shift    x={offset[0]} y={offset[1]}")

    poses = resolve_poses(target_dir, args.poses)
    print(f"poses    {', '.join(poses)}")

    for pose in poses:
        filename = pose_filename(pose)
        source = stage_shift_source(target_dir, shift_source_dir, pose, args.refresh_source, args.dry_run)
        destination = target_dir / filename
        size, resolved = shift_png(
            source,
            destination,
            offset,
            args.align_left,
            args.align_right,
            args.align_top,
            args.align_bottom,
            args.threshold,
            args.dry_run,
        )
        action = "would write" if args.dry_run else "wrote"
        print(f"{action:11} {repo_relative(destination)} {size[0]}x{size[1]} offset=({resolved[0]},{resolved[1]})")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        raise SystemExit(130)
