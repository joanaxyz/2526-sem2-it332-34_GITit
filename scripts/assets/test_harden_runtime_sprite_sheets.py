from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))

from harden_runtime_sprite_sheets import (  # noqa: E402
    DEFAULT_MARGIN,
    GRID_COLUMNS,
    GRID_ROWS,
    edge_pixel_counts,
    frame_boxes,
    harden_sheet,
    soften_clipped_effect_edges,
    visible_margin_count,
)


def build_sheet(path: Path, *, touch_both_sides: bool) -> None:
    frame = 64
    sheet = Image.new(
        "RGBA",
        (frame * GRID_COLUMNS, frame * GRID_ROWS),
        (0, 0, 0, 0),
    )
    for index, box in enumerate(frame_boxes(sheet.size)):
        cell = Image.new("RGBA", (frame, frame), (0, 0, 0, 0))
        draw = ImageDraw.Draw(cell)
        if touch_both_sides:
            draw.ellipse((-8, 14, frame + 8, 58), fill=(80, 190, 255, 255))
        else:
            draw.ellipse((12, 14, 52, 58), fill=(80, 190, 255, 255))
        sheet.alpha_composite(cell, (box[0], box[1]))
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)


def test_safe_sheet_is_left_untouched(tmp_path: Path) -> None:
    path = tmp_path / "actor" / "idle.png"
    build_sheet(path, touch_both_sides=False)

    hardened, report = harden_sheet(path)

    assert hardened is None
    assert report is None


def test_shared_transform_clears_every_frame_margin(tmp_path: Path) -> None:
    path = tmp_path / "monsters" / "monster-01" / "effects" / "skill.png"
    build_sheet(path, touch_both_sides=True)

    hardened, report = harden_sheet(path)

    assert hardened is not None
    assert report is not None
    assert report.touching_frames_before == 25
    assert report.feathered_frame_edges == 50
    for box in frame_boxes(hardened.size):
        frame = hardened.crop(box)
        assert visible_margin_count(frame, DEFAULT_MARGIN) == 0


def test_strong_effect_cut_is_feathered_but_actor_logic_can_skip_it() -> None:
    frame = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rectangle((0, 16, 30, 48), fill=(120, 220, 255, 255))

    softened, edge_count = soften_clipped_effect_edges(frame)

    assert edge_count == 1
    assert edge_pixel_counts(frame)["left"] > 0
    assert softened.getpixel((0, 32))[3] == 0
    assert 0 < softened.getpixel((12, 32))[3] < 128
    assert softened.getpixel((24, 32))[3] == 255
