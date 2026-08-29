"""Make legacy 5x5 runtime sprite sheets safe at every frame boundary.

Modern generated effects are rebuilt from retained raw art by
``process_companion_spell_sheets.py``. Older monster worlds and a few actor
strips have no raw masters, so their baked PNG is the only recoverable source.
This tool applies one shared transform to all 25 frames, preserving motion and
direction while moving every visible pixel inside a transparent safety margin.

Strong VFX cuts at a cell boundary receive a short alpha feather before the
shared transform. Actor sheets are never feathered: their silhouettes are kept
intact and only translated/scaled as one animation.

The command is a dry run unless ``--write`` is supplied.
"""

from __future__ import annotations

import argparse
import json
import statistics
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from process_companion_spell_sheets import (
    ALPHA_THRESHOLD,
    GRID_COLUMNS,
    GRID_ROWS,
    measure_place_anchor,
    measure_place_bounds,
    save_image_atomic,
    write_json_lf,
)

ROOT = Path(__file__).resolve().parents[2]
COSMETICS_ROOT = ROOT / "frontend" / "public" / "cosmetics"
DEFAULT_MARGIN = 2
EDGE_SAMPLE_PX = 2
EFFECT_FEATHER_PX = 24
EFFECT_FEATHER_MIN_PIXELS = 12


@dataclass(frozen=True)
class SheetReport:
    path: Path
    frame_size: tuple[int, int]
    touching_frames_before: int
    touching_pixels_before: int
    feathered_frame_edges: int
    scale: float
    offset: tuple[int, int]


def runtime_png_paths() -> list[Path]:
    """Return the browser-addressable companion and monster PNG surfaces."""
    companion = COSMETICS_ROOT / "companion"
    story_worlds = COSMETICS_ROOT / "story-worlds"
    paths = [
        *companion.glob("*/*.png"),
        *(path for path in companion.glob("*/effects/*/*.png") if not path.name.startswith("_")),
        *story_worlds.glob("*/monsters/monster-*/*.png"),
        *(
            path
            for path in story_worlds.glob("*/monsters/monster-*/effects/*.png")
            if not path.name.startswith("_")
        ),
    ]
    return sorted(set(paths))


def frame_boxes(size: tuple[int, int]) -> list[tuple[int, int, int, int]]:
    width, height = size
    if width % GRID_COLUMNS or height % GRID_ROWS:
        return []
    frame_width = width // GRID_COLUMNS
    frame_height = height // GRID_ROWS
    if frame_width != frame_height:
        return []
    return [
        (
            column * frame_width,
            row * frame_height,
            (column + 1) * frame_width,
            (row + 1) * frame_height,
        )
        for row in range(GRID_ROWS)
        for column in range(GRID_COLUMNS)
    ]


def threshold_bbox(frame: Image.Image) -> tuple[int, int, int, int] | None:
    alpha = frame.getchannel("A").point(lambda value: 255 if value > ALPHA_THRESHOLD else 0)
    return alpha.getbbox()


def edge_pixel_counts(
    frame: Image.Image,
    edge_width: int = EDGE_SAMPLE_PX,
) -> dict[str, int]:
    alpha = frame.getchannel("A")
    width, height = frame.size
    edge = max(1, min(edge_width, width, height))
    return {
        "top": sum(
            1 for value in alpha.crop((0, 0, width, edge)).getdata() if value > ALPHA_THRESHOLD
        ),
        "bottom": sum(
            1
            for value in alpha.crop((0, height - edge, width, height)).getdata()
            if value > ALPHA_THRESHOLD
        ),
        "left": sum(
            1
            for value in alpha.crop((0, edge, edge, height - edge)).getdata()
            if value > ALPHA_THRESHOLD
        ),
        "right": sum(
            1
            for value in alpha.crop((width - edge, edge, width, height - edge)).getdata()
            if value > ALPHA_THRESHOLD
        ),
    }


def soften_clipped_effect_edges(frame: Image.Image) -> tuple[Image.Image, int]:
    """Fade strong VFX cuts at the exact cell rim so they dissipate naturally."""
    import numpy as np

    counts = edge_pixel_counts(frame)
    clipped_edges = {edge for edge, count in counts.items() if count >= EFFECT_FEATHER_MIN_PIXELS}
    if not clipped_edges:
        return frame, 0

    arr = np.asarray(frame.convert("RGBA")).copy()
    alpha = arr[..., 3].astype(np.float32)
    height, width = alpha.shape
    ramp = np.linspace(0.0, 1.0, EFFECT_FEATHER_PX + 1, dtype=np.float32)[:EFFECT_FEATHER_PX] ** 1.6
    if "top" in clipped_edges:
        alpha[:EFFECT_FEATHER_PX, :] *= ramp[:, None]
    if "bottom" in clipped_edges:
        alpha[height - EFFECT_FEATHER_PX :, :] *= ramp[::-1, None]
    if "left" in clipped_edges:
        alpha[:, :EFFECT_FEATHER_PX] *= ramp[None, :]
    if "right" in clipped_edges:
        alpha[:, width - EFFECT_FEATHER_PX :] *= ramp[None, ::-1]
    arr[..., 3] = np.clip(alpha, 0, 255).astype(np.uint8)
    arr[arr[..., 3] == 0, :3] = 0
    return Image.fromarray(arr, mode="RGBA"), len(clipped_edges)


def read_json_object(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def placement_mode(path: Path) -> str:
    """Use the authored target anchor when available; actors stay foot-planted."""
    if path.parent.name != "effects" and "effects" not in path.parts:
        return "feet"

    manifest_path = path.parent / "manifest.json"
    manifest = read_json_object(manifest_path)
    if "sprites" in manifest:
        sprites = manifest.get("sprites")
        entry = sprites.get(path.stem) if isinstance(sprites, dict) else None
        if isinstance(entry, dict):
            playback = str(entry.get("playback", "target"))
            anchor = str(entry.get("anchor", "center"))
            return "feet" if playback == "ground" or anchor == "feet" else "center"
    else:
        playback = str(manifest.get("playback", "target"))
        anchor = str(manifest.get("anchor", "center"))
        return "feet" if playback == "ground" or anchor == "feet" else "center"
    return "center"


def stable_pivot(
    bboxes: list[tuple[int, int, int, int]],
    mode: str,
    frame_size: tuple[int, int],
) -> tuple[float, float]:
    width, height = frame_size
    if not bboxes:
        return width / 2, height / 2
    centers_x = [(x0 + x1) / 2 for x0, _y0, x1, _y1 in bboxes]
    if mode == "feet":
        verticals = [y1 for _x0, _y0, _x1, y1 in bboxes]
    else:
        verticals = [(y0 + y1) / 2 for _x0, y0, _x1, y1 in bboxes]
    return statistics.median(centers_x), statistics.median(verticals)


def transform_intervals(
    bboxes: list[tuple[int, int, int, int]],
    pivot: tuple[float, float],
    scale: float,
    frame_size: tuple[int, int],
    margin: int,
) -> tuple[float, float, float, float]:
    width, height = frame_size
    pivot_x, pivot_y = pivot
    left = max(margin - (pivot_x + (x0 - pivot_x) * scale) for x0, _y0, _x1, _y1 in bboxes)
    right = min(width - margin - (pivot_x + (x1 - pivot_x) * scale) for _x0, _y0, x1, _y1 in bboxes)
    top = max(margin - (pivot_y + (y0 - pivot_y) * scale) for _x0, y0, _x1, _y1 in bboxes)
    bottom = min(
        height - margin - (pivot_y + (y1 - pivot_y) * scale) for _x0, _y0, _x1, y1 in bboxes
    )
    return left, right, top, bottom


def choose_transform(
    bboxes: list[tuple[int, int, int, int]],
    pivot: tuple[float, float],
    frame_size: tuple[int, int],
    margin: int,
) -> tuple[float, tuple[int, int]]:
    if not bboxes:
        return 1.0, (0, 0)

    # Reserve two pixels for LANCZOS ringing so the post-resize alpha still
    # clears the requested visible margin.
    calculation_margin = margin + 2

    def feasible(scale: float) -> bool:
        left, right, top, bottom = transform_intervals(
            bboxes, pivot, scale, frame_size, calculation_margin
        )
        return left <= right and top <= bottom

    if feasible(1.0):
        scale = 1.0
    else:
        low = 0.25
        high = 1.0
        if not feasible(low):
            raise ValueError("Visible sprite content cannot fit inside the frame safety margin")
        for _ in range(32):
            middle = (low + high) / 2
            if feasible(middle):
                low = middle
            else:
                high = middle
        scale = max(0.25, low - 0.002)

    left, right, top, bottom = transform_intervals(
        bboxes, pivot, scale, frame_size, calculation_margin
    )
    offset_x = min(max(0.0, left), right)
    offset_y = min(max(0.0, top), bottom)
    return scale, (round(offset_x), round(offset_y))


def alpha_composite_clipped(
    base: Image.Image,
    overlay: Image.Image,
    destination: tuple[int, int],
) -> None:
    x, y = destination
    source_left = max(0, -x)
    source_top = max(0, -y)
    source_right = min(overlay.width, base.width - x)
    source_bottom = min(overlay.height, base.height - y)
    if source_right <= source_left or source_bottom <= source_top:
        return
    base.alpha_composite(
        overlay.crop((source_left, source_top, source_right, source_bottom)),
        (x + source_left, y + source_top),
    )


def transform_frame(
    frame: Image.Image,
    pivot: tuple[float, float],
    scale: float,
    offset: tuple[int, int],
) -> Image.Image:
    width, height = frame.size
    target_width = max(1, round(width * scale))
    target_height = max(1, round(height * scale))
    actual_scale_x = target_width / width
    actual_scale_y = target_height / height
    premultiplied = frame.convert("RGBa").resize(
        (target_width, target_height),
        Image.Resampling.LANCZOS,
    )
    resized = premultiplied.convert("RGBA")
    paste_x = round(pivot[0] - pivot[0] * actual_scale_x + offset[0])
    paste_y = round(pivot[1] - pivot[1] * actual_scale_y + offset[1])
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    alpha_composite_clipped(out, resized, (paste_x, paste_y))
    return out


def visible_margin_count(frame: Image.Image, margin: int) -> int:
    return sum(edge_pixel_counts(frame, edge_width=margin).values())


def harden_sheet(
    path: Path,
    margin: int = DEFAULT_MARGIN,
) -> tuple[Image.Image | None, SheetReport | None]:
    sheet = Image.open(path).convert("RGBA")
    boxes = frame_boxes(sheet.size)
    if not boxes:
        return None, None

    frames = [sheet.crop(box) for box in boxes]
    before_counts = [sum(edge_pixel_counts(frame).values()) for frame in frames]
    touching_frames = sum(1 for count in before_counts if count)
    if not touching_frames:
        return None, None

    is_effect = "effects" in path.parts
    prepared: list[Image.Image] = []
    feathered_edges = 0
    for frame in frames:
        if is_effect:
            frame, count = soften_clipped_effect_edges(frame)
            feathered_edges += count
        prepared.append(frame)

    bboxes = [bbox for frame in prepared if (bbox := threshold_bbox(frame)) is not None]
    frame_size = prepared[0].size
    pivot = stable_pivot(bboxes, placement_mode(path), frame_size)
    scale, offset = choose_transform(bboxes, pivot, frame_size, margin)
    transformed = [transform_frame(frame, pivot, scale, offset) for frame in prepared]

    unsafe = [
        index for index, frame in enumerate(transformed) if visible_margin_count(frame, margin)
    ]
    if unsafe:
        raise ValueError(
            f"{path}: frame safety transform left visible pixels in the "
            f"{margin}px margin for frame(s) {', '.join(map(str, unsafe))}"
        )

    out = Image.new("RGBA", sheet.size, (0, 0, 0, 0))
    for frame, box in zip(transformed, boxes, strict=True):
        out.alpha_composite(frame, (box[0], box[1]))
    report = SheetReport(
        path=path,
        frame_size=frame_size,
        touching_frames_before=touching_frames,
        touching_pixels_before=sum(before_counts),
        feathered_frame_edges=feathered_edges,
        scale=scale,
        offset=offset,
    )
    return out, report


def refresh_effect_manifest(path: Path) -> None:
    if "effects" not in path.parts:
        return
    manifest_path = path.parent / "manifest.json"
    manifest = read_json_object(manifest_path)
    if not manifest:
        return

    if isinstance(manifest.get("sprites"), dict):
        sprites = manifest["sprites"]
        entry = sprites.get(path.stem)
        if not isinstance(entry, dict):
            return
        playback = str(entry.get("playback", "target"))
        anchor = str(entry.get("anchor", "center"))
        impact = entry.get("impactStartFrame")
        impact_start = int(impact) if isinstance(impact, (int, float)) else None
        sheet = Image.open(path).convert("RGBA")
        measured = measure_place_anchor(sheet, playback, anchor, impact_start)
        bounds = measure_place_bounds(sheet, playback, impact_start)
        if measured is not None:
            entry["placeAnchor"] = measured
        if bounds is not None:
            entry["placeBounds"] = bounds
        write_json_lf(manifest_path, manifest)
        return

    # Monster manifests describe the front sheet at the top level. A repaired
    # synthetic back layer does not change placement geometry.
    if path.name != "skill.png":
        return
    playback = str(manifest.get("playback", "target"))
    anchor = str(manifest.get("anchor", "center"))
    impact = manifest.get("impactStartFrame")
    impact_start = int(impact) if isinstance(impact, (int, float)) else None
    sheet = Image.open(path).convert("RGBA")
    measured = measure_place_anchor(sheet, playback, anchor, impact_start)
    bounds = measure_place_bounds(sheet, playback, impact_start)
    if measured is not None:
        manifest["placeAnchor"] = measured
    if bounds is not None:
        manifest["placeBounds"] = bounds
    write_json_lf(manifest_path, manifest)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Harden legacy 5x5 runtime sprite sheets against cell-edge clipping."
    )
    parser.add_argument("paths", nargs="*", type=Path, help="Specific PNG paths to inspect.")
    parser.add_argument(
        "--all-runtime",
        action="store_true",
        help="Inspect every browser-addressable companion and monster PNG.",
    )
    parser.add_argument(
        "--margin",
        type=int,
        default=DEFAULT_MARGIN,
        help=f"Required transparent frame margin in pixels (default: {DEFAULT_MARGIN}).",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write repaired PNGs and refresh effect placement manifests.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.margin < 2:
        raise SystemExit("--margin must be at least 2 pixels")
    selected = runtime_png_paths() if args.all_runtime else [path.resolve() for path in args.paths]
    if not selected:
        raise SystemExit("Pass one or more PNG paths or use --all-runtime")

    reports: list[SheetReport] = []
    for path in selected:
        resolved = path if path.is_absolute() else (ROOT / path)
        if not resolved.exists():
            raise SystemExit(f"Missing PNG: {resolved}")
        hardened, report = harden_sheet(resolved, margin=args.margin)
        if hardened is None or report is None:
            continue
        reports.append(report)
        if args.write:
            save_image_atomic(hardened, resolved, "PNG", optimize=True)
            refresh_effect_manifest(resolved)
        action = "repaired" if args.write else "would repair"
        relative = resolved.relative_to(ROOT)
        print(
            f"{action}: {relative} | frames={report.touching_frames_before} "
            f"pixels={report.touching_pixels_before} "
            f"featheredEdges={report.feathered_frame_edges} "
            f"scale={report.scale:.4f} offset={report.offset}"
        )

    action = "Repaired" if args.write else "Would repair"
    print(
        f"{action} {len(reports)} sheet(s); {len(selected) - len(reports)} already safe/unsupported."
    )


if __name__ == "__main__":
    main()
