"""Post-process image-generated monster skill-effect sheets.

Inputs:
  frontend/public/cosmetics/story-worlds/arcane-spire/monsters/<slug>/effects/_raw/skill.png

Outputs:
  frontend/public/cosmetics/story-worlds/arcane-spire/monsters/<slug>/effects/skill.png
  optional generated back layer:
    frontend/public/cosmetics/story-worlds/arcane-spire/monsters/<slug>/effects/skill-back.png
  per-monster manifest/diagnostics and a roster preview contact sheet

The heavy lifting intentionally reuses the Blue skill-effect processor: chroma
key removal, frame slicing, 256px normalization, and stable projectile/target
registration all stay in one implementation.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from process_companion_spell_sheets import (
    CroppedPixelError,
    FIT_MARGIN_PX,
    FRAME,
    FRAMES,
    FPS,
    GRID_COLUMNS,
    GRID_ROWS,
    frame_diagnostics,
    make_sheet,
    measure_place_anchor,
    measure_place_bounds,
    write_json_lf,
)


ROOT = Path(__file__).resolve().parents[2]
MONSTER_ROOT = ROOT / "frontend" / "public" / "cosmetics" / "story-worlds" / "arcane-spire" / "monsters"
PREVIEW_PATH = MONSTER_ROOT / "_skill-effects-preview.jpg"
PROJECTILE_SCALE = 0.6
PROJECTILE_FIT_MARGIN = 16

MONSTERS: list[dict[str, object]] = [
    {"slug": "monster-01", "label": "Bone Archer", "playback": "projectile", "motif": "blue flaming arrow", "scale": PROJECTILE_SCALE, "durationMs": 520, "anchor": "feet", "motion": "charge", "launchStartFrame": 5, "impactStartFrame": 20},
    {"slug": "monster-02", "label": "Bone Blacksmith", "playback": "target", "motif": "blue flame ground crack", "scale": 0.82, "durationMs": 780, "anchor": "feet"},
    {"slug": "monster-03", "label": "Bone Demon", "playback": "projectile", "motif": "blue flaming meteor", "scale": PROJECTILE_SCALE, "durationMs": 660, "anchor": "feet", "motion": "charge", "launchStartFrame": 5, "impactStartFrame": 20},
    {"slug": "monster-04", "label": "Bone Ghost", "playback": "projectile", "motif": "blue flame ghost skull", "scale": PROJECTILE_SCALE, "durationMs": 600, "anchor": "center", "motion": "charge", "launchStartFrame": 5, "impactStartFrame": 20},
    {"slug": "monster-05", "label": "Bone Lancer", "playback": "target", "motif": "blue flame pierce", "scale": 0.78, "durationMs": 720, "anchor": "feet"},
    {"slug": "monster-06", "label": "Bone Necromancer", "playback": "target", "motif": "skeleton hands", "scale": 0.84, "durationMs": 860, "anchor": "feet"},
    {"slug": "monster-07", "label": "Bone Soldier", "playback": "target", "motif": "blue flame slash", "scale": 0.72, "durationMs": 680},
    {"slug": "monster-08", "label": "Cursed Lantern", "playback": "target", "motif": "blue flame spin", "scale": 0.78, "durationMs": 760, "placement": "caster"},
    {"slug": "monster-09", "label": "Floating Skull", "playback": "target", "motif": "blue flame rain", "scale": 0.86, "durationMs": 880, "anchor": "feet"},
    {"slug": "monster-10", "label": "Ghost Lady", "playback": "target", "motif": "blue flame chains", "scale": 0.84, "durationMs": 900, "anchor": "feet", "backLayer": True},
    {"slug": "monster-11", "label": "Lich King", "playback": "target", "motif": "blue flame stab", "scale": 0.9, "durationMs": 920, "anchor": "feet", "backLayer": True},
    {"slug": "monster-12", "label": "Two Headed Hound", "playback": "target", "motif": "blue wolf fang bite", "scale": 0.74, "durationMs": 700},
    {"slug": "monster-13", "label": "Undead Clown", "playback": "projectile", "motif": "carnival curse bomb", "scale": PROJECTILE_SCALE, "durationMs": 620, "anchor": "center", "motion": "charge", "launchStartFrame": 5, "impactStartFrame": 20},
    {"slug": "monster-14", "label": "Undead Siren", "playback": "target", "motif": "blue flame water orb", "scale": 0.86, "durationMs": 900, "backLayer": True},
    {"slug": "monster-15", "label": "Zombe Boy", "playback": "target", "motif": "blue zombie bite", "scale": 0.62, "durationMs": 660},
]


def sprite_entry(src: str) -> dict[str, object]:
    return {
        "src": src,
        "fps": FPS,
        "loops": False,
        "frameWidth": FRAME,
        "frameHeight": FRAME,
        "columns": GRID_COLUMNS,
        "rows": GRID_ROWS,
        "frameCount": FRAMES,
    }


def tint_back_layer(front: Image.Image) -> Image.Image:
    """Create a soft lower aura/fissure layer from the registered front sheet."""
    out = Image.new("RGBA", front.size, (0, 0, 0, 0))
    for index in range(FRAMES):
        col = index % GRID_COLUMNS
        row = index // GRID_COLUMNS
        box = (col * FRAME, row * FRAME, (col + 1) * FRAME, (row + 1) * FRAME)
        frame = front.crop(box).convert("RGBA")
        alpha = frame.getchannel("A")
        glow_alpha = alpha.filter(ImageFilter.GaussianBlur(3.2))
        glow_alpha = ImageEnhance.Brightness(glow_alpha).enhance(0.62)
        glow = Image.new("RGBA", (FRAME, FRAME), (58, 255, 204, 0))
        glow.putalpha(glow_alpha)
        smoke = Image.new("RGBA", (FRAME, FRAME), (92, 36, 156, 0))
        smoke_alpha = alpha.filter(ImageFilter.GaussianBlur(7.0))
        smoke_alpha = ImageEnhance.Brightness(smoke_alpha).enhance(0.34)
        smoke.putalpha(smoke_alpha)
        layer = Image.alpha_composite(smoke, glow)
        out.alpha_composite(layer, (col * FRAME, row * FRAME))
    return out


def process_monster(spec: dict[str, object]) -> dict[str, object]:
    slug = str(spec["slug"])
    playback = str(spec["playback"])
    anchor = str(spec.get("anchor", "center"))
    effect_dir = MONSTER_ROOT / slug / "effects"
    raw_path = effect_dir / "_raw" / "skill.png"
    out_path = effect_dir / "skill.png"
    if not raw_path.exists():
        raise SystemExit(f"Missing raw generated sheet for {slug}: {raw_path}")

    effect_dir.mkdir(parents=True, exist_ok=True)
    launch_start = int(spec["launchStartFrame"]) if "launchStartFrame" in spec else None
    impact_start = int(spec["impactStartFrame"]) if "impactStartFrame" in spec else None
    diagnostics: dict[str, object] = {
        "front": make_sheet(
            raw_path,
            out_path,
            playback,
            anchor,
            launch_start,
            impact_start,
            fit_margin=PROJECTILE_FIT_MARGIN if playback == "projectile" else FIT_MARGIN_PX,
        )
    }
    layers = [
        {
            **sprite_entry(f"/cosmetics/story-worlds/arcane-spire/monsters/{slug}/effects/skill.png"),
            "layer": "front",
            "scale": spec["scale"],
            "opacity": 1,
            "offset_x": 0,
            "offset_y": 0,
            "orient_to": "travel" if playback == "projectile" else "target-facing",
        }
    ]

    if spec.get("backLayer"):
        front = Image.open(out_path).convert("RGBA")
        back = tint_back_layer(front)
        back_path = effect_dir / "skill-back.png"
        back.save(back_path, optimize=True)
        diagnostics["back"] = frame_diagnostics(back, playback)
        layers.insert(
            0,
            {
                **sprite_entry(f"/cosmetics/story-worlds/arcane-spire/monsters/{slug}/effects/skill-back.png"),
                "layer": "back",
                "scale": round(float(spec["scale"]) * 1.08, 3),
                "opacity": 0.82,
                "offset_x": 0,
                "offset_y": 14,
                "orient_to": "target-facing",
            },
        )

    manifest = {
        "id": f"{slug}-skill-effect",
        "label": f"{spec['label']} Skill Effect",
        "motif": spec["motif"],
        "playback": playback,
        "durationMs": spec["durationMs"],
        "frameWidth": FRAME,
        "frameHeight": FRAME,
        "columns": GRID_COLUMNS,
        "rows": GRID_ROWS,
        "frameCount": FRAMES,
        "fps": FPS,
        "layers": layers,
        "anchor": anchor,
    }
    if "motion" in spec:
        manifest["motion"] = spec["motion"]
    if "launchStartFrame" in spec:
        manifest["launchStartFrame"] = spec["launchStartFrame"]
    if "impactStartFrame" in spec:
        manifest["impactStartFrame"] = spec["impactStartFrame"]
    measured = measure_place_anchor(
        Image.open(out_path).convert("RGBA"),
        playback,
        anchor,
        int(spec["impactStartFrame"]) if "impactStartFrame" in spec else None,
    )
    if measured is not None:
        manifest["placeAnchor"] = measured
    bounds = measure_place_bounds(Image.open(out_path).convert("RGBA"), playback, impact_start)
    if bounds is not None:
        manifest["placeBounds"] = bounds
    if playback == "target":
        manifest["placement"] = spec.get("placement", "target")
    write_json_lf(effect_dir / "manifest.json", manifest)
    write_json_lf(effect_dir / "_diagnostics.json", diagnostics)
    return manifest


def make_preview(manifests: list[dict[str, object]]) -> None:
    tile_w = 250
    tile_h = 174
    cols = 5
    rows = math.ceil(len(manifests) / cols)
    preview = Image.new("RGBA", (cols * tile_w, rows * tile_h), (9, 10, 18, 255))
    draw = ImageDraw.Draw(preview)
    font = ImageFont.load_default()

    for index, manifest in enumerate(manifests):
        slug = str(manifest["id"]).removesuffix("-skill-effect")
        x = (index % cols) * tile_w
        y = (index // cols) * tile_h
        sheet = Image.open(MONSTER_ROOT / slug / "effects" / "skill.png").convert("RGBA")
        frame_index = 12
        col = frame_index % GRID_COLUMNS
        row = frame_index // GRID_COLUMNS
        frame = sheet.crop((col * FRAME, row * FRAME, (col + 1) * FRAME, (row + 1) * FRAME)).resize(
            (120, 120),
            Image.Resampling.LANCZOS,
        )
        preview.alpha_composite(frame, (x + 64, y + 10))
        draw.text((x + 12, y + 136), slug, fill=(226, 246, 255), font=font)
        draw.text((x + 12, y + 152), str(manifest["motif"])[:32], fill=(112, 220, 214), font=font)

    preview.convert("RGB").save(PREVIEW_PATH, quality=92, optimize=True)


def main() -> None:
    manifests = [process_monster(spec) for spec in MONSTERS]
    write_json_lf(
        MONSTER_ROOT / "_skill-effects-manifest.json",
        {
            "id": "arcane-spire-monster-skill-effects",
            "frameWidth": FRAME,
            "frameHeight": FRAME,
            "columns": GRID_COLUMNS,
            "rows": GRID_ROWS,
            "frameCount": FRAMES,
            "fps": FPS,
            "monsters": {str(spec["slug"]): manifest for spec, manifest in zip(MONSTERS, manifests)},
        },
    )
    make_preview(manifests)


if __name__ == "__main__":
    try:
        main()
    except CroppedPixelError as exc:
        raise SystemExit(str(exc)) from None
