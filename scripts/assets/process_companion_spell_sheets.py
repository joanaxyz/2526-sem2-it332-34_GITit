"""Post-process image-generated companion spell-effect sheets.

Inputs:
  frontend/public/cosmetics/companion/<slug>/effects/<effect-set>/_raw/<name>.png

Outputs:
  frontend/public/cosmetics/companion/<slug>/effects/<effect-set>/<name>.png
  frontend/public/cosmetics/companion/<slug>/effects/<effect-set>/manifest.json
  frontend/public/cosmetics/companion/<slug>/effects/<effect-set>/_preview-contact-sheet.jpg

Companions do not all have raw generated art for every command. Blue has a
complete raw sheet per command, so a missing file is an error there. Black's
spells are intentionally smooth VFX, not pixel art, and only some commands
have raw generated sheets so far; a command with no raw sheet is simply
skipped rather than assumed to exist, and its existing manifest/diagnostics
entry (however it was produced) is left untouched. Do not add code here that
assumes every companion's raw sheets are deterministically, fully generated
up front — check `REQUIRE_COMPLETE_RAW_COVERAGE`.

Important animation note:
  This script does NOT merely center each frame by its visible bounding box.
  Bounding-box centering makes VFX swim because sparks, trails, rings, and flame
  tongues change the silhouette on every frame.

  Instead, every frame is registered to the same runtime pivot that the frontend
  uses to place the effect. Target effects use one stable sequence anchor.
  Projectile effects use a leading nose anchor while the sprite is flying, then
  switch to the cell center for the impact/fade frames because the runtime also
  settles projectiles to their center near impact.

  Fade-out frames are intentionally aligned to their own remaining visible
  pixels. The old guardrail reused/interpolated neighboring shifts for weak
  frames, but that left tiny late sparks/rings away from the pivot and made many
  animations snap at the end. Empty frames still inherit a nearby shift because
  they have no visual pixels to register.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import NamedTuple

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[2]
COMPANION_ROOT = ROOT / "frontend" / "public" / "cosmetics" / "companion"
OUT_DIR = COMPANION_ROOT / "blue" / "effects" / "skill-flames-25"
RAW_DIR = OUT_DIR / "_raw"
FRAME = 256
GRID_COLUMNS = 5
GRID_ROWS = 5
FRAMES = GRID_COLUMNS * GRID_ROWS
FPS = 18

# How much of the outer edge to force transparent after processing each cell.
# Image generators often leave 1-2 px of keyed color at the cell boundary, which
# can become visible seams in sprite-sheet renderers.
EDGE_CLEAR_PX = 2

# Some generated effects are drawn larger than one cell, so a naive crop clips
# the effect at the frame edge. After registration every effect is uniformly
# scaled about the cell centre so its widest frame fits inside the cell with this
# much clear margin, guaranteeing nothing is cut off. Layers share one fit scale.
FIT_MARGIN_PX = 12

# Alpha threshold used for finding the actual effect body.
ALPHA_THRESHOLD = 12

# If the detected anchor is wildly wrong because a frame is nearly empty, do not
# allow an extreme correction to throw the whole effect across the cell.
MAX_REGISTRATION_SHIFT = 96

# Frames below this confidence are usually fade-out frames: only a thin ring,
# a few remaining sparks, or weak smoke remains. They still get registered to
# the pivot, but the confidence is useful for diagnostics and for choosing the
# stable sequence anchor from stronger frames.
MIN_RELIABLE_ANCHOR_WEIGHT_RATIO = 0.25
MIN_RELIABLE_ANCHOR_PIXEL_RATIO = 0.08

# Keep these in sync with effectRegistry.ts. The script bakes the art so the
# runtime's placement anchors hit the intended pixels rather than a changing
# brightness centroid.
PROJECTILE_HAND_ANCHOR = (FRAME * 0.5, FRAME * 0.5)
PROJECTILE_FLIGHT_ANCHOR = (FRAME * 0.78, FRAME * 0.52)
PROJECTILE_SETTLE_ANCHOR = (FRAME * 0.5, FRAME * 0.5)
PROJECTILE_LAUNCH_START_FRAME = 10
PROJECTILE_SETTLE_START_FRAME = 20  # zero-based; visible frame 21 starts impact/dissipate

# Feet-anchored (ground-rooted) effects plant their visible base on this line so
# the runtime can sit them on the enemy's ground line. The matching runtime
# anchor is FEET_ANCHOR in effectRegistry.ts. Ground-rooted risers grow upward
# from here; a top margin keeps tall effects from clipping the cell, and tall
# sequences are uniformly scaled down to fit (see register_feet_sequence).
GROUND_ANCHOR_Y = FRAME * 0.86
FEET_TOP_MARGIN = FRAME * 0.05
# Robust base/top percentiles so a few stray high sparks or low embers do not
# define the planted edge.
FEET_BASE_PERCENTILE = 0.94
FEET_TOP_PERCENTILE = 0.05

# Playback classifications were re-derived by inspecting the actual generated art
# frame-by-frame (see the _preview contact sheets), not assumed from the command
# name. Three motions matter for rendering:
#   projectile - charge frames 0-9 gather at the caster's hand, then the spell
#       flies out and impacts the enemy. init/add additionally use the
#       gather-orb-projectile motion; the rest are plain fly-outs.
#   target     - plays on the enemy. anchor "center" sits on the body; anchor
#       "feet" is a ground-rooted riser (tornado, geyser, crystal bloom, rune
#       ring on the floor) whose base must plant on the enemy's ground line so it
#       does not float on the enemy's head.
#   ground     - rooted on the floor and travels along it from caster to enemy
#       (push shockwave, switch cresting wave). Always feet-anchored.
# A few commands were generated with genuinely different anchoring per companion,
# so those diverging cases live in COMPANION_COMMAND_OVERRIDES below.
# Authoritative playback buckets specified by the designer:
#   projectile-impact: add, branch, checkout, clone, default, init, merge,
#       reflog, stash, diff  -> charge at the hand, fly out, impact the monster.
#   ground-run: push, switch -> planted on the floor, run along it to the monster.
#   everything else: target  -> played centered on the monster.
# Both projectile impacts and target-centered effects are sized/placed against the
# monster's rendered box at runtime (see useBattleDirector), so a big boss gets a
# proportionally bigger effect than a small mob.
# The `anchor` field only applies to `target` playback and splits it into the two
# motions that were previously conflated (which made target effects appear to come
# from the ground, fall from above, or sit centered at random - see the contact
# sheet). It is classified by inspecting the actual generated art:
#   center - an aura, ring, or burst that plays ON the monster body (scan orb,
#       attune reticle, commit down-strike, weld flash, counter ring, ...). Baked to
#       the cell centre and planted with the runtime CENTER_ANCHOR on the body.
#   feet   - a ground-rooted riser that grows up from the floor (root flame,
#       tornado, beacon, ladder, ...). Baked with its base on the ground line and
#       planted on the monster's ground point. `ground` playback is always feet.
# Projectiles use hand/nose pivots during flight; `anchor` controls where the
# impact/dissipate frames pin after landing.
COMMANDS = [
    {
        "name": "init",
        "tint": "cyan",
        "motif": "ignite",
        "playback": "projectile",
        "anchor": "feet",
        "launchStartFrame": 10,
        "impactStartFrame": 15,
    },
    {
        "name": "clone",
        "tint": "azure",
        "motif": "mirror",
        "playback": "projectile",
        "anchor": "feet",
        "impactStartFrame": 15,
    },
    {"name": "status", "tint": "steel", "motif": "scan", "playback": "target", "anchor": "center"},
    {"name": "config", "tint": "indigo", "motif": "attune", "playback": "target", "anchor": "center"},
    {"name": "log", "tint": "steel", "motif": "chronicle", "playback": "target", "anchor": "center"},
    {"name": "show", "tint": "azure", "motif": "reveal", "playback": "target", "anchor": "feet"},
    {"name": "diff", "tint": "cyan", "motif": "compare", "playback": "projectile", "anchor": "center", "impactStartFrame": 15},
    {
        "name": "add",
        "tint": "cyan",
        "motif": "gather",
        "playback": "projectile",
        "anchor": "feet",
        "launchStartFrame": 3,
        "impactStartFrame": 16,
    },
    {"name": "commit", "tint": "azure", "motif": "commit", "playback": "target", "anchor": "feet"},
    {"name": "rm", "tint": "steel", "motif": "excise", "playback": "projectile", "anchor": "center", "impactStartFrame": 16},
    {"name": "check-ignore", "tint": "ash", "motif": "ward", "playback": "target", "anchor": "feet"},
    {"name": "restore", "tint": "cyan", "motif": "mend", "playback": "target", "anchor": "feet"},
    {"name": "branch", "tint": "cyan", "motif": "fork", "playback": "projectile", "anchor": "feet", "impactStartFrame": 19},
    {"name": "switch", "tint": "cyan", "motif": "switch", "playback": "ground", "anchor": "feet"},
    {"name": "checkout", "tint": "steel", "motif": "step", "playback": "projectile", "anchor": "center", "impactStartFrame": 16},
    {"name": "merge", "tint": "cyan", "motif": "merge", "playback": "projectile", "anchor": "center", "impactStartFrame": 20},
    {"name": "merge-base", "tint": "indigo", "motif": "root", "playback": "target", "anchor": "feet"},
    {"name": "checkout-conflict", "tint": "steel", "motif": "choose-side", "playback": "target", "anchor": "center"},
    {"name": "diff-conflict", "tint": "cyan", "motif": "conflict-compare", "playback": "target", "anchor": "feet"},
    {"name": "ls-files", "tint": "steel", "motif": "ledger", "playback": "target", "anchor": "feet"},
    {"name": "mergetool", "tint": "azure", "motif": "weld", "playback": "target", "anchor": "center"},
    {"name": "reset", "tint": "steel", "motif": "rewind", "playback": "target", "anchor": "feet"},
    {"name": "revert", "tint": "indigo", "motif": "counter", "playback": "target", "anchor": "center"},
    {"name": "reflog", "tint": "violet", "motif": "echo", "playback": "projectile", "anchor": "center", "impactStartFrame": 16},
    {"name": "stash", "tint": "violet", "motif": "fold", "playback": "projectile", "anchor": "center", "impactStartFrame": 15},
    {"name": "cherry-pick", "tint": "azure", "motif": "claws", "playback": "target", "anchor": "feet"},
    {"name": "remote", "tint": "steel", "motif": "beacon", "playback": "target", "anchor": "feet"},
    {"name": "fetch", "tint": "steel", "motif": "inbound", "playback": "target", "anchor": "center"},
    {"name": "pull", "tint": "azure", "motif": "pull", "playback": "target", "anchor": "feet"},
    {"name": "push", "tint": "steel", "motif": "push", "playback": "ground", "anchor": "feet"},
    {"name": "rebase", "tint": "indigo", "motif": "ladder", "playback": "target", "anchor": "feet"},
    {"name": "default", "tint": "cyan", "motif": "bolt", "playback": "projectile", "anchor": "center", "impactStartFrame": 15},
]

COMPANION_COMMAND_OVERRIDES: dict[str, dict[str, dict[str, object]]] = {
    "black": {
        "init": {"launchStartFrame": 8, "impactStartFrame": 14},
        "diff": {"impactStartFrame": 14},
        "add": {"anchor": "center", "launchStartFrame": 3, "impactStartFrame": 18},
        "rm": {"impactStartFrame": 17},
        "branch": {"anchor": "center", "impactStartFrame": 19},
        "checkout": {"impactStartFrame": 17},
        "clone": {"anchor": "center"},
    },
    "white": {
        "clone": {"anchor": "center"},
        "diff": {"impactStartFrame": 20},
        "add": {"launchStartFrame": 10, "impactStartFrame": 15},
        "branch": {"anchor": "center", "impactStartFrame": 17},
        "checkout": {"impactStartFrame": 20},
        "merge": {"anchor": "feet", "impactStartFrame": 18},
        "ls-files": {"anchor": "center"},
        "stash": {"anchor": "feet", "impactStartFrame": 13},
    },
    "blue": {"add": {"launchStartFrame": 3, "impactStartFrame": 16}},
}

CROP_ARTIFACT_REPAIRS: dict[tuple[str, str], dict[str, set[int]]] = {
    ("blue", "restore"): {"top": set(range(5, 25))},
    ("blue", "rebase"): {"top": set(range(10, 25))},
    ("white", "add"): {"bottom": set(range(14, 20))},
    ("white", "reflog"): {"top": set(range(10, 15))},
    ("white", "rebase"): {"top": {18, 19}},
    ("black", "diff-conflict"): {"top": {10, *range(15, 25)}},
}

EXTERNALLY_SUPPLIED_EFFECTS = [
    {"name": "miss", "tint": "ash", "motif": "misfire", "playback": "miss"},
]

ALL_EFFECTS = [*COMMANDS, *EXTERNALLY_SUPPLIED_EFFECTS]
RAW_COMMANDS = {spec["name"] for spec in COMMANDS}

COMPANION_EFFECT_SETS: dict[str, dict[str, object]] = {
    "blue": {
        "effectSet": "skill-flames-25",
        "manifestId": "blue-skill-flames-25",
        "label": "Blue Git Skill Flame Sprites 25",
        "generationMode": "imagegen-per-sheet",
        "styleReference": "/cosmetics/companion/blue/cast.png",
        "conceptReference": "/cosmetics/companion/blue/effects/skill-flames/_blue-flame-reference-concept.png",
        "backgroundMode": "chroma-key",
        "outputPalette": "preserve",
        "anchorMode": "bright",
        "previewBackground": (8, 13, 24, 255),
        "previewNameFill": (220, 245, 255),
        "previewMotifFill": (117, 211, 255),
        "motifPrefix": "",
        "initMotion": "gather-orb-projectile-impact-dissipate",
        "initTintOverride": None,
        "rawSourceLabel": "imagegen-raw",
        "requireCompleteRawCoverage": True,
    },
    "black": {
        "effectSet": "skill-lightning-25",
        "manifestId": "black-skill-lightning-25",
        "label": "Black Git Skill Lightning Sprites 25",
        "generationMode": "black-imagegen-and-smooth-derived-sheets",
        "styleReference": "/cosmetics/companion/black/cast.png",
        # Black's raw art is vivid purple lightning generated on a green screen.
        # Green keys cleanly because the effect has almost no green; the keyer
        # preserves colour (including the dark smoke) and despills the green rim.
        "backgroundMode": "green-screen",
        "outputPalette": "preserve",
        "anchorMode": "bright",
        "previewBackground": (7, 7, 12, 255),
        "previewNameFill": (235, 226, 255),
        "previewMotifFill": (190, 118, 255),
        "motifPrefix": "black-lightning-",
        "initMotion": "gather-orb-projectile-impact-dissipate",
        "initTintOverride": "violet",
        "rawSourceLabel": "black-imagegen-raw",
        "requireCompleteRawCoverage": False,
    },
    "white": {
        "effectSet": "skill-ice-25",
        "manifestId": "white-skill-ice-25",
        "label": "White Git Skill Ice Sprites 25",
        "generationMode": "white-imagegen-and-derived-ice-sheets",
        "styleReference": "/cosmetics/companion/white/cast.png",
        "backgroundMode": "chroma-key",
        "outputPalette": "preserve",
        "anchorMode": "bright",
        "previewBackground": (7, 13, 20, 255),
        "previewNameFill": (244, 252, 255),
        "previewMotifFill": (152, 221, 255),
        "motifPrefix": "white-ice-",
        "initMotion": "gather-orb-projectile-impact-dissipate",
        "initTintOverride": "azure",
        "rawSourceLabel": "white-imagegen-and-derived-raw",
        "requireCompleteRawCoverage": False,
    },
}

COMPANION_SLUG = "blue"
EFFECT_SET = "skill-flames-25"
EFFECT_BASE_URL = "/cosmetics/companion/blue/effects/skill-flames-25"
MANIFEST_ID = "blue-skill-flames-25"
MANIFEST_LABEL = "Blue Git Skill Flame Sprites 25"
GENERATION_MODE = "imagegen-per-sheet"
STYLE_REFERENCE = "/cosmetics/companion/blue/cast.png"
CONCEPT_REFERENCE: str | None = "/cosmetics/companion/blue/effects/skill-flames/_blue-flame-reference-concept.png"
OUTPUT_PALETTE = "preserve"
BACKGROUND_MODE = "chroma-key"
ANCHOR_MODE = "bright"
PREVIEW_BACKGROUND = (8, 13, 24, 255)
PREVIEW_NAME_FILL = (220, 245, 255)
PREVIEW_MOTIF_FILL = (117, 211, 255)
MOTIF_PREFIX = ""
INIT_MOTION = "gather-orb-projectile-impact-dissipate"
INIT_TINT_OVERRIDE: str | None = None
RAW_SOURCE_LABEL = "imagegen-raw"
REQUIRE_COMPLETE_RAW_COVERAGE = True


class FrameAnchor(NamedTuple):
    x: float
    y: float
    weight: float
    pixel_count: int
    bbox: tuple[int, int, int, int]


class RegistrationDebug(NamedTuple):
    target_anchor: tuple[float, float] | None
    detected_anchor_range: list[float]
    applied_shift_range: list[int]
    empty_frames: int
    reliable_frames: int
    low_confidence_frames: int
    mode: str


def configure_effect_set(companion: str, effect_set: str | None = None) -> None:
    config = COMPANION_EFFECT_SETS.get(companion)
    if config is None:
        known = ", ".join(sorted(COMPANION_EFFECT_SETS))
        raise SystemExit(f"Unknown companion '{companion}'. Known companions: {known}")

    resolved_effect_set = effect_set or str(config["effectSet"])
    global COMPANION_SLUG, EFFECT_SET, OUT_DIR, RAW_DIR, EFFECT_BASE_URL
    global MANIFEST_ID, MANIFEST_LABEL, GENERATION_MODE, STYLE_REFERENCE, CONCEPT_REFERENCE
    global OUTPUT_PALETTE, BACKGROUND_MODE, ANCHOR_MODE, PREVIEW_BACKGROUND, PREVIEW_NAME_FILL, PREVIEW_MOTIF_FILL
    global MOTIF_PREFIX, INIT_MOTION, INIT_TINT_OVERRIDE, RAW_SOURCE_LABEL, REQUIRE_COMPLETE_RAW_COVERAGE

    COMPANION_SLUG = companion
    EFFECT_SET = resolved_effect_set
    OUT_DIR = COMPANION_ROOT / companion / "effects" / resolved_effect_set
    RAW_DIR = OUT_DIR / "_raw"
    EFFECT_BASE_URL = f"/cosmetics/companion/{companion}/effects/{resolved_effect_set}"
    MANIFEST_ID = str(config["manifestId"])
    MANIFEST_LABEL = str(config["label"])
    GENERATION_MODE = str(config["generationMode"])
    STYLE_REFERENCE = str(config["styleReference"])
    concept_reference = config.get("conceptReference")
    CONCEPT_REFERENCE = str(concept_reference) if concept_reference else None
    OUTPUT_PALETTE = str(config["outputPalette"])
    BACKGROUND_MODE = str(config.get("backgroundMode", "chroma-key"))
    ANCHOR_MODE = str(config["anchorMode"])
    PREVIEW_BACKGROUND = tuple(config["previewBackground"])  # type: ignore[assignment]
    PREVIEW_NAME_FILL = tuple(config["previewNameFill"])  # type: ignore[assignment]
    PREVIEW_MOTIF_FILL = tuple(config["previewMotifFill"])  # type: ignore[assignment]
    MOTIF_PREFIX = str(config["motifPrefix"])
    INIT_MOTION = str(config["initMotion"])
    init_tint_override = config.get("initTintOverride")
    INIT_TINT_OVERRIDE = str(init_tint_override) if init_tint_override else None
    RAW_SOURCE_LABEL = str(config["rawSourceLabel"])
    REQUIRE_COMPLETE_RAW_COVERAGE = bool(config["requireCompleteRawCoverage"])


def sample_key_color(im: Image.Image) -> tuple[int, int, int]:
    rgb = im.convert("RGB")
    w, h = rgb.size
    strips = [
        rgb.crop((0, 0, w, max(1, h // 28))),
        rgb.crop((0, h - max(1, h // 28), w, h)),
        rgb.crop((0, 0, max(1, w // 28), h)),
        rgb.crop((w - max(1, w // 28), 0, w, h)),
    ]
    pixels: list[tuple[int, int, int]] = []
    for strip in strips:
        pixels.extend(strip.resize((80, 8)).getdata())
    count = len(pixels)
    return (
        round(sum(p[0] for p in pixels) / count),
        round(sum(p[1] for p in pixels) / count),
        round(sum(p[2] for p in pixels) / count),
    )


def remove_keyed_background(im: Image.Image) -> Image.Image:
    if BACKGROUND_MODE == "green-screen":
        return remove_green_screen_background(im)
    if BACKGROUND_MODE == "neutral-grey":
        return remove_neutral_grey_background(im)
    return remove_chroma_key_background(im)


def remove_green_screen_background(im: Image.Image) -> Image.Image:
    """Chroma-key a vivid effect off a pure-green backing card, colour preserved.

    Black's lightning is now generated on a green screen (~RGB 10,240,10). Green
    is the ideal key because the effect (purple bolts, white-hot cores, black
    smoke) has little green: a pixel is background exactly when green dominates
    both other channels. Alpha ramps on that "greenness" so semi-transparent
    edges feather cleanly, and a despill pass clamps the green channel so no green
    fringe survives around the effect. Everything non-green - including the dark
    smoke - is kept, so the shadow substance is not lost.
    """
    import numpy as np

    rgb = im.convert("RGB")
    arr = np.asarray(rgb, dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    other_max = np.maximum(r, b)

    # Greenness: how much the green channel exceeds the strongest of R/B. Pure
    # key green is strongly positive; purple/white/black effect pixels are <= 0.
    greenness = g - other_max
    lo, hi = 12.0, 80.0
    alpha = 1.0 - np.clip((greenness - lo) / (hi - lo), 0.0, 1.0)

    # Despill: pull the green channel down to the other channels wherever it spills
    # over, killing the green rim on antialiased edges without touching purples
    # (already low green) or whites (R=G=B, so unchanged).
    g_despilled = np.minimum(g, other_max)
    out_rgb = np.stack([r, g_despilled, b], axis=-1).astype(np.uint8)

    alpha_img = Image.fromarray((alpha * 255).astype(np.uint8), mode="L")
    alpha_img = alpha_img.filter(ImageFilter.GaussianBlur(0.4))
    out = Image.fromarray(out_rgb, mode="RGB").convert("RGBA")
    out.putalpha(alpha_img)
    return out


def _frame_grid_bounds(width: int, height: int) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    return fixed_axis_bounds(width, GRID_COLUMNS), fixed_axis_bounds(height, GRID_ROWS)


def remove_neutral_grey_background(im: Image.Image) -> Image.Image:
    """Key a vivid effect off a *neutral grey* backing card, preserving colour.

    Black's lightning is generated on a flat grey card whose exact grey drifts
    from sheet to sheet (and can vignette within a sheet). A single-colour
    difference matte leaves grey haloes; flattening to pure black additionally
    destroys the bright cores. Instead we exploit what actually separates the
    effect from the card: the card is neutral (near-zero chroma) at one luma,
    while the effect is either saturated (coloured bolts), much brighter than the
    card (white-hot cores), or much darker (black smoke tendrils). Alpha is the
    max of those three signals, sampled against a *per-frame* key luma so the
    drifting/vignetting grey does not matter. Colour is left untouched.
    """
    import numpy as np

    rgb = im.convert("RGB")
    w, h = rgb.size
    x_bounds, y_bounds = _frame_grid_bounds(w, h)

    arr = np.asarray(rgb, dtype=np.float32)
    luma = arr @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    chroma = arr.max(axis=2) - arr.min(axis=2)

    # Per-cell key luma (the neutral card brightness), so a drifting or
    # vignetting grey between cells does not matter.
    key = np.empty_like(luma)
    for (fy0, fy1) in y_bounds:
        for (fx0, fx1) in x_bounds:
            key[fy0:fy1, fx0:fx1] = _cell_key_luma(luma[fy0:fy1, fx0:fx1])

    # Saturation of the coloured lightning body.
    chroma_lo, chroma_hi = 14.0, 70.0
    # White-hot cores sit well above the card luma.
    bright_lo, bright_hi = 26.0, 120.0
    # Dark smoke / shadow tendrils sit below the card luma and ARE part of the
    # spell - they must survive keying. The threshold starts just below the card
    # so darker-than-card pixels are preserved (previously they were cut, which
    # deleted the black companion's shadow substance and left only bright bolts).
    dark_lo, dark_hi = 16.0, 95.0

    a_c = (chroma - chroma_lo) / (chroma_hi - chroma_lo)
    a_b = (luma - key - bright_lo) / (bright_hi - bright_lo)
    a_d = (key - luma - dark_lo) / (dark_hi - dark_lo)
    a = np.clip(np.maximum(np.maximum(a_c, a_b), a_d), 0.0, 1.0)

    alpha = Image.fromarray((a * 255).astype(np.uint8), mode="L")
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.5))
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out


def _cell_key_luma(cell_luma) -> float:
    """Median border luma of a single cell - the neutral card's brightness."""
    import numpy as np

    s = max(2, cell_luma.shape[1] // 40)
    border = np.concatenate(
        [
            cell_luma[:s, :].ravel(),
            cell_luma[-s:, :].ravel(),
            cell_luma[:, :s].ravel(),
            cell_luma[:, -s:].ravel(),
        ]
    )
    return float(np.median(border)) if border.size else 90.0


def remove_chroma_key_background(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    key = sample_key_color(im)
    rgb = im.convert("RGB")
    key_image = Image.new("RGB", im.size, key)
    diff = ImageChops.difference(rgb, key_image).convert("L")

    # Smooth matte: near the sampled key disappears, far colors stay opaque.
    low = 18
    high = 92
    alpha = diff.point(lambda v: 0 if v <= low else 255 if v >= high else round((v - low) * 255 / (high - low)))
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.35))

    out = im.copy()
    out.putalpha(alpha)

    # Despill the sampled key around antialiased edges without crushing blue fire.
    px = out.load()
    w, h = out.size
    kr, kg, kb = key
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if not 0 < a < 230:
                continue
            if kg > kr * 1.8 and kg > kb * 1.8 and g > r * 1.4 and g > b * 1.08:
                g = min(g, round((r + b) * 0.46))
                px[x, y] = (r, g, b, a)
            elif kr > kg * 1.6 and kb > kg * 1.6 and r > g * 1.4 and b > g * 1.4:
                bleed = round(g * 0.72 + min(r, b) * 0.18)
                px[x, y] = (min(r, bleed), g, min(b, bleed), a)
    return out


def apply_output_palette(sheet: Image.Image) -> Image.Image:
    if OUTPUT_PALETTE != "pure-black":
        return sheet

    out = Image.new("RGBA", sheet.size, (0, 0, 0, 0))
    out.putalpha(sheet.getchannel("A"))
    return out


def alpha_bbox(im: Image.Image, threshold: int = 8) -> tuple[int, int, int, int] | None:
    alpha = im.getchannel("A").point(lambda v: 255 if v > threshold else 0)
    return alpha.getbbox()


def clear_frame_edges(frame: Image.Image) -> Image.Image:
    frame = frame.convert("RGBA")
    alpha = frame.getchannel("A")
    draw = ImageDraw.Draw(alpha)
    edge = max(1, EDGE_CLEAR_PX)
    draw.rectangle((0, 0, FRAME - 1, edge - 1), fill=0)
    draw.rectangle((0, FRAME - edge, FRAME - 1, FRAME - 1), fill=0)
    draw.rectangle((0, 0, edge - 1, FRAME - 1), fill=0)
    draw.rectangle((FRAME - edge, 0, FRAME - 1, FRAME - 1), fill=0)
    frame.putalpha(alpha)
    return frame


def remove_edge_artifact_components(frame: Image.Image, edges: set[str]) -> Image.Image:
    """Remove detached raw-sheet spill from neighboring cells on audited frames."""
    if not edges:
        return frame

    frame = frame.convert("RGBA")
    alpha = frame.getchannel("A")
    px = alpha.load()
    visited = bytearray(FRAME * FRAME)
    to_clear: list[tuple[int, int]] = []
    band = 24
    max_height = 54
    min_width = 16
    min_area = 24

    def pos(x: int, y: int) -> int:
        return y * FRAME + x

    for start_y in range(FRAME):
        for start_x in range(FRAME):
            start = pos(start_x, start_y)
            if visited[start] or px[start_x, start_y] <= ALPHA_THRESHOLD:
                continue

            stack = [(start_x, start_y)]
            visited[start] = 1
            component: list[tuple[int, int]] = []
            x0 = x1 = start_x
            y0 = y1 = start_y

            while stack:
                x, y = stack.pop()
                component.append((x, y))
                x0 = min(x0, x)
                y0 = min(y0, y)
                x1 = max(x1, x)
                y1 = max(y1, y)
                for ny in range(max(0, y - 1), min(FRAME, y + 2)):
                    for nx in range(max(0, x - 1), min(FRAME, x + 2)):
                        p = pos(nx, ny)
                        if visited[p] or px[nx, ny] <= ALPHA_THRESHOLD:
                            continue
                        visited[p] = 1
                        stack.append((nx, ny))

            width = x1 - x0 + 1
            height = y1 - y0 + 1
            area = len(component)
            substantial = width >= min_width or area >= min_area
            top_orphan = "top" in edges and y0 <= band and height <= max_height and substantial
            bottom_orphan = "bottom" in edges and y1 >= FRAME - 1 - band and height <= max_height and substantial
            if top_orphan or bottom_orphan:
                to_clear.extend(component)

    if not to_clear:
        return frame

    for x, y in to_clear:
        px[x, y] = 0
    frame.putalpha(alpha)
    return frame


def normalize_frame(frame: Image.Image) -> Image.Image:
    # Keep the raw grid coordinate system first, then register the whole
    # sequence afterwards. Do not crop every frame to its own alpha box; that is
    # the exact mistake that creates sprite swimming.
    return clear_frame_edges(frame.resize((FRAME, FRAME), Image.Resampling.LANCZOS))


def shifted_frame(frame: Image.Image, dx: int, dy: int) -> Image.Image:
    out = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    out.alpha_composite(frame, (dx, dy))
    return out


def clamp_int(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def fixed_axis_bounds(length: int, count: int) -> list[tuple[int, int]]:
    points = [round(index * length / count) for index in range(count + 1)]
    return [(points[i], points[i + 1]) for i in range(count)]


def weighted_median(values: list[tuple[float, float]]) -> float:
    """Return weighted median for pairs of (value, weight)."""
    clean = [(value, max(0.0, weight)) for value, weight in values if weight > 0]
    if not clean:
        return 0.0
    clean.sort(key=lambda item: item[0])
    total = sum(weight for _, weight in clean)
    halfway = total / 2
    running = 0.0
    for value, weight in clean:
        running += weight
        if running >= halfway:
            return value
    return clean[-1][0]


def weighted_percentile(values: list[tuple[float, float]], percentile: float) -> float:
    """Return weighted percentile for pairs of (value, weight)."""
    clean = [(value, max(0.0, weight)) for value, weight in values if weight > 0]
    if not clean:
        return 0.0
    clean.sort(key=lambda item: item[0])
    total = sum(weight for _, weight in clean)
    threshold = total * max(0.0, min(1.0, percentile))
    running = 0.0
    for value, weight in clean:
        running += weight
        if running >= threshold:
            return value
    return clean[-1][0]


def detect_effect_anchor(frame: Image.Image, playback: str) -> FrameAnchor | None:
    """Detect the stable VFX pivot for one frame.

    This is the effect equivalent of the character root/pivot registration used
    on the skeleton knight sheet. For VFX, the most stable landmark is usually
    not the outer bounding box. It is the bright, opaque energy core.

    Target effects and projectile effects use the same core idea, but projectile
    effects slightly favor brighter pixels so long transparent flame tails do not
    pull the anchor backward.
    """
    frame = frame.convert("RGBA")
    bbox = alpha_bbox(frame, threshold=ALPHA_THRESHOLD)
    if not bbox:
        return None

    x0, y0, x1, y1 = bbox
    px = frame.load()

    sx = 0.0
    sy = 0.0
    sw = 0.0
    pixel_count = 0

    # Pass over the bbox only. That keeps the script fast even for many sheets.
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b, a = px[x, y]
            if a <= ALPHA_THRESHOLD:
                continue

            bright = max(r, g, b)
            if ANCHOR_MODE != "alpha" and bright < 12:
                continue

            # Alpha finds the actual object; brightness focuses on the stable
            # flame core instead of wispy antialiasing, particles, and trails.
            alpha_weight = a / 255.0
            bright_weight = bright / 255.0

            if ANCHOR_MODE == "alpha":
                # Pure dark VFX has no bright core by design. Use the keyed
                # silhouette itself so all-black lightning can still register.
                weight = alpha_weight
            elif playback == "projectile":
                # Projectile tails and smoke change length a lot. Squaring the
                # brightness keeps the head/core steadier than bbox centering.
                weight = alpha_weight * (0.25 + bright_weight) ** 2.0
            else:
                # Target AOEs/rings should remain centered as they grow and
                # fade. Use a gentler brightness bias so the ring body still
                # contributes to the anchor.
                weight = alpha_weight * (0.40 + bright_weight) ** 1.55

            sx += x * weight
            sy += y * weight
            sw += weight
            pixel_count += 1

    if sw <= 0 or pixel_count == 0:
        # Last-resort fallback. This should rarely run, but it is better than
        # dropping the frame or inventing a random anchor.
        return FrameAnchor((x0 + x1) / 2, (y0 + y1) / 2, 1.0, 0, bbox)

    return FrameAnchor(sx / sw, sy / sw, sw, pixel_count, bbox)


def detect_projectile_nose_anchor(frame: Image.Image) -> FrameAnchor | None:
    """Detect the leading point of a left-to-right projectile frame.

    The battle runtime positions projectiles by a nose anchor, not by the
    projectile's center of mass. Long flame tails change the energy centroid on
    every frame, so using the centroid as the registration landmark makes the
    impact point wobble. A high weighted x-percentile is more stable than the
    absolute rightmost pixel because it ignores stray sparks while still tracking
    the bright leading head.
    """
    frame = frame.convert("RGBA")
    bbox = alpha_bbox(frame, threshold=ALPHA_THRESHOLD)
    if not bbox:
        return None

    x0, y0, x1, y1 = bbox
    px = frame.load()
    weighted_pixels: list[tuple[int, int, float]] = []
    pixel_count = 0
    total_weight = 0.0

    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b, a = px[x, y]
            if a <= ALPHA_THRESHOLD:
                continue

            bright = max(r, g, b)
            if ANCHOR_MODE != "alpha" and bright < 12:
                continue

            alpha_weight = a / 255.0
            bright_weight = bright / 255.0
            weight = alpha_weight if ANCHOR_MODE == "alpha" else alpha_weight * (0.25 + bright_weight) ** 2.25
            weighted_pixels.append((x, y, weight))
            total_weight += weight
            pixel_count += 1

    if total_weight <= 0 or pixel_count == 0:
        return FrameAnchor((x0 + x1) / 2, (y0 + y1) / 2, 1.0, 0, bbox)

    nose_x = weighted_percentile([(x, weight) for x, _, weight in weighted_pixels], 0.88)
    window = max(6.0, (x1 - x0) * 0.16)
    nose_band = [
        (y, weight * (1.0 + max(0.0, x - (nose_x - window)) / window))
        for x, y, weight in weighted_pixels
        if x >= nose_x - window
    ]
    nose_y = weighted_median(nose_band) if nose_band else weighted_median([(y, weight) for _, y, weight in weighted_pixels])
    return FrameAnchor(nose_x, nose_y, total_weight, pixel_count, bbox)


def detect_feet_anchor(frame: Image.Image) -> FrameAnchor | None:
    """Detect the horizontal core and planted base of a ground-rooted frame.

    Ground/feet effects (tornadoes, geysers, crystal blooms, floor rings, the
    push shockwave, the switch wave) grow upward from the floor. The stable
    landmark is not the centroid - it rises as the effect blooms - but the
    horizontal energy centre and the visible *base*. `x` carries the weighted
    core x, `y` carries a robust bottom percentile so a couple of low embers do
    not drag the planted edge down.
    """
    frame = frame.convert("RGBA")
    bbox = alpha_bbox(frame, threshold=ALPHA_THRESHOLD)
    if not bbox:
        return None

    x0, y0, x1, y1 = bbox
    px = frame.load()
    xs: list[tuple[float, float]] = []
    ys: list[tuple[float, float]] = []
    total_weight = 0.0
    pixel_count = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b, a = px[x, y]
            if a <= ALPHA_THRESHOLD:
                continue
            bright = max(r, g, b)
            if ANCHOR_MODE != "alpha" and bright < 12:
                continue
            alpha_weight = a / 255.0
            weight = alpha_weight if ANCHOR_MODE == "alpha" else alpha_weight * (0.40 + bright / 255.0) ** 1.4
            xs.append((x, weight))
            ys.append((y, weight))
            total_weight += weight
            pixel_count += 1

    if total_weight <= 0 or pixel_count == 0:
        return FrameAnchor((x0 + x1) / 2, float(y1), 1.0, 0, bbox)

    core_x = weighted_median(xs)
    base_y = weighted_percentile(ys, FEET_BASE_PERCENTILE)
    return FrameAnchor(core_x, base_y, total_weight, pixel_count, bbox)


def registration_mode_for(playback: str, anchor: str) -> str:
    """Map a resolved (playback, anchor) to the pivot-baking strategy.

    Projectiles use the hand/nose/settle pivots. `ground` effects always plant on
    the floor and run along it. `target` effects honor their per-effect anchor:
    a ground-rooted riser ("feet") is baked with its base on the ground line, and
    a body-centered aura/burst ("center") is baked to the cell centre so the
    runtime CENTER_ANCHOR lands it on the monster's body instead of its feet.
    """
    if playback == "projectile":
        return "projectile"
    if playback == "ground":
        return "feet"
    return "feet" if anchor == "feet" else "center"


def scale_frame_centered(frame: Image.Image, scale: float) -> Image.Image:
    """Uniformly shrink a frame's content about the cell centre.

    Used to fit tall ground-rooted sequences inside the cell before planting, so
    the crest of a switch wave or the tip of a geyser does not clip the top edge.
    """
    if scale >= 0.999:
        return frame
    new = max(1, round(FRAME * scale))
    small = frame.resize((new, new), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    offset = (FRAME - new) // 2
    out.alpha_composite(small, (offset, offset))
    return out


def detect_registration_anchor(frame: Image.Image, playback: str, index: int) -> FrameAnchor | None:
    if (
        playback == "projectile"
        and PROJECTILE_LAUNCH_START_FRAME <= index < PROJECTILE_SETTLE_START_FRAME
    ):
        return detect_projectile_nose_anchor(frame)
    return detect_effect_anchor(frame, "target" if playback == "projectile" else playback)


def is_reliable_anchor(anchor: FrameAnchor, max_weight: float, max_pixels: int) -> bool:
    """Return whether a detected anchor is trustworthy enough to drive alignment."""
    if max_weight <= 0 or max_pixels <= 0:
        return False
    return (
        anchor.weight >= max_weight * MIN_RELIABLE_ANCHOR_WEIGHT_RATIO
        and anchor.pixel_count >= max(16, round(max_pixels * MIN_RELIABLE_ANCHOR_PIXEL_RATIO))
    )


def interpolated_shift(
    index: int,
    shift_by_index: dict[int, tuple[int, int]],
    fallback: tuple[int, int],
) -> tuple[int, int]:
    """Fill anchorless frame shifts from nearby registered frames."""
    if index in shift_by_index:
        return shift_by_index[index]

    previous_indices = [i for i in shift_by_index if i < index]
    next_indices = [i for i in shift_by_index if i > index]
    previous_index = max(previous_indices) if previous_indices else None
    next_index = min(next_indices) if next_indices else None

    if previous_index is not None and next_index is not None:
        prev_dx, prev_dy = shift_by_index[previous_index]
        next_dx, next_dy = shift_by_index[next_index]
        t = (index - previous_index) / (next_index - previous_index)
        return (round(prev_dx + (next_dx - prev_dx) * t), round(prev_dy + (next_dy - prev_dy) * t))

    if previous_index is not None:
        return shift_by_index[previous_index]
    if next_index is not None:
        return shift_by_index[next_index]
    return fallback


def _feet_registration_plan(
    frames: list[Image.Image], ground_travel: bool
) -> tuple[float, list[tuple[int, int]], RegistrationDebug]:
    """Plant a ground-rooted sequence's base on the ground line.

    Risers (tornado, geyser, floor ring) keep a stable horizontal core and grow
    upward, so we centre the core x and shift each frame so its visible base sits
    on GROUND_ANCHOR_Y. Ground-travel effects (push, switch) instead preserve
    their internal forward motion - the whole sequence is centred by one constant
    x shift - and the runtime slides them from caster to enemy. Tall sequences
    are uniformly scaled down first so their crest does not clip the cell.
    """
    def detect_all(fs: list[Image.Image]) -> list[FrameAnchor | None]:
        return [detect_feet_anchor(frame) for frame in fs]

    def pools(anchors: list[FrameAnchor | None]) -> tuple[dict[int, FrameAnchor], dict[int, FrameAnchor]]:
        valid_local = [a for a in anchors if a is not None]
        if not valid_local:
            return {}, {}
        mw = max(a.weight for a in valid_local)
        mp = max(a.pixel_count for a in valid_local)
        reliable = {i: a for i, a in enumerate(anchors) if a is not None and is_reliable_anchor(a, mw, mp)}
        all_valid = {i: a for i, a in enumerate(anchors) if a is not None}
        return reliable, (reliable or all_valid)

    anchors = detect_all(frames)
    valid = [a for a in anchors if a is not None]
    if not valid:
        return 1.0, [], RegistrationDebug(None, [], [], len(frames), 0, 0, "no detectable frames")
    reliable_by_index, pool = pools(anchors)

    available = GROUND_ANCHOR_Y - FEET_TOP_MARGIN
    heights = [a.bbox[3] - a.bbox[1] for a in pool.values()]
    max_height = max(heights) if heights else available
    scale = min(1.0, available / max_height) if max_height > available else 1.0
    if scale < 0.999:
        frames = [scale_frame_centered(frame, scale) for frame in frames]
        anchors = detect_all(frames)
        valid = [a for a in anchors if a is not None]
        reliable_by_index, pool = pools(anchors)

    seq_center_x = weighted_median([(a.x, a.weight) for a in pool.values()])
    const_dx = clamp_int(round(FRAME * 0.5 - seq_center_x), -MAX_REGISTRATION_SHIFT, MAX_REGISTRATION_SHIFT)

    shift_by_index: dict[int, tuple[int, int]] = {}
    for index, anchor in enumerate(anchors):
        if anchor is None:
            continue
        dx = const_dx if ground_travel else clamp_int(
            round(seq_center_x - anchor.x), -MAX_REGISTRATION_SHIFT, MAX_REGISTRATION_SHIFT
        )
        dy = clamp_int(round(GROUND_ANCHOR_Y - anchor.y), -MAX_REGISTRATION_SHIFT, MAX_REGISTRATION_SHIFT)
        shift_by_index[index] = (dx, dy)

    shifts: list[tuple[int, int]] = []
    last_shift = (0, 0)
    for index in range(len(frames)):
        dx, dy = interpolated_shift(index, shift_by_index, last_shift)
        last_shift = (dx, dy)
        shifts.append((dx, dy))

    xs = [a.x for a in valid]
    ys = [a.y for a in valid]
    dxs = [s[0] for s in shifts]
    dys = [s[1] for s in shifts]
    debug = RegistrationDebug(
        target_anchor=(round(seq_center_x, 3), round(GROUND_ANCHOR_Y, 3)),
        detected_anchor_range=[round(min(xs), 3), round(max(xs), 3), round(min(ys), 3), round(max(ys), 3)],
        applied_shift_range=[min(dxs), max(dxs), min(dys), max(dys)],
        empty_frames=len(frames) - len(valid),
        reliable_frames=len(reliable_by_index),
        low_confidence_frames=len(valid) - len(reliable_by_index),
        mode=(
            "ground-travel: base planted on ground line, forward motion preserved for runtime travel"
            if ground_travel
            else f"feet-planted base on ground line (fit scale {scale:.3f}), core-x centred"
        ),
    )
    return scale, shifts, debug


def _center_registration_plan(
    frames: list[Image.Image],
) -> tuple[float, list[tuple[int, int]], RegistrationDebug]:
    """Register a body-centered effect's energy core to the cell centre.

    Auras, rings and bursts that play *on* the monster body (status scan, config
    reticle, commit burst, revert ring, ...) are not ground-rooted. Their stable
    landmark is the bright energy core, and the runtime plants them with the
    CENTER_ANCHOR on the monster's body centre. Shifting every frame's detected
    core onto the cell centre keeps the sequence from swimming and lands it on the
    body instead of the floor - the exact opposite of the feet plan.
    """
    anchors = [detect_effect_anchor(frame, "target") for frame in frames]
    valid = [anchor for anchor in anchors if anchor is not None]
    if not valid:
        return 1.0, [], RegistrationDebug(None, [], [], len(frames), 0, 0, "no detectable frames")

    max_weight = max(anchor.weight for anchor in valid)
    max_pixels = max(anchor.pixel_count for anchor in valid)
    reliable_by_index = {
        index: anchor
        for index, anchor in enumerate(anchors)
        if anchor is not None and is_reliable_anchor(anchor, max_weight, max_pixels)
    }

    target = (FRAME * 0.5, FRAME * 0.5)
    shift_by_index: dict[int, tuple[int, int]] = {}
    for index, anchor in enumerate(anchors):
        if anchor is None:
            continue
        dx = clamp_int(round(target[0] - anchor.x), -MAX_REGISTRATION_SHIFT, MAX_REGISTRATION_SHIFT)
        dy = clamp_int(round(target[1] - anchor.y), -MAX_REGISTRATION_SHIFT, MAX_REGISTRATION_SHIFT)
        shift_by_index[index] = (dx, dy)

    shifts: list[tuple[int, int]] = []
    last_shift = (0, 0)
    for index in range(len(frames)):
        dx, dy = interpolated_shift(index, shift_by_index, last_shift)
        last_shift = (dx, dy)
        shifts.append((dx, dy))

    xs = [anchor.x for anchor in valid]
    ys = [anchor.y for anchor in valid]
    dxs = [shift[0] for shift in shifts]
    dys = [shift[1] for shift in shifts]
    debug = RegistrationDebug(
        target_anchor=(round(target[0], 3), round(target[1], 3)),
        detected_anchor_range=[round(min(xs), 3), round(max(xs), 3), round(min(ys), 3), round(max(ys), 3)],
        applied_shift_range=[min(dxs), max(dxs), min(dys), max(dys)],
        empty_frames=len(frames) - len(valid),
        reliable_frames=len(reliable_by_index),
        low_confidence_frames=len(valid) - len(reliable_by_index),
        mode="body-centered: energy core registered to cell centre",
    )
    return 1.0, shifts, debug


def _projectile_target_plan(
    frames: list[Image.Image], playback: str
) -> tuple[float, list[tuple[int, int]], RegistrationDebug]:
    anchors = [detect_registration_anchor(frame, playback, index) for index, frame in enumerate(frames)]
    valid = [anchor for anchor in anchors if anchor is not None]
    if not valid:
        return 1.0, [], RegistrationDebug(None, [], [], len(frames), 0, 0, "no detectable frames")

    max_weight = max(anchor.weight for anchor in valid)
    max_pixels = max(anchor.pixel_count for anchor in valid)

    reliable_by_index = {
        index: anchor
        for index, anchor in enumerate(anchors)
        if anchor is not None and is_reliable_anchor(anchor, max_weight, max_pixels)
    }

    # If a sheet is extremely sparse, fall back to all valid anchors rather than
    # disabling registration entirely.
    target_pool = list(reliable_by_index.values()) if reliable_by_index else valid

    sequence_target = (
        weighted_median([(anchor.x, anchor.weight) for anchor in target_pool]),
        weighted_median([(anchor.y, anchor.weight) for anchor in target_pool]),
    )

    def target_for_frame(index: int) -> tuple[float, float]:
        if playback == "projectile":
            if index < PROJECTILE_LAUNCH_START_FRAME:
                return PROJECTILE_HAND_ANCHOR
            return PROJECTILE_SETTLE_ANCHOR if index >= PROJECTILE_SETTLE_START_FRAME else PROJECTILE_FLIGHT_ANCHOR
        return sequence_target

    shift_by_index: dict[int, tuple[int, int]] = {}

    for index, anchor in enumerate(anchors):
        if anchor is None:
            continue
        target_x, target_y = target_for_frame(index)
        dx = clamp_int(round(target_x - anchor.x), -MAX_REGISTRATION_SHIFT, MAX_REGISTRATION_SHIFT)
        dy = clamp_int(round(target_y - anchor.y), -MAX_REGISTRATION_SHIFT, MAX_REGISTRATION_SHIFT)
        shift_by_index[index] = (dx, dy)

    shifts: list[tuple[int, int]] = []
    last_shift = (0, 0)
    for index in range(len(frames)):
        dx, dy = interpolated_shift(index, shift_by_index, last_shift)
        last_shift = (dx, dy)
        shifts.append((dx, dy))

    xs = [anchor.x for anchor in valid]
    ys = [anchor.y for anchor in valid]
    dxs = [shift[0] for shift in shifts]
    dys = [shift[1] for shift in shifts]
    debug = RegistrationDebug(
        target_anchor=(
            round(PROJECTILE_FLIGHT_ANCHOR[0], 3),
            round(PROJECTILE_FLIGHT_ANCHOR[1], 3),
        )
        if playback == "projectile"
        else (round(sequence_target[0], 3), round(sequence_target[1], 3)),
        detected_anchor_range=[round(min(xs), 3), round(max(xs), 3), round(min(ys), 3), round(max(ys), 3)],
        applied_shift_range=[min(dxs), max(dxs), min(dys), max(dys)],
        empty_frames=len(frames) - len(valid),
        reliable_frames=len(reliable_by_index),
        low_confidence_frames=len(valid) - len(reliable_by_index),
        mode=(
            f"hand-center anchor until frame {PROJECTILE_LAUNCH_START_FRAME - 1}, "
            f"projectile nose anchor through frame {PROJECTILE_SETTLE_START_FRAME - 1}, "
            "center anchor for impact/dissipate frames"
        )
        if playback == "projectile"
        else "sequence weighted-median energy-core pivot for all visible frames",
    )
    return 1.0, shifts, debug


def compute_registration_plan(
    frames: list[Image.Image], playback: str, anchor: str = "center"
) -> tuple[float, list[tuple[int, int]], RegistrationDebug]:
    """Return (scale, per-frame shifts, debug) without mutating the input frames.

    Layered effects compute one plan from the combined back+front alpha and apply
    it to each layer so the two depth passes stay pixel-aligned.
    """
    mode = registration_mode_for(playback, anchor)
    if mode == "feet":
        return _feet_registration_plan(frames, ground_travel=(playback == "ground"))
    if mode == "center":
        return _center_registration_plan(frames)
    return _projectile_target_plan(frames, playback)


def apply_registration_plan(
    frames: list[Image.Image], scale: float, shifts: list[tuple[int, int]]
) -> list[Image.Image]:
    scaled = [scale_frame_centered(frame, scale) for frame in frames] if scale < 0.999 else frames
    registered: list[Image.Image] = []
    last_shift = (0, 0)
    for index, frame in enumerate(scaled):
        dx, dy = shifts[index] if index < len(shifts) else last_shift
        last_shift = (dx, dy)
        registered.append(clear_frame_edges(shifted_frame(frame, dx, dy)))
    return registered


def register_sequence(
    frames: list[Image.Image], playback: str, anchor: str = "center"
) -> tuple[list[Image.Image], RegistrationDebug]:
    """Register all frames to one stable sequence anchor.

    Target effects use the weighted median of reliable energy-core anchors for
    the whole sequence. Init-style projectile sheets use the center hand anchor
    for gather/orb frames, the frontend's nose anchor for launch frames, and the
    center settle anchor for impact/fade frames. Ground-rooted effects (feet
    anchor or ground playback) plant their base on the ground line. Only frames
    with no detectable pixels inherit an interpolated shift.
    """
    scale, shifts, debug = compute_registration_plan(frames, playback, anchor)
    return apply_registration_plan(frames, scale, shifts), debug


def frame_diagnostics(sheet: Image.Image, playback: str, registration: RegistrationDebug | None = None) -> dict[str, object]:
    alpha = sheet.getchannel("A")
    centers: list[tuple[float, float]] = []
    anchors: list[FrameAnchor] = []
    registration_anchors: list[FrameAnchor] = []
    projectile_hand_anchors: list[FrameAnchor] = []
    projectile_flight_anchors: list[FrameAnchor] = []
    projectile_settle_anchors: list[FrameAnchor] = []

    for index in range(FRAMES):
        col = index % GRID_COLUMNS
        row = index // GRID_COLUMNS
        frame = sheet.crop((col * FRAME, row * FRAME, (col + 1) * FRAME, (row + 1) * FRAME))
        bbox = alpha_bbox(frame, threshold=ALPHA_THRESHOLD)
        if bbox:
            x0, y0, x1, y1 = bbox
            centers.append(((x0 + x1) / 2, (y0 + y1) / 2))
        anchor = detect_effect_anchor(frame, playback)
        if anchor:
            anchors.append(anchor)
        registration_anchor = detect_registration_anchor(frame, playback, index)
        if registration_anchor:
            if playback == "projectile":
                if index < PROJECTILE_LAUNCH_START_FRAME:
                    projectile_hand_anchors.append(registration_anchor)
                elif index < PROJECTILE_SETTLE_START_FRAME:
                    projectile_flight_anchors.append(registration_anchor)
                else:
                    projectile_settle_anchors.append(registration_anchor)
            else:
                registration_anchors.append(registration_anchor)

    if centers:
        xs = [point[0] for point in centers]
        ys = [point[1] for point in centers]
        center_range = [round(min(xs), 2), round(max(xs), 2), round(min(ys), 2), round(max(ys), 2)]
    else:
        center_range = []

    if anchors:
        ax = [anchor.x for anchor in anchors]
        ay = [anchor.y for anchor in anchors]
        anchor_range = [round(min(ax), 2), round(max(ax), 2), round(min(ay), 2), round(max(ay), 2)]
    else:
        anchor_range = []

    def frame_anchor_range(items: list[FrameAnchor]) -> list[float]:
        if not items:
            return []
        ax = [anchor.x for anchor in items]
        ay = [anchor.y for anchor in items]
        return [round(min(ax), 2), round(max(ax), 2), round(min(ay), 2), round(max(ay), 2)]

    data: dict[str, object] = {
        "size": sheet.size,
        "alphaExtrema": alpha.getextrema(),
        "bbox": alpha.getbbox(),
        # BBox centers are allowed to change because flames expand and collapse.
        # This is kept only as a visual debug signal, not as the registration rule.
        "frameBBoxCenterRange": center_range,
        # This is the important stability metric after registration.
        "frameEnergyAnchorRange": anchor_range,
    }
    if playback == "projectile":
        data["projectileHandEnergyAnchorRange"] = frame_anchor_range(projectile_hand_anchors)
        data["projectileFlightNoseAnchorRange"] = frame_anchor_range(projectile_flight_anchors)
        data["projectileSettleEnergyAnchorRange"] = frame_anchor_range(projectile_settle_anchors)
    else:
        data["frameRegistrationAnchorRange"] = frame_anchor_range(registration_anchors)
    if registration:
        registration_data: dict[str, object] = {
            "targetAnchor": registration.target_anchor,
            "detectedAnchorRangeBeforeRegistration": registration.detected_anchor_range,
            "appliedShiftRange": registration.applied_shift_range,
            "emptyFrames": registration.empty_frames,
            "reliableFrames": registration.reliable_frames,
            "lowConfidenceFrames": registration.low_confidence_frames,
            "method": registration.mode,
        }
        if playback == "projectile":
            registration_data["projectileLaunchStartFrame"] = PROJECTILE_LAUNCH_START_FRAME
            registration_data["projectileSettleStartFrame"] = PROJECTILE_SETTLE_START_FRAME
            registration_data["projectileHandAnchor"] = [
                round(PROJECTILE_HAND_ANCHOR[0], 3),
                round(PROJECTILE_HAND_ANCHOR[1], 3),
            ]
            registration_data["projectileFlightAnchor"] = [
                round(PROJECTILE_FLIGHT_ANCHOR[0], 3),
                round(PROJECTILE_FLIGHT_ANCHOR[1], 3),
            ]
            registration_data["projectileSettleAnchor"] = [
                round(PROJECTILE_SETTLE_ANCHOR[0], 3),
                round(PROJECTILE_SETTLE_ANCHOR[1], 3),
            ]
        data["registration"] = registration_data
    return data


def keyed_frames(raw_path: Path) -> list[Image.Image]:
    """Key the background out of a raw sheet and crop it to normalized frames."""
    keyed = remove_keyed_background(Image.open(raw_path))
    x_bounds = fixed_axis_bounds(keyed.width, GRID_COLUMNS)
    y_bounds = fixed_axis_bounds(keyed.height, GRID_ROWS)
    artifact_repair = CROP_ARTIFACT_REPAIRS.get((COMPANION_SLUG, raw_path.stem), {})
    frames: list[Image.Image] = []
    index = 0
    for y0, y1 in y_bounds:
        for x0, x1 in x_bounds:
            frame = normalize_frame(keyed.crop((x0, y0, x1, y1)))
            edges = {edge for edge, frame_indices in artifact_repair.items() if index in frame_indices}
            frames.append(remove_edge_artifact_components(frame, edges))
            index += 1
    return frames


def union_alpha_bbox(frames: list[Image.Image]) -> tuple[int, int, int, int] | None:
    """Tightest box containing every frame's visible pixels."""
    acc: list[int] | None = None
    for frame in frames:
        box = alpha_bbox(frame, threshold=ALPHA_THRESHOLD)
        if not box:
            continue
        if acc is None:
            acc = list(box)
        else:
            acc[0] = min(acc[0], box[0])
            acc[1] = min(acc[1], box[1])
            acc[2] = max(acc[2], box[2])
            acc[3] = max(acc[3], box[3])
    return tuple(acc) if acc else None  # type: ignore[return-value]


def fit_scale_to_cell(frames: list[Image.Image], margin: int = FIT_MARGIN_PX) -> float:
    """Uniform scale (about the cell centre) that fits every frame in the cell.

    Returns 1.0 when the effect already fits. Otherwise scales down so the widest
    excursion from centre lands `margin` px inside the edge, so no frame clips.
    """
    box = union_alpha_bbox(frames)
    if not box:
        return 1.0
    x0, y0, x1, y1 = box
    centre = FRAME / 2
    worst = max(centre - x0, x1 - centre, centre - y0, y1 - centre)
    avail = centre - margin
    if worst <= avail or worst <= 0:
        return 1.0
    return avail / worst


def scale_frames_about_centre(frames: list[Image.Image], scale: float) -> list[Image.Image]:
    if scale >= 0.999:
        return frames
    return [scale_frame_centered(frame, scale) for frame in frames]


def despill_green_sheet(sheet: Image.Image) -> Image.Image:
    """Final green-spill kill on the composed sheet.

    Despill happens on the raw frames, but the LANCZOS resamples that register,
    fit and scale each frame overshoot and can reintroduce a faint green rim at
    edges. Clamping the green channel to max(R,B) on the finished sheet guarantees
    no green survives anywhere (whites keep R=G=B, purples are already low-green).
    """
    import numpy as np

    arr = np.asarray(sheet.convert("RGBA"), dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    arr[..., 1] = np.minimum(g, np.maximum(r, b))
    return Image.fromarray(arr.astype(np.uint8), mode="RGBA")


def compose_sheet(registered_frames: list[Image.Image]) -> Image.Image:
    sheet = Image.new("RGBA", (FRAME * GRID_COLUMNS, FRAME * GRID_ROWS), (0, 0, 0, 0))
    for index, frame in enumerate(registered_frames):
        col = index % GRID_COLUMNS
        row = index // GRID_COLUMNS
        sheet.alpha_composite(frame, (col * FRAME, row * FRAME))
    sheet = apply_output_palette(sheet)
    if BACKGROUND_MODE == "green-screen":
        sheet = despill_green_sheet(sheet)
    return sheet


def combine_layer_frames(back: list[Image.Image], front: list[Image.Image]) -> list[Image.Image]:
    """Alpha-union of two depth layers per frame - drives a shared registration."""
    combined: list[Image.Image] = []
    for a, b in zip(back, front):
        merged = a.copy()
        merged.alpha_composite(b)
        combined.append(merged)
    return combined


def make_sheet(raw_path: Path, out_path: Path, playback: str, anchor: str = "center") -> dict[str, object]:
    frames = keyed_frames(raw_path)
    registered_frames, registration = register_sequence(frames, playback, anchor)
    registered_frames = scale_frames_about_centre(registered_frames, fit_scale_to_cell(registered_frames))
    sheet = compose_sheet(registered_frames)
    sheet.save(out_path, optimize=True)
    return frame_diagnostics(sheet, playback, registration)


def make_layered_sheets(
    raw_back: Path,
    out_back: Path,
    raw_front: Path,
    out_front: Path,
    playback: str,
    anchor: str = "center",
) -> dict[str, object]:
    """Process a two-layer effect, registering both layers with one shared plan.

    The artist splits a few effects into a `_back` sheet (drawn behind the actor)
    and a `_front` sheet (drawn in front). They must move as one, so the pivot is
    computed from the combined silhouette and applied identically to each layer.
    """
    back_frames = keyed_frames(raw_back)
    front_frames = keyed_frames(raw_front)
    combined = combine_layer_frames(back_frames, front_frames)
    scale, shifts, registration = compute_registration_plan(combined, playback, anchor)
    back_reg = apply_registration_plan(back_frames, scale, shifts)
    front_reg = apply_registration_plan(front_frames, scale, shifts)
    # One shared fit scale, measured on the combined silhouette, keeps the two
    # depth layers aligned and prevents either from clipping the cell.
    fit = fit_scale_to_cell(apply_registration_plan(combined, scale, shifts))
    compose_sheet(scale_frames_about_centre(back_reg, fit)).save(out_back, optimize=True)
    front_sheet = compose_sheet(scale_frames_about_centre(front_reg, fit))
    front_sheet.save(out_front, optimize=True)
    return frame_diagnostics(front_sheet, playback, registration)


def resolved_command_spec(spec: dict[str, str]) -> dict[str, str]:
    """Apply the active companion's per-command playback/anchor overrides."""
    override = COMPANION_COMMAND_OVERRIDES.get(COMPANION_SLUG, {}).get(spec["name"], {})
    merged = dict(spec)
    merged.update(override)
    return merged


def command_layers(name: str) -> list[tuple[str, Path, Path]]:
    """Resolve the raw/output sheets for a command, single or `_back`/`_front`.

    Some effects are authored as two depth layers (`<name>_back.png` drawn behind
    the actor, `<name>_front.png` in front). When both exist we emit both; a plain
    `<name>.png` stays a single sheet. Returns (layer, raw_path, out_path) tuples;
    an empty list means the command has no raw art yet.
    """
    back = RAW_DIR / f"{name}_back.png"
    front = RAW_DIR / f"{name}_front.png"
    single = RAW_DIR / f"{name}.png"
    if back.exists() and front.exists():
        return [
            ("back", back, OUT_DIR / f"{name}_back.png"),
            ("front", front, OUT_DIR / f"{name}_front.png"),
        ]
    if single.exists():
        return [("single", single, OUT_DIR / f"{name}.png")]
    return []


def manifest_entry(name: str, spec: dict[str, object], layered: bool = False) -> dict[str, object]:
    command_family = {
        "checkout-conflict": "checkout",
        "diff-conflict": "diff",
        "default": "default",
        "miss": "miss",
    }.get(name, name)
    base_command = {
        "default": "default",
        "miss": "missed attack",
    }.get(name, f"git {command_family}")
    skill_slug = {
        "default": "default",
        "miss": "missed-attack",
    }.get(name, f"git-{name}")
    tint = INIT_TINT_OVERRIDE if name == "init" and INIT_TINT_OVERRIDE else spec["tint"]
    # Report the runtime placement anchor: body-centered projectiles/auras use
    # "center", while Blue clone and ground-rooted effects use "feet".
    anchor = spec.get("anchor", "center" if spec["playback"] == "projectile" else "feet")
    entry: dict[str, object] = {
        # For layered effects the representative still/showcase uses the front
        # sheet; the depth layers themselves are listed under `layers`.
        "src": f"{EFFECT_BASE_URL}/{name}_front.png" if layered else f"{EFFECT_BASE_URL}/{name}.png",
        "fps": FPS,
        "loops": False,
        "frameWidth": FRAME,
        "frameHeight": FRAME,
        "columns": GRID_COLUMNS,
        "rows": GRID_ROWS,
        "frameCount": FRAMES,
        "tint": tint,
        "motif": f"{MOTIF_PREFIX}{spec['motif']}",
        "playback": spec["playback"],
        "anchor": anchor,
        "commandFamily": command_family,
        "baseCommand": base_command,
        "skillSlug": skill_slug,
        "generationSource": RAW_SOURCE_LABEL,
    }
    if "launchStartFrame" in spec:
        entry["launchStartFrame"] = int(spec["launchStartFrame"])
    if "impactStartFrame" in spec:
        entry["impactStartFrame"] = int(spec["impactStartFrame"])
    if layered:
        entry["layers"] = [
            {"layer": "back", "src": f"{EFFECT_BASE_URL}/{name}_back.png"},
            {"layer": "front", "src": f"{EFFECT_BASE_URL}/{name}_front.png"},
        ]
        entry["rawSrc"] = f"{EFFECT_BASE_URL}/_raw/{name}_front.png"
    else:
        # Only init/add use the gather-orb charge motion; every other projectile
        # (clone, merge, reflog, diff, branch, checkout, stash, default) is a
        # plain charge-fly-impact bolt.
        if name in {"init", "add"}:
            entry["motion"] = INIT_MOTION
        if (RAW_DIR / f"{name}.png").exists():
            entry["rawSrc"] = f"{EFFECT_BASE_URL}/_raw/{name}.png"
    return entry


def write_json_lf(path: Path, data: object) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, indent=2)
        file.write("\n")


def read_json_object(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data if isinstance(data, dict) else {}


def preview_sheet_path(name: str) -> Path | None:
    """Representative still sheet for the contact sheet: single or front layer."""
    single = OUT_DIR / f"{name}.png"
    if single.exists():
        return single
    front = OUT_DIR / f"{name}_front.png"
    if front.exists():
        return front
    return None


def make_preview() -> None:
    tile_w = 246
    tile_h = 166
    cols = 4
    preview_specs = [spec for spec in ALL_EFFECTS if preview_sheet_path(spec["name"]) is not None]
    if not preview_specs:
        return
    rows = math.ceil(len(preview_specs) / cols)
    preview = Image.new("RGBA", (cols * tile_w, rows * tile_h), PREVIEW_BACKGROUND)
    draw = ImageDraw.Draw(preview)
    font = ImageFont.load_default()

    for index, spec in enumerate(preview_specs):
        name = spec["name"]
        x = (index % cols) * tile_w
        y = (index // cols) * tile_h
        sheet = Image.open(preview_sheet_path(name)).convert("RGBA")
        preview_frame = 12
        col = preview_frame % GRID_COLUMNS
        row = preview_frame // GRID_COLUMNS
        frame = sheet.crop((col * FRAME, row * FRAME, (col + 1) * FRAME, (row + 1) * FRAME)).resize(
            (126, 126),
            Image.Resampling.LANCZOS,
        )
        preview.alpha_composite(frame, (x + 60, y + 10))
        draw.text((x + 12, y + 140), name, fill=PREVIEW_NAME_FILL, font=font)
        draw.text((x + 128, y + 140), str(spec["motif"])[:18], fill=PREVIEW_MOTIF_FILL, font=font)

    preview.convert("RGB").save(OUT_DIR / "_preview-contact-sheet.jpg", quality=92, optimize=True)


def split_selected_names(values: list[str] | None) -> set[str] | None:
    if not values:
        return None
    names: set[str] = set()
    for value in values:
        names.update(part.strip() for part in value.split(",") if part.strip())
    return names or None


def selected_specs(specs: list[dict[str, str]], names: set[str] | None) -> list[dict[str, str]]:
    return [spec for spec in specs if names is None or spec["name"] in names]


def base_manifest(existing: dict[str, object] | None = None) -> dict[str, object]:
    manifest = dict(existing or {})
    manifest.update(
        {
            "id": MANIFEST_ID,
            "label": MANIFEST_LABEL,
            "generationMode": GENERATION_MODE,
            "styleReference": STYLE_REFERENCE,
            "frameWidth": FRAME,
            "frameHeight": FRAME,
            "columns": GRID_COLUMNS,
            "rows": GRID_ROWS,
            "frameCount": FRAMES,
            "fps": FPS,
        }
    )
    if CONCEPT_REFERENCE:
        manifest["conceptReference"] = CONCEPT_REFERENCE
    else:
        manifest.pop("conceptReference", None)
    manifest["sprites"] = dict(manifest.get("sprites") or {})
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Post-process companion spell spritesheets.")
    parser.add_argument(
        "--companion",
        default="blue",
        choices=sorted(COMPANION_EFFECT_SETS),
        help="Companion slug to process.",
    )
    parser.add_argument(
        "--effect-set",
        default=None,
        help="Override the configured effect-set directory name.",
    )
    parser.add_argument(
        "--only",
        action="append",
        help="Process only selected effect name(s), comma-separated. Example: --only init",
    )
    return parser.parse_args()


def load_manifest_and_diagnostics(known_names: set[str]) -> tuple[dict[str, object], dict[str, object]]:
    """Merge with whatever is already on disk and drop entries for removed effects.

    Always merging (rather than starting fresh on a full run) matters once a
    companion can have partial raw coverage: a full run must not wipe the
    manifest/diagnostics entries for commands that have no raw sheet yet.
    """
    manifest = base_manifest(read_json_object(OUT_DIR / "manifest.json"))
    diagnostics = read_json_object(OUT_DIR / "_diagnostics.json")
    sprites = manifest["sprites"]
    if not isinstance(sprites, dict):
        sprites = {}
        manifest["sprites"] = sprites
    for stale_name in set(sprites) - known_names:
        del sprites[stale_name]
    for stale_name in set(diagnostics) - known_names:
        del diagnostics[stale_name]
    return manifest, diagnostics


def main() -> None:
    args = parse_args()
    configure_effect_set(args.companion, args.effect_set)
    selected_names = split_selected_names(args.only)
    known_names = {spec["name"] for spec in ALL_EFFECTS}
    unknown_names = sorted((selected_names or set()) - known_names)
    if unknown_names:
        raise SystemExit(f"Unknown effect name(s): {', '.join(unknown_names)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    command_specs = selected_specs(COMMANDS, selected_names)
    external_specs = selected_specs(EXTERNALLY_SUPPLIED_EFFECTS, selected_names)

    if REQUIRE_COMPLETE_RAW_COVERAGE:
        # Only the generated command sheets must be complete for a companion that
        # claims full coverage. Externally-supplied sheets (miss) are hand-authored
        # and simply skipped when absent, exactly as they are for the other
        # companions - a missing one is a content gap, not a processing error.
        missing = [spec["name"] for spec in command_specs if not command_layers(spec["name"])]
        if missing:
            raise SystemExit(f"Missing raw generated sheets: {', '.join(missing)}")

    manifest, diagnostics = load_manifest_and_diagnostics(known_names)
    sprites = manifest["sprites"]
    skipped: list[str] = []

    for spec in command_specs:
        name = spec["name"]
        layers = command_layers(name)
        if not layers:
            skipped.append(name)
            continue
        resolved = resolved_command_spec(spec)
        playback = resolved["playback"]
        anchor = resolved.get("anchor", "center")
        if len(layers) == 1:
            _, raw_path, out_path = layers[0]
            diagnostics[name] = make_sheet(raw_path, out_path, playback, anchor)
            # Drop stale depth-layer exports from before this effect was flattened.
            (OUT_DIR / f"{name}_back.png").unlink(missing_ok=True)
            (OUT_DIR / f"{name}_front.png").unlink(missing_ok=True)
        else:
            (_, raw_back, out_back), (_, raw_front, out_front) = layers
            diagnostics[name] = make_layered_sheets(
                raw_back, out_back, raw_front, out_front, playback, anchor
            )
            # Drop a stale single-layer export from before this effect was split.
            (OUT_DIR / f"{name}.png").unlink(missing_ok=True)
        sprites[name] = manifest_entry(name, resolved, layered=len(layers) > 1)

    for spec in external_specs:
        name = spec["name"]
        out_path = OUT_DIR / f"{name}.png"
        if not out_path.exists():
            skipped.append(name)
            continue
        sheet = Image.open(out_path).convert("RGBA")
        diagnostics[name] = frame_diagnostics(sheet, spec["playback"])
        sprites[name] = manifest_entry(name, spec)

    if skipped:
        print(f"Skipped (no sheet yet for '{COMPANION_SLUG}'): {', '.join(skipped)}")

    write_json_lf(OUT_DIR / "manifest.json", manifest)
    write_json_lf(OUT_DIR / "_diagnostics.json", diagnostics)
    make_preview()


if __name__ == "__main__":
    main()
