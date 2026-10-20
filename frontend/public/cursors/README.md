# GIT it! cursor suite

Static SVG cursors matched to the observatory palette in `DESIGN.md` (Starlight, Neon Blue, Night Sky).
Keep all assets 32×32 and transparent; CSS hotspots in `frontend/src/styles/cursors.css` must point at the actual action point.

| Asset | Purpose | Hotspot (x, y) |
| --- | --- | --- |
| arrow.svg | Default navigation | 4, 3 |
| hand.svg | Links and controls | 14, 4 |
| text.svg | Text input / terminal selection | 16, 16 |
| grab.svg | Drag affordance | 16, 15 |
| grabbing.svg | Active drag | 16, 16 |
| blocked.svg | Disabled | 16, 16 |
| progress.svg | Busy action | 4, 3 |
| crosshair.svg | Precision targeting | 16, 16 |
| help.svg | Contextual help | 3, 3 |

The CSS only targets hover-capable fine pointers; touch interfaces are untouched.
Unsupported SVG cursor formats fall back to native cursor keywords. Native resize
cursors remain directional to protect editor precision and usability.

Usage on specialized elements: `data-cursor="hand|text|grab|grabbing|blocked|progress|crosshair|help"`.
To opt out programmatically set `data-custom-cursors="off"` on the document root.
No additional JavaScript cursor tracking or animation runs.
