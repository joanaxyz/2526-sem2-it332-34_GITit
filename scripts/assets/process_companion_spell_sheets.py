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
  they have no visual pixels to register. A phase-local temporal guard only
  damps isolated one-frame corrections; it never smooths across charge, flight,
  and impact boundaries or replaces a fading frame's own anchor wholesale.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
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
# the effect at the frame edge. The extractor keys the full sheet, labels alpha
# components globally, assigns each component to one owning frame, and then fits
# those reclaimed pixels inside the cell before registration shifts run.
FIT_MARGIN_PX = 12

# Alpha threshold used for finding the actual effect body.
ALPHA_THRESHOLD = 12

# If the detected anchor is wildly wrong because a frame is nearly empty, do not
# allow an extreme correction to throw the whole effect across the cell.
MAX_REGISTRATION_SHIFT = 96

# Registration follows the authored pixels frame by frame, but changing sparks
# and brightness peaks can make the correction track chatter. At 18 fps that
# reads as camera shake even when every individual frame is mathematically
# centered. Blend toward a short, phase-local motion path while retaining enough
# of each frame's own correction to keep late fade particles on the pivot.
TEMPORAL_REGISTRATION_RADIUS = 2
TEMPORAL_REGISTRATION_RAW_WEIGHT = 0.35
MAX_TEMPORAL_REGISTRATION_ADJUSTMENT = 18

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

# Feet-anchored (ground-rooted) effects try to plant their visible base on this
# line. If an authored frame is too large to move there intact, registration is
# clamped instead of shrinking the entire sheet; the measured placeAnchor then
# tells the runtime where those pixels actually settled.
GROUND_ANCHOR_Y = FRAME * 0.86
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
# monster's rendered box at runtime (see useBattleDirector), so a large monster
# gets a proportionally larger effect than a small monster.
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
        "add": {"anchor": "center", "launchStartFrame": 10, "impactStartFrame": 15},
        "branch": {"anchor": "center", "impactStartFrame": 17},
        "checkout": {"impactStartFrame": 20},
        "merge": {"anchor": "feet", "impactStartFrame": 18},
        "ls-files": {"anchor": "center"},
        "stash": {"anchor": "feet", "impactStartFrame": 13},
    },
    "blue": {"add": {"launchStartFrame": 3, "impactStartFrame": 16}},
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


class OwnedFrameSource(NamedTuple):
    image: Image.Image | None
    source_bbox: tuple[int, int, int, int] | None
    cell_box: tuple[int, int, int, int]


class CroppedPixelError(RuntimeError):
    """Raised when processing would discard visible effect pixels."""


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


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def measure_place_anchor(
    sheet: Image.Image,
    playback: str,
    anchor: str,
    impact_start: int | None = None,
) -> dict[str, float] | None:
    """Report, from the baked pixels, the normalized (0..1) frame point the
    runtime should pin to the target while the effect rests on it.

    This is the pixel-truth counterpart to the fixed FEET_ANCHOR/CENTER_ANCHOR
    fractions the frontend otherwise assumes (0.86 ground line / cell centre).
    Anchoring off those fractions is fragile: they are only correct if the bake
    lands the visible art on that exact line every reprocess, so any drift in
    registration or a hand-dropped sheet silently floats the effect. Measuring
    where the pixels actually settled removes that assumption.

    - projectile: measured over the impact/dissipate frames (what settles on the
      target); that is where the impact anchor is used.
    - target/ground: measured over every non-empty frame (it plays in place).
    horizontal (x): median of the content-box centre across those frames.
    vertical (y):   feet/ground -> median of the content-box BASE (planted edge);
                    center      -> median of the content-box centre.
    """
    if playback not in {"projectile", "target", "ground"}:
        return None
    sheet = sheet.convert("RGBA")
    if playback == "projectile":
        start = PROJECTILE_SETTLE_START_FRAME if impact_start is None else impact_start
        frame_range = range(max(0, min(FRAMES - 1, start)), FRAMES)
    else:
        frame_range = range(FRAMES)
    grounded = playback == "ground" or anchor == "feet"
    centers_x: list[float] = []
    verticals: list[float] = []
    for index in frame_range:
        col = index % GRID_COLUMNS
        row = index // GRID_COLUMNS
        frame = sheet.crop((col * FRAME, row * FRAME, (col + 1) * FRAME, (row + 1) * FRAME))
        bbox = alpha_bbox(frame, threshold=ALPHA_THRESHOLD)
        if not bbox:
            continue
        x0, y0, x1, y1 = bbox
        centers_x.append((x0 + x1) / 2)
        verticals.append(y1 if grounded else (y0 + y1) / 2)
    if not centers_x:
        return None
    return {
        "x": round(_median(centers_x) / FRAME, 4),
        "y": round(_median(verticals) / FRAME, 4),
    }


def measure_place_bounds(
    sheet: Image.Image,
    playback: str,
    impact_start: int | None = None,
) -> dict[str, float] | None:
    """Union of visible planted/impact pixels, normalized to the frame.

    Runtime containment must fit the VFX silhouette, not the transparent 256px
    cell. Projectile bounds therefore cover impact frames only; target/ground
    bounds cover the full in-place animation.
    """
    if playback not in {"projectile", "target", "ground"}:
        return None
    sheet = sheet.convert("RGBA")
    if playback == "projectile":
        start = PROJECTILE_SETTLE_START_FRAME if impact_start is None else impact_start
        frame_range = range(max(0, min(FRAMES - 1, start)), FRAMES)
    else:
        frame_range = range(FRAMES)
    union: list[int] | None = None
    for index in frame_range:
        col = index % GRID_COLUMNS
        row = index // GRID_COLUMNS
        frame = sheet.crop((col * FRAME, row * FRAME, (col + 1) * FRAME, (row + 1) * FRAME))
        bbox = alpha_bbox(frame, threshold=ALPHA_THRESHOLD)
        if not bbox:
            continue
        if union is None:
            union = list(bbox)
        else:
            union[0] = min(union[0], bbox[0])
            union[1] = min(union[1], bbox[1])
            union[2] = max(union[2], bbox[2])
            union[3] = max(union[3], bbox[3])
    if union is None:
        return None
    pad = 2
    left, top, right, bottom = union
    return {
        "left": round(max(0, left - pad) / FRAME, 4),
        "top": round(max(0, top - pad) / FRAME, 4),
        "right": round(min(FRAME, right + pad) / FRAME, 4),
        "bottom": round(min(FRAME, bottom + pad) / FRAME, 4),
    }


def attach_place_anchor(entry: dict[str, object]) -> None:
    """Attach pixel placement geometry from an entry's baked sheet."""
    src = str(entry.get("src", ""))
    if not src:
        return
    sheet_path = OUT_DIR / Path(src).name
    if not sheet_path.exists():
        return
    try:
        sheet = Image.open(sheet_path)
    except OSError:
        return
    impact_start = entry.get("impactStartFrame")
    measured = measure_place_anchor(
        sheet,
        str(entry.get("playback", "target")),
        str(entry.get("anchor", "center")),
        int(impact_start) if isinstance(impact_start, (int, float)) else None,
    )
    if measured is not None:
        entry["placeAnchor"] = measured
    bounds = measure_place_bounds(
        sheet,
        str(entry.get("playback", "target")),
        int(impact_start) if isinstance(impact_start, (int, float)) else None,
    )
    if bounds is not None:
        entry["placeBounds"] = bounds


def _format_edge_counts(edge_counts: dict[str, int]) -> str:
    return ", ".join(f"{edge}={count}" for edge, count in edge_counts.items() if count)


def visible_edge_pixel_counts(
    frame: Image.Image,
    edge: int,
    threshold: int = ALPHA_THRESHOLD,
) -> tuple[int, dict[str, int]]:
    alpha = frame.getchannel("A")
    w, h = frame.size
    px = alpha.load()
    seen: set[tuple[int, int]] = set()
    total = 0
    counts = {"top": 0, "bottom": 0, "left": 0, "right": 0}

    def visit(x: int, y: int, edge_name: str) -> None:
        nonlocal total
        if px[x, y] <= threshold:
            return
        counts[edge_name] += 1
        if (x, y) not in seen:
            seen.add((x, y))
            total += 1

    for y in range(edge):
        for x in range(w):
            visit(x, y, "top")
    for y in range(max(edge, h - edge), h):
        for x in range(w):
            visit(x, y, "bottom")
    for y in range(edge, max(edge, h - edge)):
        for x in range(edge):
            visit(x, y, "left")
        for x in range(max(edge, w - edge), w):
            visit(x, y, "right")
    return total, counts


def assert_no_visible_edge_crop(frame: Image.Image, context: str) -> None:
    edge = max(1, min(EDGE_CLEAR_PX, frame.width, frame.height))
    total, counts = visible_edge_pixel_counts(frame, edge)
    if total:
        raise CroppedPixelError(
            f"Pixel crop detected in {context}: edge cleanup would clear "
            f"{total} visible pixel(s) in the outer {edge}px strip "
            f"({_format_edge_counts(counts)})."
        )


def assert_shift_keeps_visible_pixels(frame: Image.Image, dx: int, dy: int, context: str) -> None:
    bbox = alpha_bbox(frame, threshold=ALPHA_THRESHOLD)
    if not bbox:
        return

    alpha = frame.getchannel("A")
    px = alpha.load()
    w, h = frame.size
    x0, y0, x1, y1 = bbox
    if 0 <= x0 + dx and x1 + dx <= w and 0 <= y0 + dy and y1 + dy <= h:
        return

    clipped = 0
    counts = {"top": 0, "bottom": 0, "left": 0, "right": 0}
    for y in range(y0, y1):
        for x in range(x0, x1):
            if px[x, y] <= ALPHA_THRESHOLD:
                continue
            shifted_x = x + dx
            shifted_y = y + dy
            if 0 <= shifted_x < w and 0 <= shifted_y < h:
                continue
            clipped += 1
            if shifted_y < 0:
                counts["top"] += 1
            if shifted_y >= h:
                counts["bottom"] += 1
            if shifted_x < 0:
                counts["left"] += 1
            if shifted_x >= w:
                counts["right"] += 1

    if clipped:
        raise CroppedPixelError(
            f"Pixel crop detected in {context}: registration shift ({dx}, {dy}) would move "
            f"{clipped} visible pixel(s) outside the {w}x{h} frame "
            f"({_format_edge_counts(counts)}); source bbox={bbox}."
        )


def assert_paste_keeps_visible_pixels(
    overlay: Image.Image,
    dest: tuple[int, int],
    base_size: tuple[int, int],
    context: str,
) -> None:
    x, y = dest
    base_w, base_h = base_size
    bbox = alpha_bbox(overlay, threshold=ALPHA_THRESHOLD)
    if not bbox:
        return
    x0, y0, x1, y1 = bbox
    if 0 <= x + x0 and x + x1 <= base_w and 0 <= y + y0 and y + y1 <= base_h:
        return

    alpha = overlay.getchannel("A")
    px = alpha.load()
    clipped = 0
    counts = {"top": 0, "bottom": 0, "left": 0, "right": 0}
    for py in range(y0, y1):
        for px_x in range(x0, x1):
            if px[px_x, py] <= ALPHA_THRESHOLD:
                continue
            target_x = x + px_x
            target_y = y + py
            if 0 <= target_x < base_w and 0 <= target_y < base_h:
                continue
            clipped += 1
            if target_y < 0:
                counts["top"] += 1
            if target_y >= base_h:
                counts["bottom"] += 1
            if target_x < 0:
                counts["left"] += 1
            if target_x >= base_w:
                counts["right"] += 1

    if clipped:
        raise CroppedPixelError(
            f"Pixel crop detected in {context}: owned crop paste at {dest} would move "
            f"{clipped} visible pixel(s) outside the {base_w}x{base_h} frame "
            f"({_format_edge_counts(counts)}); source bbox={bbox}."
        )


def clear_frame_edges(frame: Image.Image, context: str = "frame edge cleanup") -> Image.Image:
    frame = frame.convert("RGBA")
    assert_no_visible_edge_crop(frame, context)
    edge = max(1, EDGE_CLEAR_PX)
    low_alpha_total, _counts = visible_edge_pixel_counts(frame, edge, threshold=0)
    if low_alpha_total:
        # Do not shave antialiased wisps or faint particles. Hard crops are
        # caught above with ALPHA_THRESHOLD; anything softer is safer to preserve
        # than to erase from a generated effect sheet.
        return frame
    alpha = frame.getchannel("A")
    draw = ImageDraw.Draw(alpha)
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


def shifted_frame(frame: Image.Image, dx: int, dy: int, context: str = "frame shift") -> Image.Image:
    frame = frame.convert("RGBA")
    assert_shift_keeps_visible_pixels(frame, dx, dy, context)
    out = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    out.alpha_composite(frame, (dx, dy))
    return out


def clamp_int(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def fixed_axis_bounds(length: int, count: int) -> list[tuple[int, int]]:
    points = [round(index * length / count) for index in range(count + 1)]
    return [(points[i], points[i + 1]) for i in range(count)]


def frame_cell_boxes(width: int, height: int) -> list[tuple[int, int, int, int]]:
    x_bounds = fixed_axis_bounds(width, GRID_COLUMNS)
    y_bounds = fixed_axis_bounds(height, GRID_ROWS)
    return [(x0, y0, x1, y1) for y0, y1 in y_bounds for x0, x1 in x_bounds]


def owned_frame_sources(raw_path: Path) -> list[OwnedFrameSource]:
    """Key a whole sheet and assign visible components back to their source frame.

    Several generated sheets draw a frame's art past its nominal grid cell. A
    direct cell crop cuts that spillover away; expanding every crop blindly pulls
    in neighboring frames. This global pass keeps connected effect components
    whole and assigns each component to the grid cell containing most of its
    visible alpha, so a frame can reclaim its own overflow without borrowing the
    next frame's art.
    """
    import numpy as np
    from scipy import ndimage

    keyed = remove_keyed_background(Image.open(raw_path)).convert("RGBA")
    arr = np.asarray(keyed)
    alpha = arr[..., 3]
    component_mask = alpha > max(1, ALPHA_THRESHOLD // 3)
    cell_boxes = frame_cell_boxes(keyed.width, keyed.height)
    if not component_mask.any():
        return [OwnedFrameSource(None, None, cell_box) for cell_box in cell_boxes]

    structure = np.ones((3, 3), dtype=np.uint8)
    labels, _count = ndimage.label(component_mask, structure=structure)
    slices = ndimage.find_objects(labels)
    owner_map = np.full(component_mask.shape, -1, dtype=np.int16)
    x_edges = np.array([cell_boxes[0][0], *[box[2] for box in cell_boxes[:GRID_COLUMNS]]])
    y_edges = np.array([cell_boxes[row * GRID_COLUMNS][1] for row in range(GRID_ROWS)] + [cell_boxes[-1][3]])

    for label, region_slice in enumerate(slices, start=1):
        if region_slice is None:
            continue
        region_labels = labels[region_slice]
        region = region_labels == label
        if not region.any():
            continue

        ys, xs = np.nonzero(region)
        gy = ys + region_slice[0].start
        gx = xs + region_slice[1].start
        weights = alpha[gy, gx].astype(np.float64)
        cols = np.searchsorted(x_edges, gx, side="right") - 1
        rows = np.searchsorted(y_edges, gy, side="right") - 1
        valid = (0 <= cols) & (cols < GRID_COLUMNS) & (0 <= rows) & (rows < GRID_ROWS)
        if not valid.any():
            continue

        frame_ids = (rows[valid] * GRID_COLUMNS + cols[valid]).astype(np.int32)
        totals = np.bincount(frame_ids, weights=weights[valid], minlength=FRAMES)
        owner = int(np.argmax(totals))
        if totals[owner] <= 0:
            continue
        occupied = np.flatnonzero(totals > 0)
        occupied_rows = occupied // GRID_COLUMNS
        occupied_cols = occupied % GRID_COLUMNS
        dominance = float(totals[owner] / totals.sum()) if totals.sum() > 0 else 1.0
        ambiguous_multi_frame = len(occupied) > 1 and dominance < 0.72
        spans_too_many_cells = (
            len(occupied) > 4
            or (len(occupied_cols) and int(occupied_cols.max() - occupied_cols.min() + 1) > 2)
            or (len(occupied_rows) and int(occupied_rows.max() - occupied_rows.min() + 1) > 2)
        )
        if spans_too_many_cells or ambiguous_multi_frame:
            # Separate frames can become one alpha component when wisps touch
            # across grid seams. Giving that sheet-wide component to one frame
            # makes compute_prefit_scale shrink every frame (occasionally to
            # ~10%). A component with no clear majority owner is the same case
            # even when it only joins two adjacent frames. Keep each visible
            # pixel with its own source cell instead.
            owner_map[gy[valid], gx[valid]] = frame_ids
        else:
            # A compact component may genuinely spill over one adjacent cell;
            # keep it whole so its sparks are not sliced at the grid boundary.
            owner_map[gy, gx] = owner

    sources: list[OwnedFrameSource] = []
    alpha_present = alpha > 0
    for index, cell_box in enumerate(cell_boxes):
        frame_mask = owner_map == index
        if not frame_mask.any():
            sources.append(OwnedFrameSource(None, None, cell_box))
            continue

        # Pull in the feathered edge pixels attached to the owned component, but
        # only where the keyed sheet still has alpha.
        copy_mask = ndimage.binary_dilation(frame_mask, structure=structure, iterations=1) & alpha_present
        ys, xs = np.nonzero(copy_mask)
        x0 = int(xs.min())
        x1 = int(xs.max()) + 1
        y0 = int(ys.min())
        y1 = int(ys.max()) + 1

        crop_arr = np.zeros((y1 - y0, x1 - x0, 4), dtype=np.uint8)
        local_mask = copy_mask[y0:y1, x0:x1]
        crop_arr[local_mask] = arr[y0:y1, x0:x1][local_mask]
        sources.append(
            OwnedFrameSource(
                Image.fromarray(crop_arr, mode="RGBA"),
                (x0, y0, x1, y1),
                cell_box,
            )
        )
    return sources


def compute_prefit_scale(sources: list[OwnedFrameSource], margin: int = FIT_MARGIN_PX) -> float:
    """Shared pre-scale that fits reclaimed cell spillover before 256px render."""
    centre = FRAME / 2
    worst = 0.0
    for source in sources:
        if source.source_bbox is None:
            continue
        cell_x0, cell_y0, cell_x1, cell_y1 = source.cell_box
        box_x0, box_y0, box_x1, box_y1 = source.source_bbox
        cell_cx = (cell_x0 + cell_x1) / 2
        cell_cy = (cell_y0 + cell_y1) / 2
        base_sx = FRAME / max(1, cell_x1 - cell_x0)
        base_sy = FRAME / max(1, cell_y1 - cell_y0)
        worst = max(
            worst,
            abs((box_x0 - cell_cx) * base_sx),
            abs((box_x1 - cell_cx) * base_sx),
            abs((box_y0 - cell_cy) * base_sy),
            abs((box_y1 - cell_cy) * base_sy),
        )
    available = centre - margin
    if worst <= available or worst <= 0:
        return 1.0
    return available / worst


def alpha_composite_clipped(
    base: Image.Image,
    overlay: Image.Image,
    dest: tuple[int, int],
    context: str,
) -> None:
    assert_paste_keeps_visible_pixels(overlay, dest, base.size, context)
    x, y = dest
    src_left = max(0, -x)
    src_top = max(0, -y)
    src_right = min(overlay.width, base.width - x)
    src_bottom = min(overlay.height, base.height - y)
    if src_right <= src_left or src_bottom <= src_top:
        return
    base.alpha_composite(overlay.crop((src_left, src_top, src_right, src_bottom)), (x + src_left, y + src_top))


def render_frame_source(source: OwnedFrameSource, prefit_scale: float, context: str) -> Image.Image:
    out = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    if source.image is None or source.source_bbox is None:
        return out

    cell_x0, cell_y0, cell_x1, cell_y1 = source.cell_box
    box_x0, box_y0, _, _ = source.source_bbox
    cell_cx = (cell_x0 + cell_x1) / 2
    cell_cy = (cell_y0 + cell_y1) / 2
    scale_x = (FRAME / max(1, cell_x1 - cell_x0)) * prefit_scale
    scale_y = (FRAME / max(1, cell_y1 - cell_y0)) * prefit_scale
    resized = source.image.resize(
        (max(1, round(source.image.width * scale_x)), max(1, round(source.image.height * scale_y))),
        Image.Resampling.LANCZOS,
    )
    paste_x = round(FRAME / 2 + (box_x0 - cell_cx) * scale_x)
    paste_y = round(FRAME / 2 + (box_y0 - cell_cy) * scale_y)
    alpha_composite_clipped(out, resized, (paste_x, paste_y), context)
    return out


def render_frame_sources(
    sources: list[OwnedFrameSource],
    prefit_scale: float | None = None,
    context: str = "owned crop",
) -> list[Image.Image]:
    scale = compute_prefit_scale(sources) if prefit_scale is None else prefit_scale
    return [render_frame_source(source, scale, f"{context} frame {index}") for index, source in enumerate(sources)]


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


def projectile_phase_bounds(
    launch_start: int | None,
    impact_start: int | None,
) -> tuple[int, int]:
    """Clamp authored zero-based projectile phase boundaries to this sheet."""
    launch = clamp_int(
        PROJECTILE_LAUNCH_START_FRAME if launch_start is None else int(launch_start),
        1,
        FRAMES - 2,
    )
    impact = clamp_int(
        PROJECTILE_SETTLE_START_FRAME if impact_start is None else int(impact_start),
        launch + 1,
        FRAMES - 1,
    )
    return launch, impact


def detect_registration_anchor(
    frame: Image.Image,
    playback: str,
    index: int,
    anchor: str = "center",
    launch_start: int | None = None,
    impact_start: int | None = None,
) -> FrameAnchor | None:
    if playback != "projectile":
        return detect_effect_anchor(frame, playback)
    launch, impact = projectile_phase_bounds(launch_start, impact_start)
    if launch <= index < impact:
        return detect_projectile_nose_anchor(frame)
    if index >= impact and anchor == "feet":
        return detect_feet_anchor(frame)
    return detect_effect_anchor(frame, "target")


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


def registration_phase_ranges(
    frame_count: int,
    playback: str,
    launch_start: int | None = None,
    impact_start: int | None = None,
) -> list[tuple[int, int]]:
    """Return half-open ranges that may be stabilized independently.

    Projectile sheets intentionally change pivots between gather, flight, and
    impact. Treating that authored pivot switch as jitter would bend the launch
    or pull the impact away from its target, so temporal filtering never crosses
    those boundaries. In-place and ground-travel effects use one continuous
    phase.
    """
    if frame_count <= 0:
        return []
    if playback != "projectile":
        return [(0, frame_count)]
    launch, impact = projectile_phase_bounds(launch_start, impact_start)
    cuts = sorted({0, min(frame_count, launch), min(frame_count, impact), frame_count})
    return [(start, end) for start, end in zip(cuts, cuts[1:]) if start < end]


def stabilize_registration_shifts(
    shifts: list[tuple[int, int]],
    playback: str,
    launch_start: int | None = None,
    impact_start: int | None = None,
    radius: int = TEMPORAL_REGISTRATION_RADIUS,
    raw_weight: float = TEMPORAL_REGISTRATION_RAW_WEIGHT,
    max_adjustment: int = MAX_TEMPORAL_REGISTRATION_ADJUSTMENT,
) -> list[tuple[int, int]]:
    """Low-pass the correction track without erasing authored movement.

    A five-frame triangular window produces a continuous local path. Each frame
    retains a meaningful share of its pixel-derived correction, and a hard cap
    limits how far stabilization can move it. Projectile flight keeps its raw
    vertical correction so the detected nose stays on one exact horizontal
    axis; only its horizontal correction is damped. This keeps weak fade frames
    near their own remaining pixels while removing whole-cell chatter caused by
    following every transient spark exactly.
    """
    if len(shifts) < 2 or radius <= 0 or max_adjustment < 0:
        return list(shifts)

    own_weight = max(0.0, min(1.0, raw_weight))
    stabilized = list(shifts)
    flight_bounds = projectile_phase_bounds(launch_start, impact_start) if playback == "projectile" else None
    for start, end in registration_phase_ranges(len(shifts), playback, launch_start, impact_start):
        for index in range(start, end):
            window_start = max(start, index - radius)
            window_end = min(end, index + radius + 1)
            weighted_x = 0.0
            weighted_y = 0.0
            total_weight = 0.0
            for sample in range(window_start, window_end):
                weight = float(radius + 1 - abs(sample - index))
                weighted_x += shifts[sample][0] * weight
                weighted_y += shifts[sample][1] * weight
                total_weight += weight
            if total_weight <= 0:
                continue
            trend_x = weighted_x / total_weight
            trend_y = weighted_y / total_weight
            current_x, current_y = shifts[index]
            blended_x = round(current_x * own_weight + trend_x * (1.0 - own_weight))
            blended_y = round(current_y * own_weight + trend_y * (1.0 - own_weight))
            preserve_flight_axis = (
                flight_bounds is not None and flight_bounds[0] <= index < flight_bounds[1]
            )
            stabilized[index] = (
                clamp_int(blended_x, current_x - max_adjustment, current_x + max_adjustment),
                current_y
                if preserve_flight_axis
                else clamp_int(blended_y, current_y - max_adjustment, current_y + max_adjustment),
            )
    return stabilized


def _feet_registration_plan(
    frames: list[Image.Image], ground_travel: bool
) -> tuple[float, list[tuple[int, int]], RegistrationDebug]:
    """Plant a ground-rooted sequence's base on the ground line.

    Risers (tornado, geyser, floor ring) keep a stable horizontal core and grow
    upward, so we centre the core x and shift each frame so its visible base sits
    on GROUND_ANCHOR_Y. Ground-travel effects (push, switch) instead preserve
    their internal forward motion - the whole sequence is centred by one constant
    x shift - and the runtime slides them from caster to enemy. Oversized frames
    keep their authored scale; the final registration shift is clamped to the
    cell and the runtime uses the measured pixel anchor.
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
            else "feet-planted base on ground line when bounds allow, core-x centred"
        ),
    )
    return 1.0, shifts, debug


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
    frames: list[Image.Image],
    playback: str,
    anchor: str,
    launch_start: int | None,
    impact_start: int | None,
) -> tuple[float, list[tuple[int, int]], RegistrationDebug]:
    launch, impact = projectile_phase_bounds(launch_start, impact_start)
    anchors = [
        detect_registration_anchor(frame, playback, index, anchor, launch, impact)
        for index, frame in enumerate(frames)
    ]
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
            if index < launch:
                return PROJECTILE_HAND_ANCHOR
            if index < impact:
                return PROJECTILE_FLIGHT_ANCHOR
            return (FRAME * 0.5, GROUND_ANCHOR_Y) if anchor == "feet" else PROJECTILE_SETTLE_ANCHOR
        return sequence_target

    shift_by_index: dict[int, tuple[int, int]] = {}

    for index, detected in enumerate(anchors):
        if detected is None:
            continue
        target_x, target_y = target_for_frame(index)
        dx = clamp_int(round(target_x - detected.x), -MAX_REGISTRATION_SHIFT, MAX_REGISTRATION_SHIFT)
        dy = clamp_int(round(target_y - detected.y), -MAX_REGISTRATION_SHIFT, MAX_REGISTRATION_SHIFT)
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
            f"hand-center anchor until frame {launch - 1}, "
            f"projectile nose anchor through frame {impact - 1}, "
            f"{anchor} anchor for impact/dissipate frames"
        )
        if playback == "projectile"
        else "sequence weighted-median energy-core pivot for all visible frames",
    )
    return 1.0, shifts, debug


def compute_registration_plan(
    frames: list[Image.Image],
    playback: str,
    anchor: str = "center",
    launch_start: int | None = None,
    impact_start: int | None = None,
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
    return _projectile_target_plan(frames, playback, anchor, launch_start, impact_start)


def clamp_registration_shifts(
    frames: list[Image.Image],
    shifts: list[tuple[int, int]],
    margin: int = EDGE_CLEAR_PX,
) -> list[tuple[int, int]]:
    """Keep authored pixels intact by limiting translation, never sheet scale.

    A fixed semantic target (cell centre, projectile nose, or ground line) can
    be unreachable for a very large frame. The old fallback uniformly shrank
    all 25 frames to accommodate that one excursion. Clamp only the offending
    frame's translation; placeAnchor records the resulting pixel truth for the
    target/impact phases.
    """
    clamped: list[tuple[int, int]] = []
    last_shift = (0, 0)
    for index, frame in enumerate(frames):
        desired_x, desired_y = shifts[index] if index < len(shifts) else last_shift
        last_shift = (desired_x, desired_y)
        bbox = frame.getchannel("A").getbbox()
        if not bbox:
            clamped.append((desired_x, desired_y))
            continue
        x0, y0, x1, y1 = bbox
        min_x = margin - x0
        max_x = FRAME - margin - x1
        min_y = margin - y0
        max_y = FRAME - margin - y1
        safe_x = 0 if min_x > max_x else clamp_int(desired_x, min_x, max_x)
        safe_y = 0 if min_y > max_y else clamp_int(desired_y, min_y, max_y)
        clamped.append((safe_x, safe_y))
    return clamped


def registration_debug_with_actual_shifts(
    debug: RegistrationDebug,
    shifts: list[tuple[int, int]],
) -> RegistrationDebug:
    if not shifts:
        return debug
    xs = [shift[0] for shift in shifts]
    ys = [shift[1] for shift in shifts]
    suffix = " (bounds-clamped; authored scale preserved)"
    mode = debug.mode if suffix in debug.mode else f"{debug.mode}{suffix}"
    return debug._replace(
        applied_shift_range=[min(xs), max(xs), min(ys), max(ys)],
        mode=mode,
    )


def apply_registration_plan(
    frames: list[Image.Image],
    scale: float,
    shifts: list[tuple[int, int]],
    context: str = "registration",
) -> list[Image.Image]:
    scaled = [scale_frame_centered(frame, scale) for frame in frames] if scale < 0.999 else frames
    registered: list[Image.Image] = []
    last_shift = (0, 0)
    for index, frame in enumerate(scaled):
        dx, dy = shifts[index] if index < len(shifts) else last_shift
        last_shift = (dx, dy)
        shifted = shifted_frame(frame, dx, dy, f"{context} frame {index}")
        registered.append(clear_frame_edges(shifted, f"{context} frame {index} cleanup"))
    return registered


def register_sequence(
    frames: list[Image.Image],
    playback: str,
    anchor: str = "center",
    launch_start: int | None = None,
    impact_start: int | None = None,
    context: str = "registration",
) -> tuple[list[Image.Image], RegistrationDebug]:
    """Register all frames to one stable sequence anchor.

    Target effects use the weighted median of reliable energy-core anchors for
    the whole sequence. Init-style projectile sheets use the center hand anchor
    for gather/orb frames, the frontend's nose anchor for launch frames, and the
    center settle anchor for impact/fade frames. Ground-rooted effects (feet
    anchor or ground playback) plant their base on the ground line. Only frames
    with no detectable pixels inherit an interpolated shift.
    """
    scale, shifts, debug = compute_registration_plan(
        frames,
        playback,
        anchor,
        launch_start,
        impact_start,
    )
    safe_shifts = clamp_registration_shifts(frames, shifts)
    stable_shifts = stabilize_registration_shifts(
        safe_shifts,
        playback,
        launch_start,
        impact_start,
    )
    # Interpolating between individually safe shifts is usually safe, but each
    # frame has different visible bounds. Re-clamp after temporal stabilization
    # so the anti-jitter pass can never trade steadiness for cropped pixels.
    safe_shifts = clamp_registration_shifts(frames, stable_shifts)
    debug = registration_debug_with_actual_shifts(debug, safe_shifts)
    return apply_registration_plan(frames, scale, safe_shifts, context), debug


def frame_diagnostics(
    sheet: Image.Image,
    playback: str,
    registration: RegistrationDebug | None = None,
    anchor: str = "center",
    launch_start: int | None = None,
    impact_start: int | None = None,
) -> dict[str, object]:
    alpha = sheet.getchannel("A")
    centers: list[tuple[float, float]] = []
    anchors: list[FrameAnchor] = []
    registration_anchors: list[FrameAnchor] = []
    projectile_hand_anchors: list[FrameAnchor] = []
    projectile_flight_anchors: list[FrameAnchor] = []
    projectile_settle_anchors: list[FrameAnchor] = []
    launch, impact = projectile_phase_bounds(launch_start, impact_start)

    for index in range(FRAMES):
        col = index % GRID_COLUMNS
        row = index // GRID_COLUMNS
        frame = sheet.crop((col * FRAME, row * FRAME, (col + 1) * FRAME, (row + 1) * FRAME))
        bbox = alpha_bbox(frame, threshold=ALPHA_THRESHOLD)
        if bbox:
            x0, y0, x1, y1 = bbox
            centers.append(((x0 + x1) / 2, (y0 + y1) / 2))
        energy_anchor = detect_effect_anchor(frame, playback)
        if energy_anchor:
            anchors.append(energy_anchor)
        registration_anchor = detect_registration_anchor(
            frame,
            playback,
            index,
            anchor,
            launch_start,
            impact_start,
        )
        if registration_anchor:
            if playback == "projectile":
                if index < launch:
                    projectile_hand_anchors.append(registration_anchor)
                elif index < impact:
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
            registration_data["projectileLaunchStartFrame"] = launch
            registration_data["projectileSettleStartFrame"] = impact
            registration_data["projectileHandAnchor"] = [
                round(PROJECTILE_HAND_ANCHOR[0], 3),
                round(PROJECTILE_HAND_ANCHOR[1], 3),
            ]
            registration_data["projectileFlightAnchor"] = [
                round(PROJECTILE_FLIGHT_ANCHOR[0], 3),
                round(PROJECTILE_FLIGHT_ANCHOR[1], 3),
            ]
            registration_data["projectileSettleAnchor"] = [
                round(FRAME * 0.5 if anchor == "feet" else PROJECTILE_SETTLE_ANCHOR[0], 3),
                round(GROUND_ANCHOR_Y if anchor == "feet" else PROJECTILE_SETTLE_ANCHOR[1], 3),
            ]
        data["registration"] = registration_data
    return data


def frames_from_owned_sources(
    raw_path: Path,
    sources: list[OwnedFrameSource],
    prefit_scale: float,
) -> list[Image.Image]:
    rendered = render_frame_sources(sources, prefit_scale, str(raw_path))
    # Never delete a connected component merely because it sits near a cell
    # edge. Generated effects deliberately use sparks, trails, and floor rings
    # there; the old per-sheet repair table could erase valid art. Ownership and
    # fit registration preserve every keyed component, while crop assertions
    # fail loudly if a later transform would actually discard visible pixels.
    return [
        clear_frame_edges(frame, f"{raw_path} frame {index} raw crop cleanup")
        for index, frame in enumerate(rendered)
    ]


def keyed_frames(raw_path: Path, fit_margin: int = FIT_MARGIN_PX) -> list[Image.Image]:
    """Key the background out of a raw sheet and render normalized frames."""
    sources = owned_frame_sources(raw_path)
    return frames_from_owned_sources(raw_path, sources, compute_prefit_scale(sources, margin=fit_margin))


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


def make_sheet(
    raw_path: Path,
    out_path: Path,
    playback: str,
    anchor: str = "center",
    launch_start: int | None = None,
    impact_start: int | None = None,
    fit_margin: int = FIT_MARGIN_PX,
) -> dict[str, object]:
    frames = keyed_frames(raw_path, fit_margin)
    registered_frames, registration = register_sequence(
        frames,
        playback,
        anchor,
        launch_start,
        impact_start,
        str(raw_path),
    )
    sheet = compose_sheet(registered_frames)
    save_image_atomic(sheet, out_path, "PNG", optimize=True)
    return frame_diagnostics(sheet, playback, registration, anchor, launch_start, impact_start)


def make_layered_sheets(
    raw_back: Path,
    out_back: Path,
    raw_front: Path,
    out_front: Path,
    playback: str,
    anchor: str = "center",
    launch_start: int | None = None,
    impact_start: int | None = None,
) -> dict[str, object]:
    """Process a two-layer effect, registering both layers with one shared plan.

    The artist splits a few effects into a `_back` sheet (drawn behind the actor)
    and a `_front` sheet (drawn in front). They must move as one, so the pivot is
    computed from the combined silhouette and applied identically to each layer.
    """
    back_sources = owned_frame_sources(raw_back)
    front_sources = owned_frame_sources(raw_front)
    raw_prefit = min(compute_prefit_scale(back_sources), compute_prefit_scale(front_sources))
    back_frames = frames_from_owned_sources(raw_back, back_sources, raw_prefit)
    front_frames = frames_from_owned_sources(raw_front, front_sources, raw_prefit)
    combined = combine_layer_frames(back_frames, front_frames)
    scale, shifts, registration = compute_registration_plan(
        combined,
        playback,
        anchor,
        launch_start,
        impact_start,
    )
    safe_shifts = clamp_registration_shifts(combined, shifts)
    safe_shifts = clamp_registration_shifts(
        combined,
        stabilize_registration_shifts(
            safe_shifts,
            playback,
            launch_start,
            impact_start,
        ),
    )
    registration = registration_debug_with_actual_shifts(registration, safe_shifts)
    back_reg = apply_registration_plan(back_frames, scale, safe_shifts, str(raw_back))
    front_reg = apply_registration_plan(front_frames, scale, safe_shifts, str(raw_front))
    save_image_atomic(compose_sheet(back_reg), out_back, "PNG", optimize=True)
    front_sheet = compose_sheet(front_reg)
    save_image_atomic(front_sheet, out_front, "PNG", optimize=True)
    return frame_diagnostics(
        front_sheet,
        playback,
        registration,
        anchor,
        launch_start,
        impact_start,
    )


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


def save_image_atomic(
    image: Image.Image,
    path: Path,
    image_format: str,
    **save_options: object,
) -> None:
    """Encode beside the destination, then replace with brief Windows retries.

    Vite/image preview readers can momentarily hold an existing spritesheet open
    on Windows. Writing directly to that path intermittently raises ``EINVAL``
    midway through a full rebake. A same-directory replace keeps readers from
    observing a half-written PNG and survives those short-lived handles.
    """
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.processing")
    image.save(temp_path, format=image_format, **save_options)
    try:
        for attempt in range(8):
            try:
                os.replace(temp_path, path)
                return
            except OSError:
                if attempt == 7:
                    raise
                time.sleep(0.08 * (attempt + 1))
    finally:
        if temp_path.exists():
            temp_path.unlink()


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

    save_image_atomic(
        preview.convert("RGB"),
        OUT_DIR / "_preview-contact-sheet.jpg",
        "JPEG",
        quality=92,
        optimize=True,
    )


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
    parser.add_argument(
        "--remeasure",
        action="store_true",
        help=(
            "Skip baking; only re-measure each existing baked sheet's pixel-based "
            "placeAnchor and rewrite the manifest. Use to refresh anchors without "
            "re-processing (and re-churning) the PNGs."
        ),
    )
    return parser.parse_args()


def remeasure_place_anchors() -> None:
    """Recompute placeAnchor for every sprite from its already-baked sheet and
    rewrite the manifest in place. No PNGs are touched."""
    manifest = base_manifest(read_json_object(OUT_DIR / "manifest.json"))
    sprites = manifest.get("sprites")
    if not isinstance(sprites, dict):
        print(f"No sprites in {OUT_DIR / 'manifest.json'}; nothing to remeasure.")
        return
    measured = 0
    for entry in sprites.values():
        if isinstance(entry, dict):
            attach_place_anchor(entry)
            if isinstance(entry.get("placeAnchor"), dict):
                measured += 1
    write_json_lf(OUT_DIR / "manifest.json", manifest)
    print(f"Remeasured placeAnchor for {measured}/{len(sprites)} sprites in {OUT_DIR / 'manifest.json'}")


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
    if args.remeasure:
        remeasure_place_anchors()
        return
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
        launch_start = resolved.get("launchStartFrame")
        impact_start = resolved.get("impactStartFrame")
        launch_frame = int(launch_start) if isinstance(launch_start, (int, float)) else None
        impact_frame = int(impact_start) if isinstance(impact_start, (int, float)) else None
        if len(layers) == 1:
            _, raw_path, out_path = layers[0]
            diagnostics[name] = make_sheet(
                raw_path,
                out_path,
                str(playback),
                str(anchor),
                launch_frame,
                impact_frame,
            )
            # Drop stale depth-layer exports from before this effect was flattened.
            (OUT_DIR / f"{name}_back.png").unlink(missing_ok=True)
            (OUT_DIR / f"{name}_front.png").unlink(missing_ok=True)
        else:
            (_, raw_back, out_back), (_, raw_front, out_front) = layers
            diagnostics[name] = make_layered_sheets(
                raw_back,
                out_back,
                raw_front,
                out_front,
                str(playback),
                str(anchor),
                launch_frame,
                impact_frame,
            )
            # Drop a stale single-layer export from before this effect was split.
            (OUT_DIR / f"{name}.png").unlink(missing_ok=True)
        sprites[name] = manifest_entry(name, resolved, layered=len(layers) > 1)
        attach_place_anchor(sprites[name])

    for spec in external_specs:
        name = spec["name"]
        out_path = OUT_DIR / f"{name}.png"
        if not out_path.exists():
            skipped.append(name)
            continue
        sheet = Image.open(out_path).convert("RGBA")
        diagnostics[name] = frame_diagnostics(sheet, spec["playback"])
        sprites[name] = manifest_entry(name, spec)
        attach_place_anchor(sprites[name])

    if skipped:
        print(f"Skipped (no sheet yet for '{COMPANION_SLUG}'): {', '.join(skipped)}")

    write_json_lf(OUT_DIR / "manifest.json", manifest)
    write_json_lf(OUT_DIR / "_diagnostics.json", diagnostics)
    make_preview()


if __name__ == "__main__":
    main()
