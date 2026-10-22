from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))

import process_companion_spell_sheets as processor  # noqa: E402
from process_companion_spell_sheets import (  # noqa: E402
    FRAME,
    FRAMES,
    GROUND_ANCHOR_Y,
    CroppedPixelError,
    apply_registration_plan,
    clamp_registration_shifts,
    clear_detected_bright_grid_lines,
    clear_frame_edges,
    content_axis_edges,
    compute_prefit_scale,
    compute_registration_plan,
    measure_place_bounds,
    owned_frame_sources,
    stabilize_registration_shifts,
)


def effect_frame(box: tuple[int, int, int, int]) -> Image.Image:
    frame = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rectangle(box, fill=(80, 190, 255, 255))
    return frame


def test_projectile_registration_uses_authored_phases_and_feet_impact() -> None:
    frames = [effect_frame((92, 94, 164, 158)) for _ in range(FRAMES)]

    _scale, shifts, debug = compute_registration_plan(
        frames,
        "projectile",
        "feet",
        launch_start=3,
        impact_start=16,
    )

    # The generated README says frames 1-3 charge, 4-16 fly, and 17-25
    # impact at ground. Registration must use those exact zero-based cuts.
    assert "until frame 2" in debug.mode
    assert "through frame 15" in debug.mode
    assert "feet anchor" in debug.mode
    # The robust 94th-percentile base (y=155 for this solid test block) is
    # shifted onto the shared ground line, not the old cell-centre pivot.
    assert abs((155 + shifts[16][1]) - GROUND_ANCHOR_Y) <= 1


def test_place_bounds_measure_only_projectile_impact_frames() -> None:
    sheet = Image.new("RGBA", (FRAME * 5, FRAME * 5), (0, 0, 0, 0))
    for index in range(FRAMES):
        frame = effect_frame((10, 90, 80, 150) if index < 16 else (90, 80, 180, 170))
        sheet.alpha_composite(frame, ((index % 5) * FRAME, (index // 5) * FRAME))

    bounds = measure_place_bounds(sheet, "projectile", impact_start=16)

    assert bounds is not None
    assert bounds["left"] > 0.3
    assert bounds["right"] < 0.75


def test_edge_cleanup_fails_instead_of_slicing_visible_pixels() -> None:
    frame = effect_frame((0, 80, 30, 120))

    with pytest.raises(CroppedPixelError, match="edge cleanup would clear"):
        clear_frame_edges(frame, "test frame")


def test_registration_clamps_translation_without_shrinking_art() -> None:
    frame = effect_frame((20, 20, 235, 245))
    original_bbox = frame.getchannel("A").getbbox()
    original_alpha = sum(frame.getchannel("A").getdata())

    shifts = clamp_registration_shifts([frame], [(70, 70)])
    registered = apply_registration_plan([frame], 1.0, shifts, "test registration")[0]

    assert shifts[0] != (70, 70)
    assert registered.getchannel("A").getbbox() is not None
    registered_bbox = registered.getchannel("A").getbbox()
    assert original_bbox is not None and registered_bbox is not None
    assert registered_bbox[2] - registered_bbox[0] == original_bbox[2] - original_bbox[0]
    assert registered_bbox[3] - registered_bbox[1] == original_bbox[3] - original_bbox[1]
    assert sum(registered.getchannel("A").getdata()) == original_alpha


def test_sheet_wide_connected_component_is_partitioned_by_source_cell(tmp_path: Path) -> None:
    sheet = Image.new("RGBA", (FRAME * 5, FRAME * 5), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)
    for column in range(5):
        x = column * FRAME
        draw.rectangle((x + 42, 80, x + 214, 176), fill=(80, 190, 255, 255))
    # Simulate glow/noise connecting otherwise independent frames across seams.
    draw.line((42, 128, FRAME * 5 - 42, 128), fill=(80, 190, 255, 255), width=3)
    raw_path = tmp_path / "connected.png"
    sheet.save(raw_path)

    sources = owned_frame_sources(raw_path)
    scale = compute_prefit_scale(sources)

    # The old whole-component ownership gave one frame an almost sheet-wide
    # bbox and reduced all 25 frames to roughly 10% size.
    assert scale >= 0.89
    assert all(
        source.source_bbox is None or source.source_bbox[2] - source.source_bbox[0] <= FRAME + 4
        for source in sources
    )


@pytest.mark.parametrize("transpose", [False, True], ids=["rows", "columns"])
def test_drifting_frames_keep_their_tips_when_a_glow_connects_the_row(
    tmp_path: Path, transpose: bool
) -> None:
    sheet = Image.new("RGBA", (FRAME * 5, FRAME * 5), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)
    for column in range(5):
        x = column * FRAME
        # The third row starts above its nominal y=512 boundary, as in White's
        # Mergetool. A shared flare joins all five frames into one component.
        draw.rectangle((x + 64, 490, x + 192, 650), fill=(80, 190, 255, 255))
    draw.line((64, 560, FRAME * 5 - 64, 560), fill=(80, 190, 255, 255), width=3)
    if transpose:
        sheet = sheet.transpose(Image.Transpose.TRANSPOSE)
    raw_path = tmp_path / "drifting.png"
    sheet.save(raw_path)

    sources = owned_frame_sources(raw_path)

    for cell in range(5):
        owner = cell * 5 + 2 if transpose else 10 + cell
        previous = owner - (1 if transpose else 5)
        assert sources[previous].image is None
        bbox = sources[owner].source_bbox
        assert bbox is not None
        axis = 0 if transpose else 1
        assert bbox[axis] <= 490
        assert bbox[axis + 2] >= 651
        # Keep the authored grid for normalization instead of resizing each
        # frame to its newly detected, potentially unequal ownership cell.
        assert sources[owner].cell_box[axis] == FRAME * 2


def test_ownership_seams_stay_on_grid_without_a_clearer_gutter() -> None:
    import numpy as np

    alpha = np.full((FRAME * 5, FRAME * 5), 255, dtype=np.uint8)

    assert content_axis_edges(alpha, axis=0, count=5) == list(range(0, FRAME * 5 + 1, FRAME))
    assert content_axis_edges(alpha, axis=1, count=5) == list(range(0, FRAME * 5 + 1, FRAME))


@pytest.mark.parametrize("companion", ["blue", "white"])
def test_detached_dragon_mouth_flash_stays_in_its_own_frame(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, companion: str
) -> None:
    monkeypatch.setattr(processor, "COMPANION_SLUG", companion)
    monkeypatch.setattr(processor, "BACKGROUND_MODE", "chroma-key")
    sheet = Image.new("RGBA", (1254, 1254), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((70, 800, 226, 900), fill=(60, 160, 255, 255))
    draw.polygon([(254, 829), (280, 855), (254, 881), (230, 855)], fill=(245, 245, 255, 255))
    # Another row's art obscures the mouth flash's gutter in a sheet-wide
    # projection. A row-local seam must keep all four spark tips with frame 16.
    draw.rectangle((260, 50, 310, 200), fill=(60, 160, 255, 255))
    raw_path = tmp_path / "rm.png"
    sheet.save(raw_path)

    sources = owned_frame_sources(raw_path)

    source = sources[15]
    assert source.image is not None and source.source_bbox is not None
    for x, y in [(254, 831), (278, 855), (254, 879), (232, 855)]:
        assert source.image.getpixel((x - source.source_bbox[0], y - source.source_bbox[1]))[3] > 200
    assert sources[16].image is None


def shipped_spell_frame(companion: str, name: str, index: int) -> Image.Image:
    effect_set = str(processor.COMPANION_EFFECT_SETS[companion]["effectSet"])
    path = processor.COMPANION_ROOT / companion / "effects" / effect_set / f"{name}.png"
    col, row = index % 5, index // 5
    with Image.open(path) as sheet:
        return sheet.crop((col * FRAME, row * FRAME, (col + 1) * FRAME, (row + 1) * FRAME))


@pytest.mark.parametrize(
    ("companion", "name", "index", "region"),
    [
        ("blue", "rm", 16, (0, 0, 46, FRAME)),
        ("blue", "merge", 16, (0, 205, FRAME, FRAME)),
        ("blue", "merge", 20, (0, 245, 10, FRAME)),
        ("black", "commit", 0, (0, 235, FRAME, FRAME)),
        ("black", "branch", 15, (0, 200, FRAME, FRAME)),
        ("black", "branch", 16, (0, 200, FRAME, FRAME)),
        ("black", "branch", 17, (0, 200, FRAME, FRAME)),
        ("black", "remote_front", 15, (0, 235, FRAME, FRAME)),
        ("black", "remote_back", 15, (0, 240, FRAME, FRAME)),
    ],
)
def test_shipped_spells_have_no_reported_neighbor_fragments(
    companion: str, name: str, index: int, region: tuple[int, int, int, int]
) -> None:
    # These regions contained the reported side/bottom artifacts. Check the
    # tracked runtime PNGs, so CI also catches a stale or faulty asset rebake.
    alpha = shipped_spell_frame(companion, name, index).crop(region).getchannel("A")

    assert alpha.point(lambda value: 255 if value > 12 else 0).getbbox() is None


def test_white_clone_retains_five_centered_fade_poses_without_the_extra_sixth_pose() -> None:
    for index in range(20, 25):
        alpha = shipped_spell_frame("white", "clone", index).getchannel("A")
        bbox = alpha.point(lambda value: 255 if value > 12 else 0).getbbox()

        assert bbox is not None
        left, _top, right, _bottom = bbox
        assert abs((left + right) / 2 - FRAME / 2) <= 16
        assert right - left < 200


def test_generated_bright_grid_is_removed_without_deleting_effect_highlights() -> None:
    sheet = Image.new("RGBA", (FRAME * 5, FRAME * 5), (236, 0, 220, 255))
    draw = ImageDraw.Draw(sheet)
    for separator in range(0, FRAME * 5 + 1, FRAME):
        coordinate = min(FRAME * 5 - 1, separator)
        draw.line(
            (0, max(0, coordinate - 3), FRAME * 5 - 1, max(0, coordinate - 3)),
            fill=(250, 120, 240, 255),
            width=1,
        )
        draw.line(
            (max(0, coordinate - 3), 0, max(0, coordinate - 3), FRAME * 5 - 1),
            fill=(250, 120, 240, 255),
            width=1,
        )
        draw.line((0, coordinate, FRAME * 5 - 1, coordinate), fill=(255, 255, 255, 255), width=2)
        draw.line((coordinate, 0, coordinate, FRAME * 5 - 1), fill=(255, 255, 255, 255), width=2)
    draw.ellipse((90, 90, 166, 166), fill=(245, 250, 255, 255))

    cleaned = clear_detected_bright_grid_lines(sheet)

    assert cleaned.getpixel((FRAME, FRAME // 2))[3] == 0
    assert cleaned.getpixel((FRAME // 2, FRAME))[3] == 0
    assert cleaned.getpixel((FRAME - 3, FRAME // 2))[3] == 0
    assert cleaned.getpixel((FRAME // 2, FRAME - 3))[3] == 0
    assert cleaned.getpixel((128, 128))[3] == 255


def test_local_bright_streak_does_not_trigger_grid_removal() -> None:
    sheet = Image.new("RGBA", (FRAME * 5, FRAME * 5), (236, 0, 220, 255))
    draw = ImageDraw.Draw(sheet)
    draw.line((FRAME - 4, 80, FRAME - 4, 180), fill=(255, 255, 255, 255), width=2)

    cleaned = clear_detected_bright_grid_lines(sheet)

    assert cleaned.getpixel((FRAME - 4, 128))[3] == 255


def test_registration_damps_one_frame_spike_without_flattening_motion() -> None:
    shifts = [(0, 0), (8, 2), (54, -38), (16, 6), (24, 8)]

    stabilized = stabilize_registration_shifts(shifts, "target")

    # The authored rising trajectory remains, while the isolated third-frame
    # correction is pulled close enough to its neighbours to stop camera shake.
    assert stabilized[2] == (36, -20)
    assert (
        max(
            max(abs(stabilized[index][axis] - stabilized[index - 1][axis]) for axis in (0, 1))
            for index in range(1, len(stabilized))
        )
        < 46
    )


def test_registration_never_smooths_across_projectile_phase_boundaries() -> None:
    shifts = [(0, 0), (0, 0), (60, 20), (60, 20), (-40, -12), (-40, -12)]

    stabilized = stabilize_registration_shifts(
        shifts,
        "projectile",
        launch_start=2,
        impact_start=4,
    )

    assert stabilized == shifts


def test_projectile_flight_keeps_exact_horizontal_axis() -> None:
    shifts = [(0, 0), (8, 5), (16, -18), (24, 22), (32, -12), (40, 4)]

    stabilized = stabilize_registration_shifts(
        shifts,
        "projectile",
        launch_start=2,
        impact_start=5,
    )

    # Frames 2-4 are the flight phase. Their vertical corrections must remain
    # exact so the registered nose cannot bob, even while x is de-jittered.
    assert [dy for _, dy in stabilized[2:5]] == [-18, 22, -12]
