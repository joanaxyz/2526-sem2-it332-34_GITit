#!/usr/bin/env python3
"""Build runtime monster spritesheets from aligned pose stills.

The monster manifests point battle sprites at root files such as
<monster>/idle.png, but the current generated assets live as stills under
<monster>/pose/raw. This script places each raw still onto a shared native-size
canvas with one left-foot anchor, writes the normalized still to
<monster>/pose/<pose>.png, copies that same single frame to <monster>/<pose>.png,
then updates the manifest frame size to match the output.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import deque
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_STORY_WORLDS = REPO_ROOT / "frontend" / "public" / "cosmetics" / "story-worlds"
DATA_STORY_WORLDS = REPO_ROOT / "frontend" / "src" / "shared" / "story-worlds"
POSES = ("idle", "attack", "hurt", "death")
DEFAULT_WORLDS = ("neon-backstreets", "frostbound-citadel")
NO_FEET_DEATH_ANCHORS = {
    ("frostbound-citadel", "frostveil-duchess"),
}
CENTER_BOTTOM_ANCHOR_MONSTERS = {
    ("frostbound-citadel", "twinmaw-direwolf"),
    ("frostbound-citadel", "whiteout-wyrm"),
}
SOURCE_ANCHOR_OVERRIDES = {
    ("frostbound-citadel", "glacier-smith", "idle"): (95, 401),
    ("frostbound-citadel", "glacier-smith", "attack"): (28, 372),
    ("frostbound-citadel", "glacier-smith", "hurt"): (59, 404),
    ("frostbound-citadel", "hoarfrost-geode-mimic", "death"): (199, 257),
    ("frostbound-citadel", "rimecaller", "hurt"): (222, 429),
    ("neon-backstreets", "bone-ghost", "idle"): (167, 511),
    ("neon-backstreets", "bone-ghost", "attack"): (197, 446),
    ("neon-backstreets", "bone-ghost", "hurt"): (276, 481),
    ("neon-backstreets", "bone-ghost", "death"): (288, 355),
    ("neon-backstreets", "bone-demon", "hurt"): (288, 401),
    ("neon-backstreets", "ghost-lady", "death"): (220, 241),
    ("neon-backstreets", "undead-clown", "hurt"): (196, 426),
    ("neon-backstreets", "floating-skull", "idle"): (164, 356),
    ("neon-backstreets", "floating-skull", "attack"): (149, 348),
    ("neon-backstreets", "floating-skull", "hurt"): (152, 335),
    ("neon-backstreets", "floating-skull", "death"): (307, 230),
    ("frostbound-citadel", "snow-wraith", "idle"): (207, 426),
    ("frostbound-citadel", "snow-wraith", "attack"): (68, 390),
    ("frostbound-citadel", "snow-wraith", "hurt"): (318, 412),
    ("frostbound-citadel", "snow-wraith", "death"): (280, 351),
    ("frostbound-citadel", "whiteout-wyrm", "idle"): (279, 393),
    ("frostbound-citadel", "whiteout-wyrm", "attack"): (183, 347),
    ("frostbound-citadel", "whiteout-wyrm", "hurt"): (237, 455),
    ("frostbound-citadel", "whiteout-wyrm", "death"): (258, 245),
    ("frostbound-citadel", "twinmaw-direwolf", "hurt"): (334, 360),
    ("frostbound-citadel", "twinmaw-direwolf", "death"): (311, 285),
}
PADDING_RATIO_OVERRIDES = {
    ("frostbound-citadel", "twinmaw-direwolf"): 0.18,
}
RENDERED_POSE_OFFSETS = {
    ("neon-backstreets", "floating-skull", "idle"): (0, -240),
    ("neon-backstreets", "floating-skull", "attack"): (0, -240),
    ("neon-backstreets", "floating-skull", "hurt"): (0, -240),
    ("neon-backstreets", "ghost-lady", "death"): (-12, 0),
}


@dataclass
class PoseSource:
    name: str
    path: Path
    image: Image.Image
    mask: Image.Image
    body_mask: Image.Image
    bbox: tuple[int, int, int, int]
    anchor: tuple[float, float]


@dataclass
class MonsterPlan:
    world: str
    slug: str
    asset_slug: str
    label: str
    frame_size: int
    display_scale: float
    anchor: tuple[int, int]
    poses: dict[str, PoseSource]


def image_data(im: Image.Image):
    if hasattr(im, "get_flattened_data"):
        return im.get_flattened_data()
    return im.getdata()


def silhouette_mask(im: Image.Image, threshold: int = 10) -> Image.Image:
    rgba = im.convert("RGBA")
    alpha = rgba.getchannel("A")
    alpha_bbox = alpha.point(lambda p: 255 if p > 8 else 0).getbbox()
    if alpha_bbox is not None and alpha_bbox != (0, 0, im.width, im.height):
        return alpha.point(lambda p: 255 if p > 8 else 0)

    rgb = im.convert("RGB")
    r, g, b = rgb.split()
    min_channel = ImageChops.darker(ImageChops.darker(r, g), b)
    mask = min_channel.point(lambda p: 255 if p < 255 - threshold else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return mask

    area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
    if area < im.width * im.height * 0.92:
        return mask

    return neutral_border_silhouette_mask(rgb)


def neutral_border_silhouette_mask(rgb: Image.Image) -> Image.Image:
    pixels = rgb.load()
    w, h = rgb.size
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
    seen = bytearray(w * h)
    queue: deque[tuple[int, int]] = deque()

    def idx(x: int, y: int) -> int:
        return y * w + x

    def is_bg(x: int, y: int) -> bool:
        r, g, b = pixels[x, y]
        return max(abs(r - bg[0]), abs(g - bg[1]), abs(b - bg[2])) <= tolerance

    def push(x: int, y: int) -> None:
        i = idx(x, y)
        if not seen[i] and is_bg(x, y):
            seen[i] = 1
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

    return Image.frombytes("L", (w, h), bytes(0 if v else 255 for v in seen))


def connected_components(mask: Image.Image) -> list[tuple[int, tuple[int, int, int, int]]]:
    w, h = mask.size
    scan_bbox = mask.getbbox()
    if scan_bbox is None:
        return []
    scan_left, scan_top, scan_right, scan_bottom = scan_bbox
    src = mask.load()
    seen = bytearray(w * h)
    components: list[tuple[int, tuple[int, int, int, int]]] = []

    def idx(x: int, y: int) -> int:
        return y * w + x

    for y in range(scan_top, scan_bottom):
        for x in range(scan_left, scan_right):
            i = idx(x, y)
            if seen[i] or not src[x, y]:
                continue
            seen[i] = 1
            queue: deque[tuple[int, int]] = deque([(x, y)])
            area = 0
            left = right = x
            top = bottom = y
            while queue:
                cx, cy = queue.popleft()
                area += 1
                left = min(left, cx)
                right = max(right, cx)
                top = min(top, cy)
                bottom = max(bottom, cy)
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if nx < 0 or ny < 0 or nx >= w or ny >= h:
                        continue
                    ni = idx(nx, ny)
                    if seen[ni] or not src[nx, ny]:
                        continue
                    seen[ni] = 1
                    queue.append((nx, ny))
            components.append((area, (left, top, right + 1, bottom + 1)))

    components.sort(reverse=True, key=lambda item: item[0])
    return components


def mask_from_bbox(mask: Image.Image, bbox: tuple[int, int, int, int]) -> Image.Image:
    out = Image.new("L", mask.size, 0)
    out.paste(mask.crop(bbox), bbox)
    return out


def body_mask_for_anchor(mask: Image.Image) -> Image.Image:
    components = connected_components(mask)
    if not components:
        return mask
    full_bbox = mask.getbbox()
    if full_bbox is None:
        return mask

    full_area = sum(area for area, _ in components)
    keep = [components[0][1]]
    largest_area = components[0][0]
    # Keep substantial detached pieces near the main body, but ignore projectiles
    # and sparkle trails that should not decide the foot anchor.
    main = components[0][1]
    main_cx = (main[0] + main[2]) / 2
    body_width = max(1, main[2] - main[0])
    for area, bbox in components[1:]:
        if area < max(18, largest_area * 0.035, full_area * 0.015):
            continue
        cx = (bbox[0] + bbox[2]) / 2
        if abs(cx - main_cx) <= body_width * 0.9:
            keep.append(bbox)

    out = Image.new("L", mask.size, 0)
    for bbox in keep:
        out.paste(mask.crop(bbox), bbox)
    return out


def row_segments(mask: Image.Image, y: int) -> list[tuple[int, int, int]]:
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
    return (segment[0] + segment[1]) / 2


def left_foot_anchor(mask: Image.Image) -> tuple[float, float]:
    """Return the screen-left planted/contact point for a pose.

    "Left foot" here means the foot/contact point on the left side of the image,
    not the character's anatomical left. The returned X is the left edge of that
    contact segment so all poses share the same screen-left foot origin.
    """
    bbox = mask.getbbox()
    if bbox is None:
        return (mask.width / 2, mask.height - 1)
    left, top, right, bottom = bbox
    width = max(1, right - left)
    height = max(1, bottom - top)
    lower_top = min(bottom - 1, top + round(height * 0.55))
    required_width = max(2, round(width * 0.015))
    side_limit = left + width * 0.58

    fallback: tuple[float, float] | None = None
    for y in range(bottom - 1, lower_top - 1, -1):
        segments = [seg for seg in row_segments(mask, y) if seg[2] >= required_width]
        if not segments:
            continue
        if fallback is None:
            seg = min(segments, key=segment_center)
            fallback = (seg[0], y)
        left_side = [seg for seg in segments if segment_center(seg) <= side_limit]
        if left_side:
            seg = min(left_side, key=segment_center)
            return (seg[0], y)

    if fallback is not None:
        return fallback
    return (left, bottom - 1)


def death_left_foot_anchor(mask: Image.Image) -> tuple[float, float]:
    """Return a foot-like lower-left anchor for fallen death poses.

    Death poses are often lying down, so the deepest screen-left contact can be
    a hand, shield, or weapon. Prefer the leftmost substantial lower-body
    segment instead, which keeps corpses aligned from the same side as idle's
    screen-left foot.
    """
    bbox = mask.getbbox()
    if bbox is None:
        return (mask.width / 2, mask.height - 1)

    left, top, right, bottom = bbox
    width = max(1, right - left)
    height = max(1, bottom - top)
    lower_top = min(bottom - 1, top + round(height * 0.58))
    required_width = max(3, round(width * 0.025))
    side_limit = left + width * 0.68
    candidates: list[tuple[int, int, tuple[int, int, int]]] = []

    for y in range(lower_top, bottom):
        for segment in row_segments(mask, y):
            if segment[2] < required_width:
                continue
            if segment_center(segment) > side_limit:
                continue
            candidates.append((segment[0], y, segment))

    if candidates:
        min_x = min(x for x, _, _ in candidates)
        x_slack = max(4, round(width * 0.04))
        near_left = [candidate for candidate in candidates if candidate[0] <= min_x + x_slack]
        _, y, segment = max(near_left, key=lambda candidate: (candidate[1], -segment_center(candidate[2])))
        return (segment[0], y)

    return left_foot_anchor(mask)


def no_feet_death_anchor(mask: Image.Image) -> tuple[float, float]:
    """Return a centered lower-body anchor for death poses with no visible feet."""
    bbox = mask.getbbox()
    if bbox is None:
        return (mask.width / 2, mask.height - 1)

    left, _top, right, bottom = bbox
    return ((left + right - 1) / 2, bottom - 1)


def center_bottom_anchor(mask: Image.Image) -> tuple[float, float]:
    """Return the centered lower footprint contact point for non-biped silhouettes."""
    bbox = mask.getbbox()
    if bbox is None:
        return (mask.width / 2, mask.height - 1)

    left, top, right, bottom = bbox
    width = max(1, right - left)
    height = max(1, bottom - top)
    lower_top = min(bottom - 1, top + round(height * 0.62))
    required_width = max(3, round(width * 0.018))
    contact_segments: list[tuple[int, int, int, int]] = []

    for y in range(lower_top, bottom):
        for start, end, segment_width in row_segments(mask, y):
            if segment_width >= required_width:
                contact_segments.append((start, end, segment_width, y))

    if not contact_segments:
        return no_feet_death_anchor(mask)

    deepest_y = max(y for *_segment, y in contact_segments)
    y_slack = max(3, round(height * 0.045))
    grounded = [segment for segment in contact_segments if segment[3] >= deepest_y - y_slack]
    contact_left = min(segment[0] for segment in grounded)
    contact_right = max(segment[1] for segment in grounded)
    return ((contact_left + contact_right) / 2, deepest_y)


def load_monster_data(world: str) -> dict:
    path = DATA_STORY_WORLDS / world / "data" / "monsters.json"
    return json.loads(path.read_text(encoding="utf-8"))


def displayed_frame_size_for(monster: dict) -> int:
    sizes = []
    for pose in POSES:
        sprite = monster.get("sprites", {}).get(pose, {})
        width = int(sprite.get("frameWidth") or 0)
        height = int(sprite.get("frameHeight") or 0)
        if width and height:
            display_scale = float(sprite.get("displayScale") or 1)
            sizes.append(round(max(width, height) * display_scale))
    return max(sizes or [256])


def asset_slug_for(monster: dict, fallback: str) -> str:
    sprites = monster.get("sprites", {})
    for pose in (*POSES, "portrait"):
        src = str(sprites.get(pose, {}).get("src") or "")
        marker = "/monsters/"
        if marker not in src:
            continue
        asset_slug = src.split(marker, 1)[1].split("/", 1)[0]
        if asset_slug:
            return asset_slug
    return fallback


def load_pose_sources(world: str, slug: str, asset_slug: str) -> dict[str, PoseSource]:
    pose_dir = PUBLIC_STORY_WORLDS / world / "monsters" / asset_slug / "pose"
    raw_dir = pose_dir / "raw"
    sources: dict[str, PoseSource] = {}
    for pose in POSES:
        path = raw_dir / f"{pose}.png"
        if not path.exists():
            path = pose_dir / f"{pose}.png"
        if not path.exists():
            continue
        image = Image.open(path).convert("RGB")
        mask = silhouette_mask(image)
        bbox = mask.getbbox()
        if bbox is None:
            continue
        body = body_mask_for_anchor(mask)
        anchor_override = SOURCE_ANCHOR_OVERRIDES.get((world, slug, pose))
        if anchor_override is not None:
            anchor = anchor_override
        elif (world, slug) in CENTER_BOTTOM_ANCHOR_MONSTERS:
            anchor = center_bottom_anchor(body)
        elif pose == "death" and (world, slug) in NO_FEET_DEATH_ANCHORS:
            anchor = no_feet_death_anchor(body)
        elif pose == "death":
            anchor = death_left_foot_anchor(body)
        else:
            anchor = left_foot_anchor(body)
        sources[pose] = PoseSource(pose, path, image, mask, body, bbox, anchor)
    return sources


def plan_monster(world: str, slug: str, monster: dict, padding_ratio: float) -> MonsterPlan | None:
    asset_slug = asset_slug_for(monster, slug)
    poses = load_pose_sources(world, slug, asset_slug)
    if "idle" not in poses:
        return None
    displayed_frame_size = displayed_frame_size_for(monster)
    effective_padding_ratio = max(padding_ratio, PADDING_RATIO_OVERRIDES.get((world, slug), padding_ratio))
    padding = max(24, round(displayed_frame_size * effective_padding_ratio))

    min_rel_x = math.inf
    max_rel_x = -math.inf
    min_rel_y = math.inf
    max_rel_y = -math.inf
    for source in poses.values():
        left, top, right, bottom = source.bbox
        ax, ay = source.anchor
        min_rel_x = min(min_rel_x, left - ax)
        max_rel_x = max(max_rel_x, right - 1 - ax)
        min_rel_y = min(min_rel_y, top - ay)
        max_rel_y = max(max_rel_y, bottom - 1 - ay)

    content_w = max(1.0, max_rel_x - min_rel_x + 1)
    content_h = max(1.0, max_rel_y - min_rel_y + 1)
    frame_size = math.ceil(max(content_w, content_h) + padding * 2)
    if frame_size % 2:
        frame_size += 1

    anchor_x = round(((frame_size - content_w) / 2) - min_rel_x)
    anchor_y = round(frame_size - padding - max_rel_y)
    display_scale = displayed_frame_size / frame_size

    return MonsterPlan(
        world=world,
        slug=slug,
        asset_slug=asset_slug,
        label=str(monster.get("label") or slug),
        frame_size=frame_size,
        display_scale=display_scale,
        anchor=(anchor_x, anchor_y),
        poses=poses,
    )


def render_pose_frame(plan: MonsterPlan, source: PoseSource) -> Image.Image:
    frame = Image.new("RGB", (plan.frame_size, plan.frame_size), (255, 255, 255))
    left, top, right, bottom = source.bbox
    crop = source.image.crop(source.bbox)
    crop_mask = source.mask.crop(source.bbox)
    paste_x = round(plan.anchor[0] + left - source.anchor[0])
    paste_y = round(plan.anchor[1] + top - source.anchor[1])
    frame.paste(crop, (paste_x, paste_y), crop_mask)
    if (plan.world, plan.slug, source.name) in SOURCE_ANCHOR_OVERRIDES:
        return apply_rendered_pose_offset(plan, source, frame)
    if (plan.world, plan.slug) in CENTER_BOTTOM_ANCHOR_MONSTERS:
        return apply_rendered_pose_offset(plan, source, frame)
    if source.name == "death":
        return apply_rendered_pose_offset(plan, source, frame)
    return apply_rendered_pose_offset(plan, source, align_rendered_frame_to_anchor(frame, plan.anchor))


def apply_rendered_pose_offset(plan: MonsterPlan, source: PoseSource, frame: Image.Image) -> Image.Image:
    dx, dy = RENDERED_POSE_OFFSETS.get((plan.world, plan.slug, source.name), (0, 0))
    return shift_frame(frame, dx, dy)


def rendered_left_foot_anchor(frame: Image.Image) -> tuple[float, float] | None:
    mask = silhouette_mask(frame)
    if mask.getbbox() is None:
        return None
    return left_foot_anchor(body_mask_for_anchor(mask))


def shift_frame(frame: Image.Image, dx: int, dy: int) -> Image.Image:
    if dx == 0 and dy == 0:
        return frame

    out = Image.new("RGB", frame.size, (255, 255, 255))
    w, h = frame.size
    src_left = max(0, -dx)
    src_top = max(0, -dy)
    src_right = min(w, w - dx) if dx >= 0 else w
    src_bottom = min(h, h - dy) if dy >= 0 else h
    if src_right <= src_left or src_bottom <= src_top:
        return out
    out.paste(frame.crop((src_left, src_top, src_right, src_bottom)), (src_left + dx, src_top + dy))
    return out


def align_rendered_frame_to_anchor(frame: Image.Image, target: tuple[int, int]) -> Image.Image:
    # Cropping detached effects can change which lower segment becomes the
    # detected left foot. Do a final pass on the actual output frame and nudge it
    # into place without resizing the source pixels.
    for _ in range(2):
        actual = rendered_left_foot_anchor(frame)
        if actual is None:
            return frame
        dx = round(target[0] - actual[0])
        dy = round(target[1] - actual[1])
        if dx == 0 and dy == 0:
            return frame
        frame = shift_frame(frame, dx, dy)
    return frame


def visible_bbox(frame: Image.Image) -> tuple[int, int, int, int] | None:
    return silhouette_mask(frame).getbbox()


def draw_review_cell(frame: Image.Image, plan: MonsterPlan, pose: str) -> Image.Image:
    cell_w = 220
    label_h = 36
    scale = min((cell_w - 12) / frame.width, (cell_w - label_h - 12) / frame.height)
    shown = frame.resize((round(frame.width * scale), round(frame.height * scale)), Image.Resampling.NEAREST)
    cell = Image.new("RGB", (cell_w, cell_w), (248, 250, 252))
    draw = ImageDraw.Draw(cell)
    draw.text((6, 5), f"{pose} {frame.width}x{frame.height}", fill=(17, 24, 39))
    x0 = (cell_w - shown.width) // 2
    y0 = label_h + (cell_w - label_h - shown.height) // 2
    cell.paste(shown, (x0, y0))

    anchor_x = x0 + plan.anchor[0] * scale
    anchor_y = y0 + plan.anchor[1] * scale
    draw.line((anchor_x, y0, anchor_x, y0 + shown.height), fill=(239, 68, 68), width=1)
    draw.line((x0, anchor_y, x0 + shown.width, anchor_y), fill=(239, 68, 68), width=1)
    draw.ellipse((anchor_x - 3, anchor_y - 3, anchor_x + 3, anchor_y + 3), outline=(185, 28, 28), width=2)

    bbox = visible_bbox(frame)
    if bbox is not None:
        bx0, by0, bx1, by1 = bbox
        draw.rectangle(
            (
                x0 + bx0 * scale,
                y0 + by0 * scale,
                x0 + (bx1 - 1) * scale,
                y0 + (by1 - 1) * scale,
            ),
            outline=(14, 165, 233),
            width=1,
        )
    return cell


def build_review(plans: list[MonsterPlan], rendered: dict[tuple[str, str, str], Image.Image], path: Path) -> None:
    row_h = 242
    label_w = 180
    cell_w = 220
    width = label_w + cell_w * len(POSES)
    height = max(1, row_h * len(plans))
    review = Image.new("RGB", (width, height), (229, 236, 244))
    draw = ImageDraw.Draw(review)

    for row, plan in enumerate(plans):
        y = row * row_h
        draw.rectangle((0, y, width, y + row_h - 1), fill=(238, 242, 247))
        draw.text((10, y + 14), f"{plan.world}", fill=(75, 85, 99))
        draw.text((10, y + 34), plan.slug, fill=(17, 24, 39))
        draw.text((10, y + 54), plan.label, fill=(17, 24, 39))
        draw.text((10, y + 82), f"display {plan.display_scale:.3f}", fill=(75, 85, 99))
        draw.text((10, y + 102), f"anchor {plan.anchor[0]},{plan.anchor[1]}", fill=(75, 85, 99))
        for col, pose in enumerate(POSES):
            frame = rendered.get((plan.world, plan.slug, pose))
            if frame is None:
                continue
            review.paste(draw_review_cell(frame, plan, pose), (label_w + col * cell_w, y + 10))

    path.parent.mkdir(parents=True, exist_ok=True)
    review.save(path)


def write_plan_outputs(plan: MonsterPlan, dry_run: bool) -> dict[tuple[str, str, str], Image.Image]:
    rendered: dict[tuple[str, str, str], Image.Image] = {}
    monster_dir = PUBLIC_STORY_WORLDS / plan.world / "monsters" / plan.asset_slug
    pose_dir = monster_dir / "pose"
    if not dry_run:
        pose_dir.mkdir(parents=True, exist_ok=True)

    for pose in POSES:
        source = plan.poses.get(pose)
        if source is None:
            continue
        frame = render_pose_frame(plan, source)
        rendered[(plan.world, plan.slug, pose)] = frame
        if dry_run:
            continue
        frame.save(pose_dir / f"{pose}.png")
        frame.save(monster_dir / f"{pose}.png")
    return rendered


def update_manifest(world: str, plans: list[MonsterPlan], dry_run: bool) -> None:
    if dry_run:
        return

    path = DATA_STORY_WORLDS / world / "data" / "monsters.json"
    data = load_monster_data(world)
    by_slug = {plan.slug: plan for plan in plans if plan.world == world}
    changed = False

    for slug, plan in by_slug.items():
        monster = data.get(slug)
        if not monster:
            continue
        sprites = monster.get("sprites", {})
        for pose in (*POSES, "portrait"):
            sprite = sprites.get(pose)
            if not sprite:
                continue
            sprite["frameWidth"] = plan.frame_size
            sprite["frameHeight"] = plan.frame_size
            sprite["columns"] = 1
            sprite["rows"] = 1
            sprite["frameCount"] = 1
            sprite["fps"] = 1
            sprite["displayScale"] = round(plan.display_scale, 6)
            changed = True

    if changed:
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build monster pose sheets from raw stills.")
    parser.add_argument("--world", action="append", choices=DEFAULT_WORLDS, help="World to process. Repeatable.")
    parser.add_argument("--monster", action="append", help="Only process the named monster slug. Repeatable.")
    parser.add_argument("--dry-run", action="store_true", help="Create the review only; do not write PNG outputs.")
    parser.add_argument("--padding-ratio", type=float, default=0.08, help="Frame padding as a ratio of frame size.")
    parser.add_argument(
        "--review-out",
        type=Path,
        default=REPO_ROOT / "tmp" / "monster-pose-sheet-left-foot-review.png",
        help="Path for the silhouette review image.",
    )
    args = parser.parse_args()

    worlds = tuple(args.world or DEFAULT_WORLDS)
    selected_monsters = set(args.monster or [])
    plans: list[MonsterPlan] = []
    rendered: dict[tuple[str, str, str], Image.Image] = {}

    for world in worlds:
        monsters = load_monster_data(world)
        for slug, monster in monsters.items():
            if selected_monsters and slug not in selected_monsters:
                continue
            plan = plan_monster(world, slug, monster, args.padding_ratio)
            if plan is None:
                print(f"skip {world}/{slug}: no idle source")
                continue
            plans.append(plan)
            rendered.update(write_plan_outputs(plan, args.dry_run))
            print(
                f"{world}/{slug}: frame={plan.frame_size} displayScale={plan.display_scale:.6f} "
                f"anchor={plan.anchor[0]},{plan.anchor[1]}"
            )
        update_manifest(world, plans, args.dry_run)

    build_review(plans, rendered, args.review_out)
    print(f"review={args.review_out}")


if __name__ == "__main__":
    main()
