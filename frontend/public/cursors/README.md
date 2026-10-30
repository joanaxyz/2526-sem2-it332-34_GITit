# GIT it! cursor suite

Static SVG cursors matched to the observatory palette in `DESIGN.md`: black
Editor Night bodies (`#080C14`) with Neon Blue (`#00A3FF`) edges and highlights.
The arrow uses a compact, diagonal browser-pointer silhouette with rounded tips;
hands use curved palms and text caps have capsule ends. Fine outlines keep the
black silhouettes visible over dark surfaces; blue detail stays restrained.

Assets render at 28×28px using the original 32×32 viewBox, making the rounded
design 12.5% smaller. Keep backgrounds transparent and scale the CSS hotspots in
`frontend/src/styles/cursors.css` with the rendered size.

| Asset | Purpose | Hotspot (x, y) |
| --- | --- | --- |
| arrow.svg | Default navigation | 4, 3 |
| hand.svg | Links and controls | 12, 4 |
| text.svg | Text input / terminal selection | 14, 14 |
| grab.svg | Drag affordance | 14, 13 |
| grabbing.svg | Active drag | 14, 14 |
| blocked.svg | Disabled | 14, 14 |
| progress.svg | Busy action | 4, 3 |
| crosshair.svg | Precision targeting | 14, 14 |
| help.svg | Contextual help | 4, 3 |

The CSS only targets hover-capable fine pointers; touch interfaces are untouched.
Unsupported SVG cursor formats fall back to native cursor keywords. Native resize
cursors remain directional to protect editor precision and usability.

Usage on specialized elements: `data-cursor="hand|text|grab|grabbing|blocked|progress|crosshair|help"`.
To opt out programmatically set `data-custom-cursors="off"` on the document root.
No additional JavaScript cursor tracking or animation runs.
