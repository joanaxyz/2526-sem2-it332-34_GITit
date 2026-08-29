from pathlib import Path

from PIL import Image

from scripts.assets.remove_sprite_white_background import (
    SpriteTask,
    clean_png,
    enclosed_transparent_mask,
    enclosed_white_mask,
)


def donut_source(size: tuple[int, int] = (8, 8)) -> Image.Image:
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    for y in range(1, 7):
        for x in range(1, 7):
            image.putpixel((x, y), (40, 50, 60, 255))
    for y in range(3, 5):
        for x in range(3, 5):
            image.putpixel((x, y), (0, 0, 0, 0))
    return image


def test_enclosed_transparent_mask_excludes_exterior() -> None:
    image = donut_source()

    mask = enclosed_transparent_mask(
        image,
        alpha_threshold=0,
        min_hole_size=4,
        grid_columns=1,
        grid_rows=1,
    )

    assert sum(mask) == 4
    assert mask[3 * image.width + 3] == 1
    assert mask[0] == 0


def test_enclosed_white_mask_excludes_exterior_white() -> None:
    image = donut_source()
    for y in range(3, 5):
        for x in range(3, 5):
            image.putpixel((x, y), (255, 255, 255, 255))
    image.putpixel((0, 0), (255, 255, 255, 255))

    mask = enclosed_white_mask(
        image,
        tolerance=18,
        alpha_threshold=0,
        min_hole_size=4,
        grid_columns=1,
        grid_rows=1,
    )

    assert sum(mask) == 4
    assert mask[3 * image.width + 3] == 1
    assert mask[0] == 0


def test_restore_alpha_holes_preserves_destination_art(tmp_path: Path) -> None:
    source_path = tmp_path / "raw" / "idle.png"
    destination_path = tmp_path / "idle.png"
    source_path.parent.mkdir()
    donut_source().save(source_path)
    Image.new("RGBA", (8, 8), (120, 80, 40, 255)).save(destination_path)
    task = SpriteTask(
        source=source_path,
        destination=destination_path,
        raw_path=source_path,
        stage_action=None,
    )

    result = clean_png(
        task,
        tolerance=18,
        alpha_threshold=0,
        mode="connected",
        min_hole_size=0,
        hole_fringe_radius=0,
        min_transparent_hole_size=4,
        hole_fringe_min_rgb=205,
        hole_fringe_min_luma=225,
        hole_fringe_max_chroma=30,
        grid_columns=1,
        grid_rows=1,
        restore_alpha_holes=True,
        clean_current_white_holes=False,
        edge_defringe=False,
        edge_defringe_radius=1,
        dry_run=False,
    )

    with Image.open(destination_path) as restored:
        rgba = restored.convert("RGBA")
        assert rgba.getpixel((3, 3))[3] == 0
        assert rgba.getpixel((1, 1)) == (120, 80, 40, 255)
        assert rgba.getpixel((0, 0)) == (120, 80, 40, 255)

    assert result.removed_pixels == 4

    second_result = clean_png(
        task,
        tolerance=18,
        alpha_threshold=0,
        mode="connected",
        min_hole_size=0,
        hole_fringe_radius=0,
        min_transparent_hole_size=4,
        hole_fringe_min_rgb=205,
        hole_fringe_min_luma=225,
        hole_fringe_max_chroma=30,
        grid_columns=1,
        grid_rows=1,
        restore_alpha_holes=True,
        clean_current_white_holes=False,
        edge_defringe=False,
        edge_defringe_radius=1,
        dry_run=False,
    )

    with Image.open(destination_path) as restored:
        assert restored.convert("RGBA").getpixel((1, 1)) == (120, 80, 40, 255)

    assert second_result.removed_pixels == 0
    assert second_result.wrote is False


def test_clean_current_white_holes_preserves_destination_art(tmp_path: Path) -> None:
    source_path = tmp_path / "raw" / "idle.png"
    destination_path = tmp_path / "idle.png"
    source_path.parent.mkdir()
    Image.new("RGBA", (8, 8), (10, 20, 30, 255)).save(source_path)
    destination = donut_source()
    for y in range(3, 5):
        for x in range(3, 5):
            destination.putpixel((x, y), (255, 255, 255, 255))
    destination.save(destination_path)
    task = SpriteTask(
        source=source_path,
        destination=destination_path,
        raw_path=source_path,
        stage_action=None,
    )

    result = clean_png(
        task,
        tolerance=18,
        alpha_threshold=0,
        mode="connected",
        min_hole_size=4,
        hole_fringe_radius=0,
        min_transparent_hole_size=4,
        hole_fringe_min_rgb=205,
        hole_fringe_min_luma=225,
        hole_fringe_max_chroma=30,
        grid_columns=1,
        grid_rows=1,
        restore_alpha_holes=False,
        clean_current_white_holes=True,
        edge_defringe=False,
        edge_defringe_radius=1,
        dry_run=False,
    )

    with Image.open(destination_path) as cleaned:
        rgba = cleaned.convert("RGBA")
        assert rgba.getpixel((3, 3))[3] == 0
        assert rgba.getpixel((1, 1)) == (40, 50, 60, 255)
        assert rgba.getpixel((0, 0))[3] == 0

    assert result.removed_pixels == 4


def test_clean_current_connected_white_preserves_destination_art(tmp_path: Path) -> None:
    source_path = tmp_path / "raw" / "idle.png"
    destination_path = tmp_path / "idle.png"
    source_path.parent.mkdir()
    Image.new("RGBA", (8, 8), (200, 40, 80, 255)).save(source_path)

    destination = donut_source()
    destination.putpixel((0, 0), (255, 255, 255, 255))
    destination.putpixel((3, 3), (255, 255, 255, 255))
    destination.save(destination_path)
    task = SpriteTask(
        source=source_path,
        destination=destination_path,
        raw_path=source_path,
        stage_action=None,
    )

    result = clean_png(
        task,
        tolerance=18,
        alpha_threshold=0,
        mode="connected",
        min_hole_size=0,
        hole_fringe_radius=0,
        min_transparent_hole_size=4,
        hole_fringe_min_rgb=205,
        hole_fringe_min_luma=225,
        hole_fringe_max_chroma=30,
        grid_columns=1,
        grid_rows=1,
        restore_alpha_holes=False,
        clean_current_white_holes=False,
        edge_defringe=False,
        edge_defringe_radius=1,
        dry_run=False,
        clean_current_connected_white=True,
    )

    with Image.open(destination_path) as cleaned:
        rgba = cleaned.convert("RGBA")
        assert rgba.getpixel((0, 0))[3] == 0
        assert rgba.getpixel((3, 3)) == (255, 255, 255, 255)
        assert rgba.getpixel((1, 1)) == (40, 50, 60, 255)

    assert result.removed_pixels == 1
    assert result.cleaned_current_connected_white is True
