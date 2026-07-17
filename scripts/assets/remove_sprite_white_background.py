#!/usr/bin/env python3
"""Remove leftover white backgrounds from companion and monster PNG sprites.

The script follows the raw-to-root asset workflow:

  source: <sprite-dir>/raw/<name>.png
  output: <sprite-dir>/<name>.png

When a sprite directory does not have a raw copy yet, the current root PNG is
copied into a new raw/ folder before the cleaned PNG is written back to the
root. This keeps the uncleaned original available for later reprocessing.

Static companion portraits are intentionally skipped. Pass --include-portraits
to opt them into an explicit cleanup run.

By default, only near-white pixels connected to the outside transparent/white
background are removed. Enclosed-white removal, enclosed-hole fringe cleanup,
and white-matte edge decontamination are intentionally opt-in: pale character
details can be indistinguishable from a white matte without per-sprite visual
review. Use --min-hole-size, --hole-fringe-radius, or --edge-defringe only for a
reviewed asset set.

Usage:
    python scripts/remove_sprite_white_background.py --dry-run
    python scripts/remove_sprite_white_background.py
    python scripts/remove_sprite_white_background.py --scope companion
    python scripts/remove_sprite_white_background.py --scope companion --include-portraits
    python scripts/remove_sprite_white_background.py frontend/public/cosmetics/companion/blue
    python scripts/remove_sprite_white_background.py path/to/sprite/raw/idle.png

Requires: Pillow.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[2]
COSMETICS_ROOT = REPO_ROOT / "frontend" / "public" / "cosmetics"
COMPANION_ROOT = COSMETICS_ROOT / "companion"
STORY_WORLDS_ROOT = COSMETICS_ROOT / "story-worlds"
RAW_DIR_NAME = "raw"
POSE_DIR_NAME = "pose"
PORTRAIT_FILE_NAMES = frozenset({"avatar.png", "battle_portrait.png", "portrait.png"})


@dataclass(frozen=True)
class SpriteTask:
    source: Path
    destination: Path
    raw_path: Path | None
    stage_action: str | None


@dataclass(frozen=True)
class CleanResult:
    source: Path
    destination: Path
    size: tuple[int, int]
    removed_pixels: int
    recolored_pixels: int
    stage_action: str | None
    raw_path: Path | None
    wrote: bool


def image_data(image: Image.Image):
    """Return a stable pixel iterator across Pillow versions."""
    if hasattr(image, "get_flattened_data"):
        return image.get_flattened_data()
    return image.getdata()


def is_near_white(r: int, g: int, b: int, tolerance: int) -> bool:
    cutoff = 255 - tolerance
    return r >= cutoff and g >= cutoff and b >= cutoff


def is_background_like_fringe(
    r: int,
    g: int,
    b: int,
    min_rgb: int,
    min_luma: int,
    max_chroma: int,
) -> bool:
    darkest = min(r, g, b)
    lightness = (r + g + b) / 3
    chroma = max(r, g, b) - darkest
    return darkest >= min_rgb and lightness >= min_luma and chroma <= max_chroma


def connected_white_mask(
    rgba: Image.Image,
    tolerance: int,
    alpha_threshold: int,
    min_hole_size: int,
) -> bytearray:
    """Return 1 for near-white pixels connected to the image background.

    Also sweeps near-white "holes" that are fully enclosed by opaque
    artwork (e.g. the gap inside a bow string, a chain loop, or a cloak
    fold) once such a hole reaches ``min_hole_size`` pixels. Those pockets
    are background bleed-through, not intentional interior highlights, and
    the border flood fill alone can never reach them since they never
    touch the image edge.
    """
    width, height = rgba.size
    total = width * height
    traversable = bytearray(total)
    removable = bytearray(total)

    for index, (r, g, b, a) in enumerate(image_data(rgba)):
        if a <= alpha_threshold:
            traversable[index] = 1
        elif is_near_white(r, g, b, tolerance):
            traversable[index] = 1
            removable[index] = 1

    queue: deque[int] = deque()
    seen = bytearray(total)

    def seed(index: int) -> None:
        if traversable[index] and not seen[index]:
            seen[index] = 1
            queue.append(index)

    last_row = (height - 1) * width
    for x in range(width):
        seed(x)
        seed(last_row + x)
    for y in range(height):
        row = y * width
        seed(row)
        seed(row + width - 1)

    while queue:
        index = queue.popleft()
        x = index % width

        if x > 0:
            neighbor = index - 1
            if traversable[neighbor] and not seen[neighbor]:
                seen[neighbor] = 1
                queue.append(neighbor)
        if x < width - 1:
            neighbor = index + 1
            if traversable[neighbor] and not seen[neighbor]:
                seen[neighbor] = 1
                queue.append(neighbor)
        if index >= width:
            neighbor = index - width
            if traversable[neighbor] and not seen[neighbor]:
                seen[neighbor] = 1
                queue.append(neighbor)
        if index < total - width:
            neighbor = index + width
            if traversable[neighbor] and not seen[neighbor]:
                seen[neighbor] = 1
                queue.append(neighbor)

    mask = bytearray(1 if seen[index] and removable[index] else 0 for index in range(total))

    if min_hole_size > 0:
        _remove_enclosed_holes(mask, removable, seen, width, height, min_hole_size)

    return mask


def transparent_hole_fringe_mask(
    rgba: Image.Image,
    alpha_threshold: int,
    radius: int,
    min_hole_size: int,
    min_rgb: int,
    min_luma: int,
    max_chroma: int,
    grid_columns: int,
    grid_rows: int,
) -> bytearray:
    """Return 1 for pale fringe pixels touching enclosed transparent holes.

    Near-white blob removal catches fully opaque leftover background, but AI
    sprites often leave antialiased gray-white residue around punched-out holes
    that are already transparent. This pass starts from transparent regions
    that do not reach the sheet edge, then removes only adjacent pale,
    low-saturation opaque pixels. It avoids using the silhouette's outside edge
    as a seed, so ordinary light contour highlights are preserved.
    """
    if radius <= 0 or min_hole_size <= 0:
        return bytearray(rgba.width * rgba.height)

    width, height = rgba.size
    if (
        grid_columns > 1
        and grid_rows > 1
        and width % grid_columns == 0
        and height % grid_rows == 0
    ):
        frame_width = width // grid_columns
        frame_height = height // grid_rows
        full_mask = bytearray(width * height)
        for row in range(grid_rows):
            for column in range(grid_columns):
                left = column * frame_width
                top = row * frame_height
                frame_mask = _transparent_hole_fringe_mask_for_image(
                    rgba.crop((left, top, left + frame_width, top + frame_height)),
                    alpha_threshold=alpha_threshold,
                    radius=radius,
                    min_hole_size=min_hole_size,
                    min_rgb=min_rgb,
                    min_luma=min_luma,
                    max_chroma=max_chroma,
                )
                for y in range(frame_height):
                    source_row = y * frame_width
                    target_row = (top + y) * width + left
                    full_mask[target_row : target_row + frame_width] = frame_mask[
                        source_row : source_row + frame_width
                    ]
        return full_mask

    return _transparent_hole_fringe_mask_for_image(
        rgba,
        alpha_threshold=alpha_threshold,
        radius=radius,
        min_hole_size=min_hole_size,
        min_rgb=min_rgb,
        min_luma=min_luma,
        max_chroma=max_chroma,
    )


def _transparent_hole_fringe_mask_for_image(
    rgba: Image.Image,
    alpha_threshold: int,
    radius: int,
    min_hole_size: int,
    min_rgb: int,
    min_luma: int,
    max_chroma: int,
) -> bytearray:
    width, height = rgba.size
    total = width * height
    pixels = list(image_data(rgba))
    transparent = bytearray(1 if a <= alpha_threshold else 0 for _, _, _, a in pixels)
    exterior = bytearray(total)
    queue: deque[int] = deque()

    def seed(index: int) -> None:
        if transparent[index] and not exterior[index]:
            exterior[index] = 1
            queue.append(index)

    last_row = (height - 1) * width
    for x in range(width):
        seed(x)
        seed(last_row + x)
    for y in range(height):
        row = y * width
        seed(row)
        seed(row + width - 1)

    while queue:
        index = queue.popleft()
        x = index % width

        if x > 0:
            neighbor = index - 1
            if transparent[neighbor] and not exterior[neighbor]:
                exterior[neighbor] = 1
                queue.append(neighbor)
        if x < width - 1:
            neighbor = index + 1
            if transparent[neighbor] and not exterior[neighbor]:
                exterior[neighbor] = 1
                queue.append(neighbor)
        if index >= width:
            neighbor = index - width
            if transparent[neighbor] and not exterior[neighbor]:
                exterior[neighbor] = 1
                queue.append(neighbor)
        if index < total - width:
            neighbor = index + width
            if transparent[neighbor] and not exterior[neighbor]:
                exterior[neighbor] = 1
                queue.append(neighbor)

    labeled = bytearray(total)
    mask = bytearray(total)

    for start in range(total):
        if not transparent[start] or exterior[start] or labeled[start]:
            continue

        component = [start]
        labeled[start] = 1
        queue = deque([start])
        while queue:
            index = queue.popleft()
            x = index % width

            if x > 0:
                neighbor = index - 1
                if transparent[neighbor] and not exterior[neighbor] and not labeled[neighbor]:
                    labeled[neighbor] = 1
                    component.append(neighbor)
                    queue.append(neighbor)
            if x < width - 1:
                neighbor = index + 1
                if transparent[neighbor] and not exterior[neighbor] and not labeled[neighbor]:
                    labeled[neighbor] = 1
                    component.append(neighbor)
                    queue.append(neighbor)
            if index >= width:
                neighbor = index - width
                if transparent[neighbor] and not exterior[neighbor] and not labeled[neighbor]:
                    labeled[neighbor] = 1
                    component.append(neighbor)
                    queue.append(neighbor)
            if index < total - width:
                neighbor = index + width
                if transparent[neighbor] and not exterior[neighbor] and not labeled[neighbor]:
                    labeled[neighbor] = 1
                    component.append(neighbor)
                    queue.append(neighbor)

        if len(component) < min_hole_size:
            continue

        for index in component:
            x = index % width
            y = index // width
            min_x = max(0, x - radius)
            max_x = min(width - 1, x + radius)
            min_y = max(0, y - radius)
            max_y = min(height - 1, y + radius)

            for neighbor_y in range(min_y, max_y + 1):
                row = neighbor_y * width
                for neighbor_x in range(min_x, max_x + 1):
                    neighbor = row + neighbor_x
                    if mask[neighbor]:
                        continue
                    r, g, b, a = pixels[neighbor]
                    if a <= alpha_threshold:
                        continue
                    if is_background_like_fringe(r, g, b, min_rgb, min_luma, max_chroma):
                        mask[neighbor] = 1

    return mask


def _remove_enclosed_holes(
    mask: bytearray,
    removable: bytearray,
    seen: bytearray,
    width: int,
    height: int,
    min_hole_size: int,
) -> None:
    """Flag enclosed near-white blobs (not reachable from the border) for removal.

    Small blobs are left alone since they are more likely to be genuine
    pinpoint highlights (eye glints, metal shine) than leftover background.
    """
    total = width * height
    labeled = bytearray(total)

    for start in range(total):
        if not removable[start] or seen[start] or labeled[start]:
            continue

        blob = [start]
        labeled[start] = 1
        queue = deque([start])
        while queue:
            index = queue.popleft()
            x = index % width

            neighbors = []
            if x > 0:
                neighbors.append(index - 1)
            if x < width - 1:
                neighbors.append(index + 1)
            if index >= width:
                neighbors.append(index - width)
            if index < total - width:
                neighbors.append(index + width)

            for neighbor in neighbors:
                if removable[neighbor] and not seen[neighbor] and not labeled[neighbor]:
                    labeled[neighbor] = 1
                    blob.append(neighbor)
                    queue.append(neighbor)

        if len(blob) >= min_hole_size:
            for index in blob:
                mask[index] = 1


def all_white_mask(rgba: Image.Image, tolerance: int, alpha_threshold: int) -> bytearray:
    return bytearray(
        1 if a > alpha_threshold and is_near_white(r, g, b, tolerance) else 0
        for r, g, b, a in image_data(rgba)
    )


def _dilate_mask(mask: "np.ndarray", radius: int) -> "np.ndarray":
    """Grow a boolean mask outward by ``radius`` 4-connected steps."""
    grown = mask
    for _ in range(radius):
        step = grown.copy()
        step[1:, :] |= grown[:-1, :]
        step[:-1, :] |= grown[1:, :]
        step[:, 1:] |= grown[:, :-1]
        step[:, :-1] |= grown[:, 1:]
        grown = step
    return grown


def decontaminate_white_edges(
    image: Image.Image,
    alpha_threshold: int,
    radius: int,
) -> tuple[Image.Image, int]:
    """Remove the white matte from the antialiased silhouette edge.

    Sprites generated on a white background keep a faint white-tinted halo on
    the partly-transparent ring where the artwork met the background. Deleting
    that ring would leave a hard, aliased edge; instead we un-premultiply the
    white contribution out of every partly-transparent edge pixel
    (``F = (C - (1 - a) * 255) / a``), which restores the artwork's true edge
    colour so it composites cleanly over any background.

    Only pixels within ``radius`` of the transparent background are touched, so
    interior soft glows and flames that sit on top of the artwork (not over the
    old white background) are preserved. Fully opaque pixels are a mathematical
    no-op, so hard-keyed sprites with no antialiasing (e.g. the white companion)
    are left untouched.
    """
    if radius <= 0:
        return image, 0

    arr = np.asarray(image, dtype=np.float32)
    if arr.ndim != 3 or arr.shape[-1] != 4:
        return image, 0

    rgb = arr[..., :3]
    alpha = arr[..., 3]
    transparent = alpha <= alpha_threshold
    if not transparent.any():
        return image, 0

    band = _dilate_mask(transparent.copy(), radius) & ~transparent
    target = band & (alpha > 0) & (alpha < 255)
    if not target.any():
        return image, 0

    coverage = (alpha / 255.0)[..., None]
    corrected = np.clip(
        (rgb - (1.0 - coverage) * 255.0) / np.clip(coverage, 1e-3, 1.0),
        0.0,
        255.0,
    )
    new_rgb = np.where(target[..., None], corrected, rgb)
    recolored = int((np.abs(new_rgb - rgb).sum(axis=-1) >= 1.0).sum())
    if not recolored:
        return image, 0

    result = arr.copy()
    result[..., :3] = new_rgb
    output = Image.fromarray(np.rint(result).clip(0, 255).astype(np.uint8), "RGBA")
    return output, recolored


def apply_transparency(rgba: Image.Image, remove_mask: bytearray) -> tuple[Image.Image, int]:
    removed = sum(remove_mask)
    if not removed:
        return rgba, 0

    pixels = list(image_data(rgba))
    pixels = [
        (r, g, b, 0) if remove_mask[index] else (r, g, b, a)
        for index, (r, g, b, a) in enumerate(pixels)
    ]
    output = Image.new("RGBA", rgba.size)
    output.putdata(pixels)
    return output, removed


def clean_png(
    task: SpriteTask,
    tolerance: int,
    alpha_threshold: int,
    mode: str,
    min_hole_size: int,
    hole_fringe_radius: int,
    min_transparent_hole_size: int,
    hole_fringe_min_rgb: int,
    hole_fringe_min_luma: int,
    hole_fringe_max_chroma: int,
    grid_columns: int,
    grid_rows: int,
    edge_defringe: bool,
    edge_defringe_radius: int,
    dry_run: bool,
) -> CleanResult:
    with Image.open(task.source) as image:
        rgba = image.convert("RGBA")
        if mode == "all":
            remove_mask = all_white_mask(rgba, tolerance, alpha_threshold)
        else:
            remove_mask = connected_white_mask(rgba, tolerance, alpha_threshold, min_hole_size)
            fringe_mask = transparent_hole_fringe_mask(
                rgba,
                alpha_threshold=alpha_threshold,
                radius=hole_fringe_radius,
                min_hole_size=min_transparent_hole_size,
                min_rgb=hole_fringe_min_rgb,
                min_luma=hole_fringe_min_luma,
                max_chroma=hole_fringe_max_chroma,
                grid_columns=grid_columns,
                grid_rows=grid_rows,
            )
            if any(fringe_mask):
                remove_mask = bytearray(
                    1 if remove_mask[index] or fringe_mask[index] else 0
                    for index in range(len(remove_mask))
                )

        output, removed = apply_transparency(rgba, remove_mask)

        recolored = 0
        if edge_defringe:
            output, recolored = decontaminate_white_edges(
                output, alpha_threshold, edge_defringe_radius
            )

    wrote = False
    if not dry_run:
        task.destination.parent.mkdir(parents=True, exist_ok=True)
        if removed or recolored:
            output.save(task.destination, optimize=True)
            wrote = True
        elif task.source.resolve() != task.destination.resolve():
            shutil.copy2(task.source, task.destination)
            wrote = True

    return CleanResult(
        source=task.source,
        destination=task.destination,
        size=output.size,
        removed_pixels=removed,
        recolored_pixels=recolored,
        stage_action=task.stage_action,
        raw_path=task.raw_path,
        wrote=wrote,
    )


def is_companion_portrait(path: Path) -> bool:
    """Return whether path is one of the companion's static portrait assets."""
    try:
        relative_path = path.resolve().relative_to(COMPANION_ROOT.resolve())
    except ValueError:
        return False

    if len(relative_path.parts) < 2:
        return False

    companion_slug = relative_path.parts[0].lower()
    file_name = path.name.lower()
    return file_name in PORTRAIT_FILE_NAMES or file_name == f"{companion_slug}.png"


def direct_pngs(directory: Path, include_portraits: bool = False) -> list[Path]:
    return sorted(
        path
        for path in directory.glob("*.png")
        if path.is_file() and (include_portraits or not is_companion_portrait(path))
    )


def task_for_root_png(path: Path, raw_action: str, dry_run: bool) -> SpriteTask:
    raw_path = path.parent / RAW_DIR_NAME / path.name
    if raw_path.exists():
        return SpriteTask(source=raw_path, destination=path, raw_path=raw_path, stage_action=None)

    if raw_action == "none":
        return SpriteTask(source=path, destination=path, raw_path=None, stage_action=None)

    if not dry_run:
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        if raw_action == "move":
            shutil.move(str(path), str(raw_path))
        else:
            shutil.copy2(path, raw_path)
        source = raw_path
    else:
        source = path

    return SpriteTask(source=source, destination=path, raw_path=raw_path, stage_action=raw_action)


def tasks_for_directory(
    directory: Path,
    raw_action: str,
    dry_run: bool,
    include_portraits: bool = False,
) -> list[SpriteTask]:
    raw_dir = directory / RAW_DIR_NAME
    raw_pngs = direct_pngs(raw_dir, include_portraits) if raw_dir.exists() else []
    tasks = [
        SpriteTask(source=path, destination=directory / path.name, raw_path=path, stage_action=None)
        for path in raw_pngs
    ]
    raw_names = {path.name for path in raw_pngs}

    tasks.extend(
        task_for_root_png(path, raw_action, dry_run)
        for path in direct_pngs(directory, include_portraits)
        if path.name not in raw_names
    )
    if tasks:
        return tasks

    return [
        task_for_root_png(path, raw_action, dry_run)
        for path in direct_pngs(directory, include_portraits)
    ]


def tasks_for_raw_directory(directory: Path, include_portraits: bool = False) -> list[SpriteTask]:
    if directory.name != RAW_DIR_NAME:
        return []
    destination_dir = directory.parent
    return [
        SpriteTask(source=path, destination=destination_dir / path.name, raw_path=path, stage_action=None)
        for path in direct_pngs(directory, include_portraits)
    ]


def tasks_for_path(
    path: Path,
    raw_action: str,
    dry_run: bool,
    include_portraits: bool = False,
) -> list[SpriteTask]:
    resolved = path.resolve()
    if not resolved.exists():
        raise SystemExit(f"Path does not exist: {path}")
    if resolved.is_dir():
        if resolved.name == RAW_DIR_NAME:
            return tasks_for_raw_directory(resolved, include_portraits)
        return tasks_for_directory(resolved, raw_action, dry_run, include_portraits)
    if resolved.suffix.lower() != ".png":
        return []
    if is_companion_portrait(resolved) and not include_portraits:
        return []
    if resolved.parent.name == RAW_DIR_NAME:
        return [
            SpriteTask(
                source=resolved,
                destination=resolved.parent.parent / resolved.name,
                raw_path=resolved,
                stage_action=None,
            )
        ]
    return [task_for_root_png(resolved, raw_action, dry_run)]


def has_png_work(directory: Path, include_portraits: bool = False) -> bool:
    return bool(
        direct_pngs(directory, include_portraits)
        or direct_pngs(directory / RAW_DIR_NAME, include_portraits)
    )


def default_sprite_dirs(
    scope: str,
    include_nested: bool,
    include_pose: bool,
    include_portraits: bool = False,
) -> list[Path]:
    directories: list[Path] = []

    if scope in {"all", "companion"} and COMPANION_ROOT.exists():
        directories.extend(
            path
            for path in sorted(COMPANION_ROOT.iterdir())
            if path.is_dir() and has_png_work(path, include_portraits)
        )

    if scope in {"all", "monsters"} and STORY_WORLDS_ROOT.exists():
        for monsters_root in sorted(STORY_WORLDS_ROOT.glob("*/monsters")):
            for monster_dir in sorted(path for path in monsters_root.iterdir() if path.is_dir()):
                if has_png_work(monster_dir, include_portraits):
                    directories.append(monster_dir)
                pose_dir = monster_dir / POSE_DIR_NAME
                if include_pose and pose_dir.is_dir() and has_png_work(pose_dir, include_portraits):
                    directories.append(pose_dir)

    if include_nested:
        extra_roots: list[Path] = []
        if scope in {"all", "companion"} and COMPANION_ROOT.exists():
            extra_roots.append(COMPANION_ROOT)
        if scope in {"all", "monsters"} and STORY_WORLDS_ROOT.exists():
            extra_roots.extend(sorted(STORY_WORLDS_ROOT.glob("*/monsters")))

        seen = {path.resolve() for path in directories}
        skip_names = {RAW_DIR_NAME, "_raw", "samples"}
        if not include_pose:
            skip_names.add(POSE_DIR_NAME)

        for root in extra_roots:
            for directory in sorted(path for path in root.rglob("*") if path.is_dir()):
                if directory.name in skip_names:
                    continue
                if any(part in skip_names for part in directory.parts):
                    continue
                if has_png_work(directory, include_portraits) and directory.resolve() not in seen:
                    directories.append(directory)
                    seen.add(directory.resolve())

    return directories


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def print_result(result: CleanResult, dry_run: bool) -> None:
    action = "would clean" if dry_run else "cleaned"
    if result.removed_pixels == 0 and result.recolored_pixels == 0:
        action = "would copy " if dry_run and result.source != result.destination else "unchanged"
    if result.stage_action:
        raw = relative(result.raw_path) if result.raw_path else "raw"
        stage = f" stage={result.stage_action}:{raw}"
    else:
        stage = ""

    print(
        f"{action:11} {relative(result.source)} -> {relative(result.destination)} "
        f"{result.size[0]}x{result.size[1]} removed={result.removed_pixels} "
        f"defringed={result.recolored_pixels}{stage}"
    )


def dedupe_tasks(tasks: list[SpriteTask]) -> list[SpriteTask]:
    seen: set[tuple[Path, Path]] = set()
    unique: list[SpriteTask] = []
    for task in tasks:
        key = (task.source.resolve(), task.destination.resolve())
        if key in seen:
            continue
        seen.add(key)
        unique.append(task)
    return unique


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="sprite files or directories; defaults to companion and monster sprite dirs",
    )
    parser.add_argument(
        "--scope",
        choices=("all", "companion", "monsters"),
        default="all",
        help="default asset scope when no paths are passed (default: all)",
    )
    parser.add_argument(
        "--include-nested",
        action="store_true",
        help="also process nested sprite dirs such as monster projectiles/effects",
    )
    parser.add_argument(
        "--include-pose",
        action="store_true",
        help="include monster pose stills during default discovery (default: skipped)",
    )
    parser.add_argument(
        "--include-portraits",
        action="store_true",
        help="include static companion portraits (default: skipped)",
    )
    parser.add_argument(
        "--raw-action",
        choices=("copy", "move", "none"),
        default="copy",
        help="how to stage root PNGs into raw/ when raw/ does not exist (default: copy)",
    )
    parser.add_argument(
        "--tolerance",
        type=int,
        default=18,
        help="maximum channel distance from pure white to remove (default: 18)",
    )
    parser.add_argument(
        "--alpha-threshold",
        type=int,
        default=0,
        help="alpha values at or below this are treated as transparent background (default: 0)",
    )
    parser.add_argument(
        "--mode",
        choices=("connected", "all"),
        default="connected",
        help="remove only background-connected whites, or all whites (default: connected)",
    )
    parser.add_argument(
        "--min-hole-size",
        type=int,
        default=0,
        help=(
            "enclosed near-white blobs (not touching the image border, e.g. inside a "
            "bow, chain loop, cloak fold, or a punched-out gap in wing membrane) at or "
            "above this pixel count are treated as leftover background and removed too; "
            "smaller blobs are kept as likely pinpoint highlights. Raise this if a future "
            "asset pack has genuine tiny white highlights worth preserving. Only applies "
            "in --mode connected. Use 0 to disable entirely (default: 0)"
        ),
    )
    parser.add_argument(
        "--hole-fringe-radius",
        type=int,
        default=0,
        help=(
            "remove pale low-saturation pixels within this many pixels of enclosed "
            "transparent holes, useful for antialiased white residue in wing "
            "perforations; use 0 to disable (default: 0)"
        ),
    )
    parser.add_argument(
        "--min-transparent-hole-size",
        type=int,
        default=4,
        help="minimum enclosed transparent component size before fringe cleanup applies (default: 4)",
    )
    parser.add_argument(
        "--hole-fringe-min-rgb",
        type=int,
        default=205,
        help="minimum RGB channel value for fringe cleanup candidates (default: 205)",
    )
    parser.add_argument(
        "--hole-fringe-min-luma",
        type=int,
        default=225,
        help="minimum average RGB value for fringe cleanup candidates (default: 225)",
    )
    parser.add_argument(
        "--hole-fringe-max-chroma",
        type=int,
        default=30,
        help="maximum RGB channel spread for fringe cleanup candidates (default: 30)",
    )
    parser.add_argument(
        "--grid-columns",
        type=int,
        default=5,
        help="sprite grid columns for frame-local hole detection; whole image fallback when not divisible (default: 5)",
    )
    parser.add_argument(
        "--grid-rows",
        type=int,
        default=5,
        help="sprite grid rows for frame-local hole detection; whole image fallback when not divisible (default: 5)",
    )
    edge_defringe_group = parser.add_mutually_exclusive_group()
    edge_defringe_group.add_argument(
        "--edge-defringe",
        dest="edge_defringe",
        action="store_true",
        help=(
            "enable the white-matte edge decontamination pass that removes the "
            "antialiased white halo ringing each silhouette (default: disabled)"
        ),
    )
    edge_defringe_group.add_argument(
        "--no-edge-defringe",
        dest="edge_defringe",
        action="store_false",
        help="explicitly keep white-matte edge decontamination disabled",
    )
    parser.set_defaults(edge_defringe=False)
    parser.add_argument(
        "--edge-defringe-radius",
        type=int,
        default=1,
        help=(
            "how many pixels inward from the transparent background to un-premultiply "
            "the white matte; 1 targets just the antialiased edge ring (default: 1)"
        ),
    )
    parser.add_argument("--dry-run", action="store_true", help="report work without writing files")
    args = parser.parse_args(argv)

    if args.tolerance < 0 or args.tolerance > 255:
        raise SystemExit("--tolerance must be between 0 and 255")
    if args.alpha_threshold < 0 or args.alpha_threshold > 254:
        raise SystemExit("--alpha-threshold must be between 0 and 254")
    if args.min_hole_size < 0:
        raise SystemExit("--min-hole-size must be >= 0")
    if args.hole_fringe_radius < 0:
        raise SystemExit("--hole-fringe-radius must be >= 0")
    if args.min_transparent_hole_size < 0:
        raise SystemExit("--min-transparent-hole-size must be >= 0")
    for name in ("hole_fringe_min_rgb", "hole_fringe_min_luma", "hole_fringe_max_chroma"):
        value = getattr(args, name)
        if value < 0 or value > 255:
            raise SystemExit(f"--{name.replace('_', '-')} must be between 0 and 255")
    if args.grid_columns < 1 or args.grid_rows < 1:
        raise SystemExit("--grid-columns and --grid-rows must be >= 1")
    if args.edge_defringe_radius < 0:
        raise SystemExit("--edge-defringe-radius must be >= 0")

    task_paths = args.paths or default_sprite_dirs(
        args.scope,
        args.include_nested,
        args.include_pose,
        args.include_portraits,
    )
    tasks: list[SpriteTask] = []
    for path in task_paths:
        tasks.extend(
            tasks_for_path(
                path,
                args.raw_action,
                args.dry_run,
                args.include_portraits,
            )
        )
    tasks = dedupe_tasks(tasks)

    if not tasks:
        print("No PNG sprites found to process.", file=sys.stderr)
        return 1

    total_removed = 0
    for task in tasks:
        result = clean_png(
            task,
            tolerance=args.tolerance,
            alpha_threshold=args.alpha_threshold,
            mode=args.mode,
            min_hole_size=args.min_hole_size,
            hole_fringe_radius=args.hole_fringe_radius,
            min_transparent_hole_size=args.min_transparent_hole_size,
            hole_fringe_min_rgb=args.hole_fringe_min_rgb,
            hole_fringe_min_luma=args.hole_fringe_min_luma,
            hole_fringe_max_chroma=args.hole_fringe_max_chroma,
            grid_columns=args.grid_columns,
            grid_rows=args.grid_rows,
            edge_defringe=args.edge_defringe,
            edge_defringe_radius=args.edge_defringe_radius,
            dry_run=args.dry_run,
        )
        total_removed += result.removed_pixels
        print_result(result, args.dry_run)

    print(f"Total sprites: {len(tasks)}; removed pixels: {total_removed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
