"""Official Archive relic seed spec.

A relic is the single structural Archive asset (it replaced the old tower
pieces/artifacts). For now there is ONE generic official relic, built from an
existing section SVG; the user will skin/replace it later. Its kind
(tome/adventure/challenge) is chosen per placement, not baked into the asset.

Each relic carries two regions in its ``view_box`` space:
  - ``interactive_viewbox`` ``{x, y, width, height}`` - the hover/click hotspot
    that opens the relic overview.
  - ``landing_viewbox`` ``{x1, y1, x2, y2}`` - the rail Blue walks along.
"""

ARCANE_SPIRE_TAG = "arcane-spire"

OFFICIAL_RELIC_SLUG = "official-relic"

OFFICIAL_RELIC_SPECS = [
    {
        "slug": OFFICIAL_RELIC_SLUG,
        "label": "Arcane Relic",
        "svg": "sections/hall.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 368 200",
        # Centred hotspot covering most of the relic art.
        "interactive_viewbox": {"x": 84, "y": 40, "width": 200, "height": 120},
        # A rail near the base of the relic for the companion to stand on.
        "landing_viewbox": {"x1": 40, "y1": 188, "x2": 328, "y2": 188},
    },
]
