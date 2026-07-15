#!/usr/bin/env python3
"""Stage and pad monster raw pose PNGs.

The script targets one monster at a time:

  frontend/public/cosmetics/story-worlds/<story-world>/monsters/<monster>/pose/raw

On the first run it moves current raw-root PNGs into _raw, then writes padded
copies back into the raw root:

  raw/_raw/idle.png  -> preserved original
  raw/idle.png       -> padded working source

Rerunning regenerates the raw root files from raw/_raw, so padding does not
compound. The output canvas grows by exactly the requested side padding.

Usage:
    python scripts/pad_monster_raw.py bone-lancer
    python scripts/pad_monster_raw.py two-headed-hound --all 300
    python scripts/pad_monster_raw.py bone-lancer --padding-size 192
    python scripts/pad_monster_raw.py bone-lancer --story-world arcane-spire --right 192 --dry-run

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
STORY_WORLDS_ROOT = REPO_ROOT / "frontend" / "public" / "story-worlds"
BACKUP_DIR_NAME = "_raw"


@dataclass(frozen=True)
class Pad:
    left: int
    top: int
    right: int
    bottom: int

    @property
    def size_delta(self) -> tuple[int, int]:
        return self.left + self.right, self.top + self.bottom


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


def monster_raw_dir(story_world: str, monster: str) -> Path:
    monsters_dir = STORY_WORLDS_ROOT / story_world / "monsters"
    candidates = [monsters_dir / folder / "pose" / "raw" for folder in monster_folder_candidates(monster)]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def require_non_negative(pad: Pad) -> None:
    if min(pad.left, pad.top, pad.right, pad.bottom) < 0:
        raise SystemExit("Padding values must be 0 or greater")


def root_pngs(raw_dir: Path) -> list[Path]:
    return sorted(path for path in raw_dir.glob("*.png") if path.is_file())


def stage_originals(raw_dir: Path, backup_dir: Path, dry_run: bool) -> list[Path]:
    backup_pngs = root_pngs(backup_dir) if backup_dir.exists() else []
    if backup_pngs:
        print(f"source   {repo_relative(backup_dir)} ({len(backup_pngs)} preserved PNGs)")
        return backup_pngs

    current_pngs = root_pngs(raw_dir)
    if not current_pngs:
        raise SystemExit(f"No PNGs found in {raw_dir}")

    print(f"stage    {repo_relative(raw_dir)}/*.png -> {repo_relative(backup_dir)}/")
    if dry_run:
        return current_pngs

    backup_dir.mkdir(parents=True, exist_ok=True)
    staged: list[Path] = []
    for png in current_pngs:
        destination = backup_dir / png.name
        shutil.move(str(png), destination)
        staged.append(destination)
    return staged


def canvas_fill(image: Image.Image):
    if image.mode == "RGBA":
        return (255, 255, 255, 0)
    if image.mode == "LA":
        return (255, 0)
    if image.mode == "L":
        return 255
    return (255, 255, 255)


def pad_image(
    source: Path,
    destination: Path,
    pad: Pad,
    dry_run: bool,
) -> tuple[tuple[int, int], tuple[int, int], Pad]:
    with Image.open(source) as image:
        extra_w, extra_h = pad.size_delta
        output_size = (image.width + extra_w, image.height + extra_h)

        if dry_run:
            return image.size, output_size, pad

        canvas = Image.new(image.mode, output_size, canvas_fill(image))
        canvas.paste(image, (pad.left, pad.top))
        destination.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(destination)
        return image.size, output_size, pad


def write_padded_images(
    raw_dir: Path,
    sources: list[Path],
    pad: Pad,
    dry_run: bool,
) -> None:
    for source in sources:
        destination = raw_dir / source.name
        original_size, output_size, effective_pad = pad_image(
            source,
            destination,
            pad,
            dry_run,
        )
        action = "would write" if dry_run else "wrote"
        print(
            f"{action:11} {repo_relative(destination)} "
            f"{original_size[0]}x{original_size[1]} -> {output_size[0]}x{output_size[1]} "
            f"pad=({effective_pad.left},{effective_pad.top},{effective_pad.right},{effective_pad.bottom})"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("monster", help="monster folder/species name, e.g. bone-lancer")
    parser.add_argument("--story-world", default="arcane-spire", help="story-world slug (default: arcane-spire)")
    parser.add_argument("--raw-dir", type=Path, help="override the resolved monster pose/raw directory")
    parser.add_argument(
        "--padding-size",
        type=int,
        default=192,
        help="right-side padding pixels when --all and --right are omitted (default: 192)",
    )
    parser.add_argument("--all", dest="all_sides", type=int, help="pixels to add on every side")
    parser.add_argument("--left", type=int, help="pixels to add on the left")
    parser.add_argument("--top", type=int, help="pixels to add on the top")
    parser.add_argument("--right", type=int, help="pixels to add on the right")
    parser.add_argument("--bottom", type=int, help="pixels to add on the bottom")
    parser.add_argument("--dry-run", action="store_true", help="report staging and output sizes without writing")
    args = parser.parse_args(argv)

    raw_dir = (args.raw_dir or monster_raw_dir(args.story_world, args.monster)).resolve()
    backup_dir = raw_dir / BACKUP_DIR_NAME
    base = args.all_sides
    left = args.left if args.left is not None else (base if base is not None else 0)
    top = args.top if args.top is not None else (base if base is not None else 0)
    right = args.right if args.right is not None else (base if base is not None else args.padding_size)
    bottom = args.bottom if args.bottom is not None else (base if base is not None else 0)
    pad = Pad(left, top, right, bottom)
    require_non_negative(pad)

    if not raw_dir.exists():
        raise SystemExit(f"Raw directory does not exist: {raw_dir}")

    print(f"monster  {args.monster}")
    print(f"raw dir  {repo_relative(raw_dir)}")
    print(f"padding  left={pad.left} top={pad.top} right={pad.right} bottom={pad.bottom}")
    sources = stage_originals(raw_dir, backup_dir, args.dry_run)
    write_padded_images(raw_dir, sources, pad, args.dry_run)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        raise SystemExit(130)
