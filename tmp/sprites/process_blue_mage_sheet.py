from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source.png"
OUT_SHEET = ROOT / "blue_mage_8frame_64x64_sheet.png"
OUT_PREVIEW = ROOT / "blue_mage_8frame_64x64_sheet_preview_8x.png"
OUT_CONTACT = ROOT / "blue_mage_8frame_contact.png"

FRAME_W = 64
FRAME_H = 64
FRAME_COUNT = 8


def is_key(r: int, g: int, b: int) -> bool:
    # The generated chroma key is green, but edge pixels vary from pure key
    # green into pale/dark green. Remove green-dominant pixels while preserving
    # cyan spell effects and yellow hit marks.
    return (g >= 35 and g >= r + 12 and g >= b + 12) or (g >= 185 and r <= 120 and b <= 130)


def alpha_from_green(source: Image.Image) -> Image.Image:
    rgba = source.convert("RGBA")
    px = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = px[x, y]
            if is_key(r, g, b):
                px[x, y] = (0, 0, 0, 0)
            elif a != 255:
                px[x, y] = (r, g, b, 255)
    return rgba


def content_bbox(img: Image.Image) -> tuple[int, int, int, int]:
    alpha = img.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        raise ValueError("No non-transparent pixels found")
    return bbox


def crop_by_window(img: Image.Image, x0: int, x1: int) -> Image.Image:
    strip = img.crop((x0, 0, x1, img.height))
    bbox = content_bbox(strip)
    return strip.crop(bbox)


def normalize_frame(crop: Image.Image, *, max_w: int, max_h: int, y_pad: int = 3) -> Image.Image:
    w, h = crop.size
    scale = min(max_w / w, max_h / h)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    sprite = crop.resize((new_w, new_h), Image.Resampling.NEAREST)

    frame = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    x = (FRAME_W - new_w) // 2
    y = FRAME_H - y_pad - new_h
    if new_h >= FRAME_H:
        y = 0
    frame.alpha_composite(sprite, (x, y))
    return frame


def make_preview(sheet: Image.Image, scale: int = 8) -> Image.Image:
    preview = Image.new("RGBA", (sheet.width, sheet.height), (28, 28, 34, 255))
    preview.alpha_composite(sheet, (0, 0))
    # Add subtle cell dividers in the preview only; the final sheet has none.
    for x in range(0, sheet.width + 1, FRAME_W):
        for y in range(sheet.height):
            if 0 <= x < sheet.width:
                preview.putpixel((x, y), (255, 255, 255, 70))
    return preview.resize((sheet.width * scale, sheet.height * scale), Image.Resampling.NEAREST)


def main() -> None:
    src = Image.open(SOURCE)
    rgba = alpha_from_green(src)

    # Hand-checked source windows around the eight generated poses, left-to-right.
    # They intentionally include detached spell sparks/effects where they belong.
    windows = [
        (5, 190),      # idle
        (205, 445),    # run A
        (450, 660),    # run B
        (665, 870),    # miss / failed cast
        (880, 1065),   # cast windup
        (1068, 1360),  # cast release
        (1358, 1515),  # hurt
        (1535, 1765),  # death
    ]

    frames: list[Image.Image] = []
    for index, (x0, x1) in enumerate(windows):
        crop = crop_by_window(rgba, x0, x1)
        # Cast release and death are wider poses; preserve more horizontal action.
        max_w = 62 if index in {5, 7} else 56
        max_h = 56 if index != 7 else 42
        y_pad = 3 if index != 7 else 8
        frames.append(normalize_frame(crop, max_w=max_w, max_h=max_h, y_pad=y_pad))

    sheet = Image.new("RGBA", (FRAME_W * FRAME_COUNT, FRAME_H), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        sheet.alpha_composite(frame, (i * FRAME_W, 0))

    sheet.save(OUT_SHEET)
    make_preview(sheet).save(OUT_PREVIEW)

    contact = Image.new("RGBA", (FRAME_W * FRAME_COUNT, FRAME_H * 2), (28, 28, 34, 255))
    contact.alpha_composite(sheet, (0, 0))
    contact.alpha_composite(make_preview(sheet, scale=1), (0, FRAME_H))
    contact.save(OUT_CONTACT)

    print(f"sheet={OUT_SHEET}")
    print(f"preview={OUT_PREVIEW}")
    print(f"contact={OUT_CONTACT}")
    print(f"size={sheet.width}x{sheet.height}")


if __name__ == "__main__":
    main()
