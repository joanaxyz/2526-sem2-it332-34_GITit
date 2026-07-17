from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw


sys.path.insert(0, str(Path(__file__).resolve().parent))

from process_companion_spell_sheets import (  # noqa: E402
    CroppedPixelError,
    FRAME,
    FRAMES,
    GROUND_ANCHOR_Y,
    apply_registration_plan,
    clamp_registration_shifts,
    clear_frame_edges,
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


def test_registration_damps_one_frame_spike_without_flattening_motion() -> None:
    shifts = [(0, 0), (8, 2), (54, -38), (16, 6), (24, 8)]

    stabilized = stabilize_registration_shifts(shifts, "target")

    # The authored rising trajectory remains, while the isolated third-frame
    # correction is pulled close enough to its neighbours to stop camera shake.
    assert stabilized[2] == (36, -20)
    assert max(
        max(abs(stabilized[index][axis] - stabilized[index - 1][axis]) for axis in (0, 1))
        for index in range(1, len(stabilized))
    ) < 46


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
