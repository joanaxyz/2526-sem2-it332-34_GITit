#!/usr/bin/env python3
"""Crop and palette-optimize runtime actor sprite sheets without frame jitter.

Every animation for one actor receives the same frame crop, calculated from
the union of visible pixels across all actions and grid cells. Frame order,
frame count, and grid layout are preserved. Portraits, skill effects, raw
sources, and non-animated images are intentionally excluded.

The command is a dry run unless ``--apply`` is supplied.

Requires Pillow:
    python -m pip install --user Pillow
"""

from __future__ import annotations

import argparse
import io
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "frontend" / "public"
COMPANION_DATA = ROOT / "frontend" / "src" / "shared" / "cosmetics" / "companions" / "data"
STORY_DATA = ROOT / "frontend" / "src" / "shared" / "story-worlds"
DEFAULT_ALPHA_THRESHOLD = 8
DEFAULT_PADDING = 2
DEFAULT_COLORS = 256


@dataclass
class SpriteEntry:
    action: str
    path: Path
    descriptor: dict[str, Any]


@dataclass
class Actor:
    name: str
    manifest_path: Path
    metrics: dict[str, Any]
    sprites: list[SpriteEntry]


@dataclass(frozen=True)
class ActorPlan:
    actor: Actor
    frame_size: tuple[int, int]
    grid: tuple[int, int]
    crop: tuple[int, int, int, int]
    idle_bbox: tuple[int, int, int, int] | None

    @property
    def compact_frame_size(self) -> tuple[int, int]:
        left, top, right, bottom = self.crop
        return right - left, bottom - top


def animated_entries(sprites: dict[str, Any]) -> list[SpriteEntry]:
    entries: list[SpriteEntry] = []
    for action, value in sprites.items():
        if not isinstance(value, dict):
            continue
        columns = int(value.get("columns", 1))
        rows = int(value.get("rows", 1))
        src = str(value.get("src", ""))
        if columns * rows <= 1 or not src.startswith("/cosmetics/"):
            continue
        if "/effects/" in src or "/raw/" in src:
            continue
        path = (PUBLIC / src.removeprefix("/")).resolve()
        if not path.is_relative_to(PUBLIC.resolve()):
            raise ValueError(f"Actor sheet escapes public root: {src}")
        entries.append(SpriteEntry(action=action, path=path, descriptor=value))
    return entries


def load_actors() -> tuple[list[Actor], dict[Path, dict[str, Any]]]:
    actors: list[Actor] = []
    documents: dict[Path, dict[str, Any]] = {}

    for path in sorted(COMPANION_DATA.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not isinstance(payload.get("sprites"), dict):
            continue
        documents[path] = payload
        entries = animated_entries(payload["sprites"])
        if entries:
            actors.append(
                Actor(
                    name=f"companion/{payload.get('id', path.stem)}",
                    manifest_path=path,
                    metrics=payload.setdefault("metrics", {}),
                    sprites=entries,
                )
            )

    for path in sorted(STORY_DATA.glob("*/data/monsters.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            continue
        documents[path] = payload
        world = path.parents[1].name
        for slug, monster in payload.items():
            if not isinstance(monster, dict) or not isinstance(monster.get("sprites"), dict):
                continue
            entries = animated_entries(monster["sprites"])
            if entries:
                actors.append(
                    Actor(
                        name=f"{world}/{slug}",
                        manifest_path=path,
                        metrics=monster.setdefault("metrics", {}),
                        sprites=entries,
                    )
                )

    return actors, documents


def combine_bbox(
    current: tuple[int, int, int, int] | None,
    candidate: tuple[int, int, int, int] | None,
) -> tuple[int, int, int, int] | None:
    if candidate is None:
        return current
    if current is None:
        return candidate
    return (
        min(current[0], candidate[0]),
        min(current[1], candidate[1]),
        max(current[2], candidate[2]),
        max(current[3], candidate[3]),
    )


def visible_bbox(frame: Image.Image, alpha_threshold: int) -> tuple[int, int, int, int] | None:
    alpha = frame.getchannel("A").point(lambda value: 255 if value > alpha_threshold else 0)
    return alpha.getbbox()


def plan_actor(actor: Actor, alpha_threshold: int, padding: int) -> ActorPlan:
    shapes = {
        (
            int(sprite.descriptor["frameWidth"]),
            int(sprite.descriptor["frameHeight"]),
            int(sprite.descriptor["columns"]),
            int(sprite.descriptor["rows"]),
        )
        for sprite in actor.sprites
    }
    if len(shapes) != 1:
        raise ValueError(f"{actor.name} uses inconsistent actor-sheet grids: {sorted(shapes)}")
    frame_width, frame_height, columns, rows = shapes.pop()

    union: tuple[int, int, int, int] | None = None
    idle_bbox: tuple[int, int, int, int] | None = None
    for sprite in actor.sprites:
        if not sprite.path.is_file():
            raise ValueError(f"Missing actor sheet: {sprite.path.relative_to(ROOT)}")
        with Image.open(sprite.path) as opened:
            expected_size = (frame_width * columns, frame_height * rows)
            if opened.size != expected_size:
                raise ValueError(
                    f"{sprite.path.relative_to(ROOT)} is {opened.size}, expected {expected_size}"
                )
            sheet = opened.convert("RGBA")
            for row in range(rows):
                for column in range(columns):
                    frame = sheet.crop(
                        (
                            column * frame_width,
                            row * frame_height,
                            (column + 1) * frame_width,
                            (row + 1) * frame_height,
                        )
                    )
                    bbox = visible_bbox(frame, alpha_threshold)
                    union = combine_bbox(union, bbox)
                    if sprite.action == "idle":
                        idle_bbox = combine_bbox(idle_bbox, bbox)

    if union is None:
        raise ValueError(f"{actor.name} has no visible pixels")
    # Pillow fills an out-of-bounds crop with transparency. Do not clamp here:
    # a source whose visible pixels reach an old cell edge still needs the same
    # safety margin as every other actor.
    crop = (
        union[0] - padding,
        union[1] - padding,
        union[2] + padding,
        union[3] + padding,
    )
    return ActorPlan(
        actor=actor,
        frame_size=(frame_width, frame_height),
        grid=(columns, rows),
        crop=crop,
        idle_bbox=idle_bbox,
    )


def compact_sheet(
    plan: ActorPlan,
    sprite: SpriteEntry,
    colors: int,
    alpha_threshold: int,
) -> bytes:
    frame_width, frame_height = plan.frame_size
    columns, rows = plan.grid
    compact_width, compact_height = plan.compact_frame_size
    with Image.open(sprite.path) as opened:
        source = opened.convert("RGBA")
        # Palette quantization can otherwise promote a barely visible alpha
        # value into the visible range. Normalize the same values that the crop
        # planner deliberately treats as transparent.
        alpha = source.getchannel("A").point(lambda value: 0 if value <= alpha_threshold else value)
        source.putalpha(alpha)
        output = Image.new(
            "RGBA",
            (compact_width * columns, compact_height * rows),
            (0, 0, 0, 0),
        )
        for row in range(rows):
            for column in range(columns):
                frame = source.crop(
                    (
                        column * frame_width,
                        row * frame_height,
                        (column + 1) * frame_width,
                        (row + 1) * frame_height,
                    )
                ).crop(plan.crop)
                output.alpha_composite(frame, (column * compact_width, row * compact_height))

    encoded: Image.Image = output
    if colors:
        encoded = output.quantize(
            colors=colors,
            method=Image.Quantize.FASTOCTREE,
            dither=Image.Dither.FLOYDSTEINBERG,
        )
    buffer = io.BytesIO()
    encoded.save(buffer, format="PNG", optimize=True, compress_level=9)
    return buffer.getvalue()


def write_atomic(path: Path, payload: bytes) -> None:
    temporary = path.with_suffix(".compacted.tmp.png")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def update_actor_metadata(plan: ActorPlan) -> None:
    compact_width, compact_height = plan.compact_frame_size
    for sprite in plan.actor.sprites:
        sprite.descriptor["frameWidth"] = compact_width
        sprite.descriptor["frameHeight"] = compact_height

    if plan.idle_bbox is not None:
        # Pixel-bound anchoring normally measures this in the browser. Keeping
        # the fallback synchronized avoids a first-frame vertical jump.
        plan.actor.metrics["foot_offset"] = max(1, plan.crop[3] - plan.idle_bbox[3])


def write_documents(documents: dict[Path, dict[str, Any]]) -> None:
    for path, payload in documents.items():
        temporary = path.with_suffix(".compacted.tmp.json")
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
        os.replace(temporary, path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="write compacted sheets and descriptors"
    )
    parser.add_argument(
        "--actor",
        action="append",
        default=[],
        help="only process this actor name; repeatable",
    )
    parser.add_argument("--alpha-threshold", type=int, default=DEFAULT_ALPHA_THRESHOLD)
    parser.add_argument("--padding", type=int, default=DEFAULT_PADDING)
    parser.add_argument(
        "--colors",
        type=int,
        default=DEFAULT_COLORS,
        help="PNG palette colors; use 0 for lossless RGBA output (default: 256)",
    )
    args = parser.parse_args()
    if not 0 <= args.alpha_threshold <= 254:
        parser.error("--alpha-threshold must be between 0 and 254")
    if args.padding < 0:
        parser.error("--padding must be non-negative")
    if args.colors not in {0, *range(2, 257)}:
        parser.error("--colors must be 0 or between 2 and 256")
    return args


def main() -> int:
    args = parse_args()
    actors, documents = load_actors()
    selected = set(args.actor)
    if selected:
        known = {actor.name for actor in actors}
        unknown = selected - known
        if unknown:
            raise SystemExit(f"Unknown actor(s): {', '.join(sorted(unknown))}")
        actors = [actor for actor in actors if actor.name in selected]

    before_total = 0
    after_total = 0
    sheet_count = 0
    for actor in actors:
        plan = plan_actor(actor, args.alpha_threshold, args.padding)
        compact_width, compact_height = plan.compact_frame_size
        actor_before = 0
        actor_after = 0
        payloads: list[tuple[SpriteEntry, bytes]] = []
        for sprite in actor.sprites:
            payload = compact_sheet(plan, sprite, args.colors, args.alpha_threshold)
            payloads.append((sprite, payload))
            actor_before += sprite.path.stat().st_size
            actor_after += len(payload)
        if args.apply:
            for sprite, payload in payloads:
                write_atomic(sprite.path, payload)
            update_actor_metadata(plan)

        before_total += actor_before
        after_total += actor_after
        sheet_count += len(actor.sprites)
        old_width, old_height = plan.frame_size
        print(
            f"{actor.name}: {len(actor.sprites)} sheets, "
            f"frame {old_width}x{old_height} -> {compact_width}x{compact_height}, "
            f"{actor_before:,} -> {actor_after:,} bytes"
        )

    if args.apply:
        write_documents(documents)
    savings = before_total - after_total
    ratio = savings / before_total if before_total else 0
    action = "Compacted" if args.apply else "Would compact"
    print(
        f"{action} {sheet_count} actor sheets for {len(actors)} actors: "
        f"{before_total:,} -> {after_total:,} bytes ({ratio:.1%} smaller)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
