#!/usr/bin/env python3
"""Align monster and companion pose stills to a shared feet anchor.

Character art ships as a set of PNG "pose" stills on a (near-)white background:
idle / attack / hurt / death, etc. Each pose is drawn on its own, so
the character's feet land at a different spot in every file. In game they all
render in the same slot, so unless the feet sit at one fixed point the character
appears to hop between states.

This workflow re-anchors every pose to the feet of the reference pose (idle):

  1. Detect the character silhouette (pixels that aren't background white).
  2. Anchor Y = the lowest substantial support row. The support row must contain
     a wide enough contiguous silhouette segment, so low skinny sword/staff
     pixels are ignored when they dip below the actual feet.
     Anchor X defaults to the horizontal centroid of the bottom band. Ghost-like
     floating characters use the silhouette center instead, because their bottom
     pixels are tails, chains, hair, or flame wisps rather than planted feet.
     Death poses also use the silhouette center for X by default: fallen limbs
     and weapons often become the lowest support, but the corpse should stay
     centered under the standing body while its floor Y still matches the feet.
  3. Translate each pose so its feet anchor lands exactly on the reference's.
  4. Compute the union of the shifted silhouettes, add safety padding around
     that union, then expand the shorter canvas side to match the longer side.
     Extra horizontal room is balanced left/right; extra vertical room mostly
     goes above the character so the character sits lower in the square.
  5. Composite only the detected character silhouette onto a pure white canvas,
     so the whole still has a clean white background and no black or transparent
     border is introduced by the shift.

By default, input is expected at <pose-dir>/raw/<pose>.png and output goes to
the outer <pose-dir>/<pose>.png (RGB, white background). Use --root to align
outer pose PNGs in place, or --_raw to align preserved raw/_raw PNGs into raw.
The reference pose is never translated: it is composited at offset (0, 0), and
every other pose is moved to match its feet anchor.

Usage:
    python scripts/align_monster_poses.py                    # every monster pose/raw dir
    python scripts/align_monster_poses.py ghost-lady          # one monster by folder/name
    python scripts/align_monster_poses.py black               # one companion by folder/name
    python scripts/align_monster_poses.py ghost-lady --root   # align pose/*.png in place
    python scripts/align_monster_poses.py ghost-lady --_raw   # align raw/_raw into raw
    python scripts/align_monster_poses.py --scope companions  # every companion pose/raw dir
    python scripts/align_monster_poses.py black --upright-x-offset 200  # nicer fall into death
    python scripts/align_monster_poses.py black --pose-x-offset hurt=33  # hand-tune a pose
    python scripts/align_monster_poses.py blue --pose-y-offset run=-200  # lift a staged run pose
    python scripts/align_monster_poses.py blue --preserve-background  # shift the whole raw PNG
    python scripts/align_monster_poses.py path/to/pose ...   # specific pose or raw dir(s)
    python scripts/align_monster_poses.py --x-anchor center  # force floating-body horizontal anchor
    python scripts/align_monster_poses.py blue --x-anchor right-foot --upright-x-offset 200
    python scripts/align_monster_poses.py --death-x-anchor feet  # legacy death alignment
    python scripts/align_monster_poses.py --dry-run          # report shifts, write nothing

Requires: Pillow.
"""

from __future__ import annotations

import argparse
import statistics
import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path

try:
    from PIL import Image, ImageChops
except ModuleNotFoundError as exc:
    if exc.name != "PIL":
        raise
    raise SystemExit(
        "Missing dependency: Pillow.\n"
        "Install it for the Python interpreter running this script:\n"
        "  python -m pip install --user Pillow"
    ) from exc

REPO_ROOT = Path(__file__).resolve().parents[2]
COSMETICS_ROOT = REPO_ROOT / "frontend" / "public" / "cosmetics"
STORY_WORLDS_ROOT = COSMETICS_ROOT / "story-worlds"
LEGACY_STORY_WORLDS_ROOT = REPO_ROOT / "frontend" / "public" / "story-worlds"
STORY_WORLDS_ROOTS = (STORY_WORLDS_ROOT, LEGACY_STORY_WORLDS_ROOT)
COMPANION_ROOT = COSMETICS_ROOT / "companion"
POSE_DIR_NAME = "pose"
RAW_DIR_NAME = "raw"
ORIGINAL_RAW_DIR_NAME = "_raw"
HELPER_POSE_STEMS = {"attack-end", "attack-start", "idle-attack-row", "run"}
FLOATING_MONSTER_HINTS = ("ghost", "spirit", "wraith", "phantom")
SCOPES = ("auto", "monsters", "companions", "all")
BODY_FOCUS_HEIGHT_RATIO = 0.68
CENTERED_SUPPORT_TOLERANCE_RATIO = 0.25
SUPPORT_COLUMN_MARGIN_RATIO = 0.04
LOWER_FRAME_EXTRA_TOP_RATIO = 0.75


@dataclass
class PosePlan:
    path: Path
    image: Image.Image
    mask: Image.Image
    anchor: tuple[float, int, tuple[int, int, int, int]] | None
    dx: int
    dy: int
    note: str
    fill: tuple[int, int, int]


@dataclass(frozen=True)
class CanvasPlan:
    width: int
    height: int
    origin_x: int
    origin_y: int
    content_bbox: tuple[int, int, int, int]


def image_data(im: Image.Image):
    """Return a stable pixel iterator across Pillow versions."""
    if hasattr(im, "get_flattened_data"):
        return im.get_flattened_data()
    return im.getdata()


def silhouette_mask(im: Image.Image, threshold: int) -> Image.Image:
    """Binary "L" mask (255 = character, 0 = background).

    A pixel counts as character if any channel drops more than `threshold`
    below pure white -- i.e. min(r, g, b) < 255 - threshold. Using the darkest
    channel catches saturated colours (bright red, deep blue) that a plain
    luminance test would treat as light. If that grabs almost the whole image,
    fall back to a border flood that removes light neutral gray backgrounds.
    """
    r, g, b = im.convert("RGB").split()
    min_channel = ImageChops.darker(ImageChops.darker(r, g), b)
    cutoff = 255 - threshold
    mask = min_channel.point(lambda p: 255 if p < cutoff else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return mask

    min_x, min_y, max_x_excl, max_y_excl = bbox
    bbox_area = (max_x_excl - min_x) * (max_y_excl - min_y)
    image_area = mask.width * mask.height
    if bbox_area < image_area * 0.92:
        return mask

    return neutral_border_silhouette_mask(im)


def neutral_border_silhouette_mask(im: Image.Image) -> Image.Image:
    """Remove connected border background pixels from non-white backgrounds.

    Most generated sheets are white-backed, but some older monster poses sit on
    a black full-frame square. When the first white-threshold pass grabs nearly
    the whole image, sample the border colour and flood-fill only connected
    pixels close to that colour. Foreground pixels keep becoming the silhouette.
    """
    rgb = im.convert("RGB")
    pixels = rgb.load()
    w, h = rgb.size
    background = bytearray(w * h)
    queue: deque[tuple[int, int]] = deque()
    margin = min(8, max(1, w // 32), max(1, h // 32))
    samples: list[tuple[int, int, int]] = []

    for x in range(w):
        for y in range(margin):
            samples.append(pixels[x, y])
            samples.append(pixels[x, h - 1 - y])
    for y in range(h):
        for x in range(margin):
            samples.append(pixels[x, y])
            samples.append(pixels[w - 1 - x, y])

    bg = (
        int(statistics.median(px[0] for px in samples)),
        int(statistics.median(px[1] for px in samples)),
        int(statistics.median(px[2] for px in samples)),
    )
    tolerance = 52

    def idx(x: int, y: int) -> int:
        return y * w + x

    def is_background(x: int, y: int) -> bool:
        r, g, b = pixels[x, y]
        return max(abs(r - bg[0]), abs(g - bg[1]), abs(b - bg[2])) <= tolerance

    def push(x: int, y: int) -> None:
        i = idx(x, y)
        if not background[i] and is_background(x, y):
            background[i] = 1
            queue.append((x, y))

    for x in range(w):
        push(x, 0)
        push(x, h - 1)
    for y in range(h):
        push(0, y)
        push(w - 1, y)

    while queue:
        x, y = queue.popleft()
        if x:
            push(x - 1, y)
        if x + 1 < w:
            push(x + 1, y)
        if y:
            push(x, y - 1)
        if y + 1 < h:
            push(x, y + 1)

    return Image.frombytes("L", (w, h), bytes(0 if v else 255 for v in background))


def row_segments(mask: Image.Image, y: int) -> list[tuple[int, int, int]]:
    """Return contiguous foreground runs for one mask row as (left, right, width)."""
    pixels = mask.load()
    segments: list[tuple[int, int, int]] = []
    start: int | None = None
    previous = 0

    for x in range(mask.width):
        if pixels[x, y]:
            if start is None:
                start = x
            previous = x
        elif start is not None:
            segments.append((start, previous, previous - start + 1))
            start = None

    if start is not None:
        segments.append((start, previous, previous - start + 1))

    return segments


def segment_center(segment: tuple[int, int, int]) -> float:
    left, right, _ = segment
    return (left + right) / 2


def body_focus(mask: Image.Image, bbox: tuple[int, int, int, int]) -> tuple[float, int]:
    """Return (focus_x, focus_width) for the upper body/body mass.

    Low props such as hammers can be wider or lower than the feet. Looking at
    the upper part of the silhouette gives support-row selection a body-centered
    x reference without special-casing individual monsters.
    """
    min_x, min_y, max_x_excl, max_y_excl = bbox
    content_h = max_y_excl - min_y
    focus_bottom = min(max_y_excl, min_y + max(1, round(content_h * BODY_FOCUS_HEIGHT_RATIO)))
    focus = mask.crop((0, min_y, mask.width, focus_bottom))
    focus_bbox = focus.getbbox()
    focus_w = focus.width
    sum_x = 0
    count = 0

    for i, v in enumerate(image_data(focus)):
        if v:
            sum_x += i % focus_w
            count += 1

    focus_x = sum_x / count if count else center_x_for_bbox(bbox)
    focus_width = (focus_bbox[2] - focus_bbox[0]) if focus_bbox is not None else (max_x_excl - min_x)
    return focus_x, focus_width


def lowest_support(
    mask: Image.Image,
    bbox: tuple[int, int, int, int],
    support_segment_ratio: float,
    min_support_width: int,
) -> tuple[int, list[tuple[int, int, int]]]:
    """Return the lowest row and row segments that look like body support.

    Weapon tips and stray antialiasing often create a lower absolute bbox edge
    than the feet. Requiring a minimum contiguous run keeps those skinny pixels
    from becoming the floor anchor. Broad low props need another guard, so rows
    whose support segments are far from the body focus are skipped when a more
    centered support row exists.
    """
    min_x, min_y, max_x_excl, max_y_excl = bbox
    content_w = max_x_excl - min_x
    required_width = max(min_support_width, round(content_w * support_segment_ratio))
    focus_x, focus_width = body_focus(mask, bbox)
    center_tolerance = max(
        required_width * 2,
        min(content_w, focus_width) * CENTERED_SUPPORT_TOLERANCE_RATIO,
    )
    fallback: tuple[int, list[tuple[int, int, int]]] | None = None

    for y in range(max_y_excl - 1, min_y - 1, -1):
        support_segments = [segment for segment in row_segments(mask, y) if segment[2] >= required_width]
        if not support_segments:
            continue

        if fallback is None:
            fallback = (y, support_segments)

        centered_segments = [
            segment for segment in support_segments if abs(segment_center(segment) - focus_x) <= center_tolerance
        ]
        if centered_segments:
            return y, centered_segments

    if fallback is not None:
        return fallback
    return max_y_excl - 1, []


def lowest_support_row(
    mask: Image.Image,
    bbox: tuple[int, int, int, int],
    support_segment_ratio: float,
    min_support_width: int,
) -> int:
    return lowest_support(mask, bbox, support_segment_ratio, min_support_width)[0]


def feet_anchor(
    mask: Image.Image,
    foot_band: float,
    support_segment_ratio: float,
    min_support_width: int,
):
    """Return (feet_cx, feet_y, bbox) or None if the mask is empty.

    feet_y is the lowest substantial support row; feet_cx is the horizontal
    centroid of the silhouette within the bottom `foot_band` fraction above that
    support row.
    """
    bbox = mask.getbbox()
    if bbox is None:
        return None
    min_x, min_y, max_x_excl, max_y_excl = bbox
    max_y, support_segments = lowest_support(mask, bbox, support_segment_ratio, min_support_width)
    content_h = max_y_excl - min_y
    band_top = max(min_y, max_y - int(content_h * foot_band))

    band = mask.crop((0, band_top, mask.width, max_y + 1))
    band_w = band.width
    column_left = 0
    column_right = band_w - 1
    if support_segments:
        column_margin = max(1, round((max_x_excl - min_x) * SUPPORT_COLUMN_MARGIN_RATIO))
        column_left = max(0, min(left for left, _, _ in support_segments) - column_margin)
        column_right = min(mask.width - 1, max(right for _, right, _ in support_segments) + column_margin)

    sum_x = 0
    count = 0
    for i, v in enumerate(image_data(band)):
        x = i % band_w
        if v and column_left <= x <= column_right:
            sum_x += x
            count += 1
    feet_cx = sum_x / count if count else (min_x + max_x_excl - 1) / 2
    return feet_cx, max_y, bbox


def side_foot_anchor(
    mask: Image.Image,
    support_segment_ratio: float,
    min_support_width: int,
    side: str,
):
    """Return the first lower-row foot segment on the requested image side.

    Some companion idle poses have one boot lower than the other. A generic
    "feet" anchor picks the absolute lowest boot, but pose staging often needs
    the visible image-right or image-left boot instead.
    """
    bbox = mask.getbbox()
    if bbox is None:
        return None

    min_x, min_y, max_x_excl, max_y_excl = bbox
    content_w = max_x_excl - min_x
    content_h = max_y_excl - min_y
    required_width = max(min_support_width, round(content_w * support_segment_ratio))
    side_threshold = min_x + (content_w * (0.6 if side == "right" else 0.4))
    lower_top = min(max_y_excl - 1, min_y + round(content_h * 0.62))

    for y in range(max_y_excl - 1, lower_top - 1, -1):
        segments = [segment for segment in row_segments(mask, y) if segment[2] >= required_width]
        if side == "right":
            candidates = [segment for segment in segments if segment_center(segment) >= side_threshold]
            if candidates:
                segment = max(candidates, key=segment_center)
                return segment_center(segment), y, bbox
        else:
            candidates = [segment for segment in segments if segment_center(segment) <= side_threshold]
            if candidates:
                segment = min(candidates, key=segment_center)
                return segment_center(segment), y, bbox

    return feet_anchor(mask, 0.12, support_segment_ratio, min_support_width)


def center_x_for_bbox(bbox: tuple[int, int, int, int]) -> float:
    min_x, _, max_x_excl, _ = bbox
    return (min_x + max_x_excl - 1) / 2


def alignment_anchor(
    mask: Image.Image,
    foot_band: float,
    support_segment_ratio: float,
    min_support_width: int,
    x_anchor: str,
):
    """Return (anchor_x, support_y, bbox), using the requested horizontal anchor."""
    if x_anchor == "right-foot":
        return side_foot_anchor(mask, support_segment_ratio, min_support_width, "right")
    if x_anchor == "left-foot":
        return side_foot_anchor(mask, support_segment_ratio, min_support_width, "left")

    anchor = feet_anchor(mask, foot_band, support_segment_ratio, min_support_width)
    if anchor is None:
        return None

    feet_cx, support_y, bbox = anchor
    if x_anchor == "center":
        return center_x_for_bbox(bbox), support_y, bbox
    return feet_cx, support_y, bbox


def pose_x_anchor(pose_name: str, x_anchor: str, death_x_anchor: str) -> str:
    """Return the horizontal anchor mode to use for one pose."""
    if pose_name != "death":
        return x_anchor
    if death_x_anchor == "same":
        return x_anchor
    return death_x_anchor


def is_upright_pose(pose_name: str) -> bool:
    return pose_name != "death"


def background_color(im: Image.Image, mask: Image.Image, margin: int = 6):
    """Median RGB of background pixels along the image border."""
    rgb = im.convert("RGB")
    w, h = rgb.size
    strips = [
        (0, 0, w, margin),          # top
        (0, h - margin, w, h),      # bottom
        (0, 0, margin, h),          # left
        (w - margin, 0, w, h),      # right
    ]
    samples: list[tuple[int, int, int]] = []
    for box in strips:
        pixels = image_data(rgb.crop(box))
        mask_pixels = image_data(mask.crop(box))
        samples.extend(px for px, m in zip(pixels, mask_pixels) if not m)
    if not samples:
        return (255, 255, 255)
    return (
        int(statistics.median(s[0] for s in samples)),
        int(statistics.median(s[1] for s in samples)),
        int(statistics.median(s[2] for s in samples)),
    )


def parse_fill(bg_mode: str):
    """'sample' -> None (per-image), 'white' -> (255,255,255), '#rrggbb' -> tuple."""
    if bg_mode == "sample":
        return None
    if bg_mode == "white":
        return (255, 255, 255)
    hex_str = bg_mode.lstrip("#")
    if len(hex_str) != 6:
        raise argparse.ArgumentTypeError(f"--bg must be 'sample', 'white', or #rrggbb (got {bg_mode!r})")
    return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))


def parse_pose_offsets(values: list[str] | None, label: str) -> dict[str, int]:
    offsets: dict[str, int] = {}
    for value in values or []:
        if "=" not in value:
            raise argparse.ArgumentTypeError(f"{label} must be pose=px (got {value!r})")
        pose, raw_offset = value.split("=", 1)
        pose = pose.strip().removesuffix(".png")
        if not pose:
            raise argparse.ArgumentTypeError(f"{label} is missing a pose name (got {value!r})")
        try:
            offsets[pose] = int(raw_offset)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"{label} must be an integer (got {value!r})") from exc
    return offsets


def is_alignable_pose_png(path: Path) -> bool:
    """Return true for single-pose stills, false for helper/contact images."""
    if path.suffix.lower() != ".png":
        return False
    stem = path.stem
    if stem in HELPER_POSE_STEMS:
        return False
    if stem.endswith("-row"):
        return False
    if stem.startswith("_"):
        return False
    return True


def pose_png_paths(source_dir: Path) -> list[Path]:
    return sorted(path for path in source_dir.glob("*.png") if path.is_file() and is_alignable_pose_png(path))


def shifted_content_bbox(plan: PosePlan, preserve_background: bool) -> tuple[int, int, int, int] | None:
    if preserve_background:
        bbox = (0, 0, plan.image.width, plan.image.height)
    else:
        bbox = plan.mask.getbbox()
        if bbox is None:
            return None

    min_x, min_y, max_x_excl, max_y_excl = bbox
    return (
        min_x + plan.dx,
        min_y + plan.dy,
        max_x_excl + plan.dx,
        max_y_excl + plan.dy,
    )


def natural_canvas(plans: list[PosePlan], crop_padding: int, preserve_background: bool) -> CanvasPlan:
    """Return a per-folder natural square canvas around shifted visible content.

    The output does not inherit the largest source image. Each monster/companion
    gets one consistent canvas sized to the union of that character's aligned
    poses plus padding, then the shorter side is expanded to match the longer
    side so every pose keeps a uniform square aspect ratio. Extra horizontal
    room is centered; extra vertical room is biased above the art so the
    character sits lower in the frame.
    """
    shifted_bboxes = [bbox for plan in plans if (bbox := shifted_content_bbox(plan, preserve_background))]
    if not shifted_bboxes:
        return CanvasPlan(1, 1, crop_padding, crop_padding, (0, 0, 0, 0))

    min_x = min(bbox[0] for bbox in shifted_bboxes)
    min_y = min(bbox[1] for bbox in shifted_bboxes)
    max_x_excl = max(bbox[2] for bbox in shifted_bboxes)
    max_y_excl = max(bbox[3] for bbox in shifted_bboxes)
    width = max(1, max_x_excl - min_x + (crop_padding * 2))
    height = max(1, max_y_excl - min_y + (crop_padding * 2))
    side = max(width, height)
    extra_x = side - width
    extra_y = side - height
    extra_left = extra_x // 2
    extra_top = round(extra_y * LOWER_FRAME_EXTRA_TOP_RATIO)
    return CanvasPlan(
        width=side,
        height=side,
        origin_x=-min_x + crop_padding + extra_left,
        origin_y=-min_y + crop_padding + extra_top,
        content_bbox=(min_x, min_y, max_x_excl, max_y_excl),
    )


def align_dir(
    source_dir: Path,
    out_dir: Path,
    reference: str,
    threshold: int,
    foot_band: float,
    support_segment_ratio: float,
    min_support_width: int,
    crop_padding: int,
    x_anchor: str,
    death_x_anchor: str,
    upright_x_offset: int,
    pose_x_offsets: dict[str, int],
    pose_y_offsets: dict[str, int],
    fill_color,
    preserve_background: bool,
    dry_run: bool,
) -> None:
    ref_path = source_dir / f"{reference}.png"
    rel_source = source_dir.relative_to(REPO_ROOT) if source_dir.is_relative_to(REPO_ROOT) else source_dir
    rel_out = out_dir.relative_to(REPO_ROOT) if out_dir.is_relative_to(REPO_ROOT) else out_dir
    print(f"\n{rel_source} -> {rel_out}")

    all_png_paths = sorted(path for path in source_dir.glob("*.png") if path.is_file())
    png_paths = pose_png_paths(source_dir)
    if not png_paths:
        print("  ! skipped: no PNG files found")
        return

    ignored_paths = [path for path in all_png_paths if path not in png_paths]
    if ignored_paths:
        ignored = ", ".join(path.name for path in ignored_paths)
        print(f"  ignored helper/non-pose PNGs: {ignored}")

    if not ref_path.exists():
        print(f"  ! skipped: no reference {reference}.png")
        return

    ref_mask = silhouette_mask(Image.open(ref_path), threshold)
    ref_anchors = {
        anchor_mode: alignment_anchor(
            ref_mask,
            foot_band,
            support_segment_ratio,
            min_support_width,
            anchor_mode,
        )
        for anchor_mode in ("feet", "center", "left-foot", "right-foot")
    }
    ref = ref_anchors[x_anchor]
    if ref is None:
        print(f"  ! skipped: {reference}.png has no detectable character")
        return
    ref_cx, ref_y, _ = ref
    ref_x = round(ref_cx)
    print(
        f"  x-anchor={x_anchor} death-x-anchor={death_x_anchor} "
        f"reference {reference}: anchor=({ref_x}, {ref_y})"
    )

    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    plans: list[PosePlan] = []
    for path in png_paths:
        im = Image.open(path)
        mask = silhouette_mask(im, threshold)
        anchor_mode = pose_x_anchor(path.stem, x_anchor, death_x_anchor)
        anchor = alignment_anchor(mask, foot_band, support_segment_ratio, min_support_width, anchor_mode)
        if path.stem == reference:
            dx = dy = 0
            note = "reference pose -> shift=(+0, +0)"
        elif anchor is None:
            dx = dy = 0
            note = "empty mask -> background canvas"
        else:
            target_ref = ref_anchors[anchor_mode]
            if target_ref is None:
                print(f"  ! skipped: {reference}.png has no detectable {anchor_mode} anchor")
                return
            target_ref_x, target_ref_y, _ = target_ref
            cx, y, _ = anchor
            dx = round(target_ref_x) - round(cx)
            dy = round(target_ref_y - y)
            note = f"x-anchor={anchor_mode} anchor=({cx:.0f}, {y})  shift=({dx:+d}, {dy:+d})"

        if upright_x_offset and is_upright_pose(path.stem):
            dx += upright_x_offset
            note = f"{note}  upright-x-offset=({upright_x_offset:+d})"

        pose_x_offset = pose_x_offsets.get(path.stem, 0)
        if pose_x_offset:
            dx += pose_x_offset
            note = f"{note}  pose-x-offset=({pose_x_offset:+d})"

        pose_y_offset = pose_y_offsets.get(path.stem, 0)
        if pose_y_offset:
            dy += pose_y_offset
            note = f"{note}  pose-y-offset=({pose_y_offset:+d})"

        fill = fill_color if fill_color is not None else background_color(im, mask)
        plans.append(PosePlan(path, im, mask, anchor, dx, dy, note, fill))

    canvas_plan = natural_canvas(plans, crop_padding, preserve_background)
    out_w = canvas_plan.width
    out_h = canvas_plan.height
    print(
        "  natural square canvas "
        f"content={canvas_plan.content_bbox} padding={crop_padding} canvas=({out_w}x{out_h})"
    )

    for plan in plans:
        print(f"  {plan.path.name:14} {plan.note}")

        if dry_run:
            continue
        canvas = Image.new("RGB", (out_w, out_h), plan.fill)
        if preserve_background:
            canvas.paste(
                plan.image.convert("RGB"),
                (canvas_plan.origin_x + plan.dx, canvas_plan.origin_y + plan.dy),
            )
        else:
            bbox = plan.mask.getbbox()
            if bbox is not None:
                min_x, min_y, _, _ = bbox
                canvas.paste(
                    plan.image.convert("RGB").crop(bbox),
                    (canvas_plan.origin_x + plan.dx + min_x, canvas_plan.origin_y + plan.dy + min_y),
                    plan.mask.crop(bbox),
                )
        canvas.save(out_dir / plan.path.name)


def source_and_output_for_pose_dir(pose_dir: Path, target: str) -> tuple[Path, Path]:
    if target == "root":
        return pose_dir, pose_dir
    if target == ORIGINAL_RAW_DIR_NAME:
        raw_dir = pose_dir / RAW_DIR_NAME
        return raw_dir / ORIGINAL_RAW_DIR_NAME, raw_dir
    raw_dir = pose_dir / RAW_DIR_NAME
    return raw_dir, pose_dir


def existing_story_world_roots() -> list[Path]:
    roots: list[Path] = []
    seen: set[Path] = set()
    for root in STORY_WORLDS_ROOTS:
        resolved = root.resolve()
        if resolved in seen or not root.exists():
            continue
        seen.add(resolved)
        roots.append(root)
    return roots


def discover_source_dirs(target: str, scope: str) -> list[tuple[Path, Path]]:
    jobs: list[tuple[Path, Path]] = []
    discovery_scope = "monsters" if scope == "auto" else scope

    if discovery_scope in {"monsters", "all"}:
        for story_world_root in existing_story_world_roots():
            for pose_dir in sorted(story_world_root.glob(f"*/monsters/*/{POSE_DIR_NAME}")):
                source_dir, out_dir = source_and_output_for_pose_dir(pose_dir, target)
                if source_dir.is_dir():
                    jobs.append((source_dir, out_dir))

    if discovery_scope in {"companions", "all"}:
        for pose_dir in sorted(COMPANION_ROOT.glob(f"*/{POSE_DIR_NAME}")):
            source_dir, out_dir = source_and_output_for_pose_dir(pose_dir, target)
            if source_dir.is_dir():
                jobs.append((source_dir, out_dir))

    return jobs


def asset_folder_candidates(asset: str) -> list[str]:
    """Return likely asset folder names for a user-facing monster or companion name."""
    cleaned = asset.strip()
    candidates = [
        cleaned,
        cleaned.lower(),
        cleaned.replace(" ", "_"),
        cleaned.replace(" ", "-"),
        cleaned.replace("-", "_").replace(" ", "_"),
        cleaned.replace("_", "-").replace(" ", "-"),
    ]

    seen: set[str] = set()
    unique: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in seen:
            seen.add(candidate)
            unique.append(candidate)
    return unique


def resolve_monster_source_and_output(monster: str, story_world: str, target: str) -> tuple[Path, Path] | None:
    for folder in asset_folder_candidates(monster):
        for story_world_root in existing_story_world_roots():
            pose_dir = story_world_root / story_world / "monsters" / folder / POSE_DIR_NAME
            source_dir, out_dir = source_and_output_for_pose_dir(pose_dir, target)
            if source_dir.is_dir():
                return source_dir.resolve(), out_dir.resolve()
    return None


def resolve_companion_source_and_output(companion: str, target: str) -> tuple[Path, Path] | None:
    for folder in asset_folder_candidates(companion):
        pose_dir = COMPANION_ROOT / folder / POSE_DIR_NAME
        source_dir, out_dir = source_and_output_for_pose_dir(pose_dir, target)
        if source_dir.is_dir():
            return source_dir.resolve(), out_dir.resolve()
    return None


def named_scope_order(scope: str) -> tuple[str, ...]:
    if scope in {"auto", "all"}:
        return ("monsters", "companions")
    return (scope,)


def resolve_named_source_and_output(name: str, story_world: str, target: str, scope: str) -> tuple[Path, Path] | None:
    for asset_scope in named_scope_order(scope):
        if asset_scope == "monsters":
            monster_paths = resolve_monster_source_and_output(name, story_world, target)
            if monster_paths is not None:
                return monster_paths
        elif asset_scope == "companions":
            companion_paths = resolve_companion_source_and_output(name, target)
            if companion_paths is not None:
                return companion_paths
    return None


def looks_like_path(path: Path) -> bool:
    raw = str(path)
    return path.is_absolute() or "/" in raw or "\\" in raw


def resolve_source_and_output(path: Path, story_world: str, target: str, scope: str) -> tuple[Path, Path]:
    resolved = path.resolve()
    if resolved.name == RAW_DIR_NAME:
        return resolved, resolved.parent

    if resolved.name == ORIGINAL_RAW_DIR_NAME and resolved.parent.name == RAW_DIR_NAME:
        return resolved, resolved.parent

    if resolved.name == POSE_DIR_NAME:
        return source_and_output_for_pose_dir(resolved, target)

    raw_dir = resolved / RAW_DIR_NAME
    if raw_dir.is_dir():
        return source_and_output_for_pose_dir(resolved, target)

    if not looks_like_path(path):
        named_paths = resolve_named_source_and_output(str(path), story_world, target, scope)
        if named_paths is not None:
            return named_paths

    return resolved, resolved


def resolve_jobs(pose_dirs: list[Path], story_world: str, target: str, scope: str) -> list[tuple[Path, Path]]:
    if not pose_dirs:
        return discover_source_dirs(target, scope)

    if len(pose_dirs) > 1 and all(not looks_like_path(path) for path in pose_dirs):
        joined_name = " ".join(str(path) for path in pose_dirs)
        named_paths = resolve_named_source_and_output(joined_name, story_world, target, scope)
        if named_paths is not None:
            return [named_paths]

    return [resolve_source_and_output(path, story_world, target, scope) for path in pose_dirs]


def asset_slug_for_source(source_dir: Path) -> str:
    if source_dir.name == ORIGINAL_RAW_DIR_NAME and source_dir.parent.name == RAW_DIR_NAME:
        return source_dir.parent.parent.parent.name.lower()
    if source_dir.name == RAW_DIR_NAME and source_dir.parent.name == POSE_DIR_NAME:
        return source_dir.parent.parent.name.lower()
    if source_dir.name == POSE_DIR_NAME:
        return source_dir.parent.name.lower()
    return source_dir.parent.name.lower()


def is_companion_source(source_dir: Path) -> bool:
    try:
        source_dir.resolve().relative_to(COMPANION_ROOT.resolve())
    except ValueError:
        return False
    return True


def resolve_x_anchor(source_dir: Path, x_anchor: str) -> str:
    if x_anchor != "auto":
        return x_anchor

    if is_companion_source(source_dir):
        return "center"

    slug = asset_slug_for_source(source_dir)
    if any(hint in slug for hint in FLOATING_MONSTER_HINTS):
        return "center"
    return "feet"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "pose_dirs",
        nargs="*",
        type=Path,
        help="monster/companion names or source directories (default: every matching monster directory)",
    )
    parser.add_argument("--story-world", "--theme", dest="story_world", default="arcane-spire", help="story world slug for monster-name arguments (default: arcane-spire)")
    parser.add_argument(
        "--scope",
        choices=SCOPES,
        default="auto",
        help=(
            "which asset family to resolve; auto batches monsters but named targets try monsters then companions "
            "(default: auto)"
        ),
    )
    target_group = parser.add_mutually_exclusive_group()
    target_group.add_argument("--root", dest="target", action="store_const", const="root", help="read and write pose/*.png")
    target_group.add_argument("--raw", dest="target", action="store_const", const=RAW_DIR_NAME, help="read pose/raw/*.png and write pose/*.png (default)")
    target_group.add_argument("--_raw", dest="target", action="store_const", const=ORIGINAL_RAW_DIR_NAME, help="read pose/raw/_raw/*.png and write pose/raw/*.png")
    parser.set_defaults(target=RAW_DIR_NAME)
    parser.add_argument("--reference", default="idle", help="pose used as the feet anchor (default: idle)")
    parser.add_argument("--threshold", type=int, default=24, help="channel drop below white that counts as character (default: 24)")
    parser.add_argument("--foot-band", type=float, default=0.12, help="bottom fraction of the silhouette used as feet (default: 0.12)")
    parser.add_argument(
        "--support-segment-ratio",
        type=float,
        default=0.025,
        help="minimum support-row segment width as a fraction of silhouette width (default: 0.025)",
    )
    parser.add_argument(
        "--min-support-width",
        type=int,
        default=20,
        help="minimum contiguous support-row pixels before a row can count as feet (default: 20)",
    )
    parser.add_argument(
        "--crop-padding",
        type=int,
        default=32,
        help="extra white padding when shifted art touches or crosses a frame edge (default: 32)",
    )
    parser.add_argument(
        "--x-anchor",
        choices=("auto", "feet", "center", "left-foot", "right-foot"),
        default="auto",
        help=(
            "horizontal anchor: bottom-band feet, silhouette center, image-side foot, "
            "or auto by asset name (default: auto)"
        ),
    )
    parser.add_argument(
        "--death-x-anchor",
        choices=("same", "feet", "center", "left-foot", "right-foot"),
        default="center",
        help="horizontal anchor for death.png; 'same' uses --x-anchor, 'feet' restores legacy behavior (default: center)",
    )
    parser.add_argument(
        "--upright-x-offset",
        type=int,
        default=0,
        help="extra horizontal shift applied after alignment to every non-death pose; useful for staged falls (default: 0)",
    )
    parser.add_argument(
        "--pose-x-offset",
        action="append",
        default=[],
        metavar="POSE=PX",
        help="extra horizontal shift for one named pose after alignment; may be repeated (example: hurt=33)",
    )
    parser.add_argument(
        "--pose-y-offset",
        action="append",
        default=[],
        metavar="POSE=PX",
        help="extra vertical shift for one named pose after alignment; may be repeated (example: run=-200)",
    )
    parser.add_argument("--bg", default="white", help="fill for revealed strips: 'white' (default), 'sample' (per-image), or #rrggbb")
    parser.add_argument(
        "--preserve-background",
        action="store_true",
        help="paste the whole source image instead of masking the character onto a clean canvas",
    )
    parser.add_argument("--dry-run", action="store_true", help="report shifts without writing files")
    args = parser.parse_args(argv)

    fill_color = parse_fill(args.bg)
    if args.preserve_background and args.bg == "white":
        fill_color = None
    try:
        pose_x_offsets = parse_pose_offsets(args.pose_x_offset, "--pose-x-offset")
        pose_y_offsets = parse_pose_offsets(args.pose_y_offset, "--pose-y-offset")
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))
    jobs = resolve_jobs(args.pose_dirs, args.story_world, args.target, args.scope)
    if not jobs:
        story_roots = " / ".join(str(root) for root in STORY_WORLDS_ROOTS)
        print(f"No pose/raw directories found for scope {args.scope!r} under {story_roots} / {COMPANION_ROOT}", file=sys.stderr)
        return 1

    for source_dir, out_dir in jobs:
        x_anchor = resolve_x_anchor(source_dir, args.x_anchor)
        align_dir(
            source_dir,
            out_dir,
            args.reference,
            args.threshold,
            args.foot_band,
            args.support_segment_ratio,
            args.min_support_width,
            args.crop_padding,
            x_anchor,
            args.death_x_anchor,
            args.upright_x_offset,
            pose_x_offsets,
            pose_y_offsets,
            fill_color,
            args.preserve_background,
            args.dry_run,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
