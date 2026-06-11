---
name: GIT it!
description: Scenario-driven Git learning rendered as a neon-lit medieval world — the Arcane Observatory.
colors:
  aurora-cyan: "#00F5D4"
  ocean-blue: "#00B4D8"
  deep-blue: "#0077B6"
  abyss-navy: "#03045E"
  night-sky: "#0a1015"
  observatory-wall: "#0f1824"
  tower-stone: "#1a2637"
  shadow-stone: "#18202a"
  starlight: "#ebf6fa"
  mist: "#7594a3"
  rampart-edge: "#253141"
  ember-red: "#ff5c5c"
  ink-on-cyan: "#031c18"
typography:
  display:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "clamp(1.55rem, 2.2vw, 2.05rem)"
    fontWeight: 900
    lineHeight: 1.1
  headline:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 700
    lineHeight: 1.2
  body:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "0.68rem"
    fontWeight: 700
    letterSpacing: "0.08em"
  numeral:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "1.35rem"
    fontWeight: 800
    lineHeight: 1
rounded:
  sm: "calc(0.75rem - 4px)"
  md: "calc(0.75rem - 2px)"
  lg: "0.75rem"
  panel: "8px"
  pill: "999px"
spacing:
  xs: "0.3rem"
  sm: "0.85rem"
  md: "1.25rem"
  lg: "2rem"
components:
  button-primary:
    backgroundColor: "{colors.ocean-blue}"
    textColor: "#ffffff"
    rounded: "{rounded.md}"
    height: "2.5rem"
    padding: "0.5rem 1rem"
  button-outline:
    backgroundColor: "transparent"
    textColor: "{colors.starlight}"
    rounded: "{rounded.md}"
    height: "2.5rem"
    padding: "0.5rem 1rem"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.mist}"
    rounded: "{rounded.md}"
    height: "2.5rem"
    padding: "0.5rem 1rem"
  card:
    backgroundColor: "{colors.observatory-wall}"
    textColor: "{colors.starlight}"
    rounded: "{rounded.lg}"
    padding: "1.25rem"
  game-panel:
    backgroundColor: "{colors.night-sky}"
    textColor: "{colors.starlight}"
    rounded: "{rounded.panel}"
  stat-tile:
    backgroundColor: "{colors.observatory-wall}"
    textColor: "{colors.starlight}"
    rounded: "12px"
  index-pill:
    backgroundColor: "{colors.night-sky}"
    textColor: "{colors.aurora-cyan}"
    rounded: "{rounded.pill}"
    padding: "0.25rem 0.65rem"
---

# Design System: GIT it!

## 1. Overview

**Creative North Star: "The Arcane Observatory"**

A wizard's tower at night. The learner studies under a living sky — sun and moon arcing, stars fading, clouds drifting in parallax — while glowing instruments report the state of their work. Every surface is deep night-navy stone; every signal is light: aurora-cyan edges, warm window glow, neon numerals. The fantasy is medieval, the rendering is neon, and the mood is focused enchantment — study that feels like practicing magic, not filling in a worksheet.

The system runs at two intensities. Atmospheric surfaces (home hub, tower, quest selection) carry the world: skies, glow pulses, scanline HUD panels, falling-block loaders. The practice workspace inverts the ratio: a faint atmospheric wash (`workspace-bg`) behind a ruthlessly legible terminal and DAG. The system explicitly rejects flat card grids and generic SaaS dashboards, wordy explainer UI, cutesy edu-gamification, and random decoration — every glow has a reason and a place.

**Key Characteristics:**
- Deep night-navy darkness as the canvas; light as the only signal vocabulary
- Instrumented and precise components: mono numerals, corner brackets, 1px neon edges, scanlines
- A living, time-aware sky as ambient identity on world surfaces
- Motion with physical weight — pieces fall, settle, and breathe; glow pulses mark life
- Warm amber (window light) as the single warm counterpoint to the cyan/blue field

## 2. Colors

A committed two-accent neon palette over a ramp of cold navy darks — light against night, never color against color.

### Primary
- **Aurora Cyan** (#00F5D4): the voice of the system. Marks what is alive, interactive, or earned — focus rings, progress tips, earned reward markers, panel light-bars, stat numerals, glow pulses. Used as light (borders, shadows, text-glow) far more often than as fill.

### Secondary
- **Ocean Blue** (#00B4D8): the working accent. Primary button gradients (to **Deep Blue** #0077B6), secondary glow layers, data-viz strokes. Cyan announces; ocean blue acts.

### Tertiary
- **Ember Red** (#ff5c5c): destructive and failure states only.
- **Window Amber** (rgba(255, 209, 130, …)): warm light inside tower windows and doors — the one warm note, reserved for the world itself.

### Neutral
- **Night Sky** (#0a1015): the body background; near-black with a cold blue cast.
- **Observatory Wall** (#0f1824): card and panel surfaces.
- **Tower Stone** (#1a2637): secondary surfaces, hover fills.
- **Shadow Stone** (#18202a): muted wells and inset areas.
- **Rampart Edge** (#253141): borders and input strokes at rest.
- **Starlight** (#ebf6fa): foreground text — a cool white, never pure #fff for prose.
- **Mist** (#7594a3): secondary text and labels. Body prose stays Starlight; Mist is for supporting lines only.

### Named Rules
**The Light-Is-Signal Rule.** Cyan and blue are never decoration-by-default. A glow means one of three things: it is interactive, it is alive (in progress), or it was earned. If none apply, the element stays stone.

**The One Warm Note Rule.** Amber belongs to the world (windows, doors, chests). It is prohibited in UI chrome, buttons, and text.

## 3. Typography

**Display/Body Font:** Inter (with system-ui fallback)
**Label/Mono Font:** JetBrains Mono (with ui-monospace fallback)

**Character:** A geometric–technical pairing. Inter carries headings and prose with heavy weights at the top (800–900) for confident, game-title density; JetBrains Mono is the instrument readout — every number, stat, kicker, and terminal line speaks mono.

### Hierarchy
- **Display** (900, clamp(1.55rem, 2.2vw, 2.05rem), 1.1): storey and page titles. Tight, heavy, no letter-spacing tricks.
- **Headline** (700, ~1.125rem, 1.2): card and panel titles.
- **Body** (400–500, 0.875rem, 1.55): prose and descriptions, Starlight on dark. Keep runs short — this system shows state rather than narrating it.
- **Label** (JetBrains Mono 600–700, 0.64–0.68rem, +0.08em, UPPERCASE): kickers, footers, HUD captions. Always mono, always quiet.
- **Numeral** (JetBrains Mono 800, 1.35rem, 1): stats and KPI values, finished with a cyan text-glow (`text-shadow: 0 0 16px rgba(0,245,212,0.34)`).

### Named Rules
**The Mono Numerals Rule.** Every quantity — coins, scores, percentages, counts — renders in JetBrains Mono with a neon text-shadow. Inter never carries a stat.

## 4. Elevation

Light is elevation. Surfaces sit in deep ambient darkness (`box-shadow: 0 4px 24px rgba(0,0,0,0.45), 0 1px 4px rgba(0,0,0,0.3)` — the `panel` shadow) that grounds them against the sky; cyan glow then lifts whatever matters. Resting panels get a 1px neon light-bar across the top edge and faint inset starlight; hover and achievement states widen the glow (`aurora-sm`: 0 0 12px rgba(0,245,212,0.25); `aurora-md`: 0 0 22px rgba(0,245,212,0.35) + 0 0 44px rgba(0,180,216,0.15)). World-facing panels add `backdrop-filter: blur(10–12px)` so the living sky reads through them.

### Shadow Vocabulary
- **panel** (`0 4px 24px rgba(0,0,0,0.45), 0 1px 4px rgba(0,0,0,0.3)`): default grounding for cards and panels.
- **aurora-sm** (`0 0 12px rgba(0,245,212,0.25)`): subtle interactive glow — hover, focus accents.
- **aurora-md** (`0 0 22px rgba(0,245,212,0.35), 0 0 44px rgba(0,180,216,0.15)`): earned/achievement glow — rewards, completions, perfect scores.

### Named Rules
**The Earned Glow Rule.** Glow intensity scales with meaning: rest < hover < alive < earned. The brightest pulses (completion sparkle, perfect-score text-glow) are reserved for achievement moments and are never ambient.

## 5. Components

Instrumented and precise: HUD instruments with mono numerals, corner brackets, thin neon edges, and crisp state changes.

### Buttons
- **Shape:** softly squared (radius 0.625rem default; 0.75rem large)
- **Primary:** Ocean Blue → Deep Blue horizontal gradient (#00B4D8 → #0077B6), white text, semibold 0.875rem, blue ambient shadow (`0 8px 28px rgba(0,119,182,0.3)`); height 2.5rem, padding 0.5rem 1rem
- **Hover / Focus:** hover shifts the shadow toward cyan (`0 8px 36px rgba(0,245,212,0.35)`); focus is a 2px cyan ring (`ring-ring`) offset against the background
- **Secondary / Outline / Ghost / Destructive:** Tower Stone fill / 1px Rampart Edge border on translucent background / borderless Mist text that resolves to Starlight on Tower Stone / Ember Red fill

### Game Panel (signature container)
The HUD slab for gamified surfaces (`.game-panel`): Observatory-dark gradient fill, 1px cyan border at 16% opacity, a 1px neon **light-bar** across the top edge, a faint scanline texture masked to fade out by 70% height, `backdrop-filter: blur(10px)`, and optional engraved **corner brackets** (12px L-shapes in pale starlight, `.game-corner--tl/tr/bl/br`). Hover brightens the border and adds a soft cyan halo. Radius 8px.

### Open Instrument Deck (stats surfaces)
Analytics surfaces (the home Stats tab) reject panel chrome entirely: charts, ledgers, and gauges sit **directly on the night sky**, organized by a single bold Inter title per section (no eyebrow kickers), generous whitespace (2.5rem section gaps), and hairline rules (`1px rgba(125,211,252,0.07–0.08)`) between ledger rows (`.metric-line`, `.kpi-line`, `.match-row`). Accents live in the data itself — neon mono numerals, glowing icons, accent dots — never in row borders or stripes. Exactly **one glass element per deck** is allowed: a chamfered glass slat (`.stats-glass-band`, the hero plaques' vocabulary) carrying the headline readout. Range pills (`.hub-pill`) are soft borderless fills, cyan-tinted when active.

### Cards / Containers
- **Corner Style:** 0.75rem
- **Background:** Observatory Wall (#0f1824)
- **Shadow Strategy:** `panel` shadow at rest (see Elevation); glow only with a reason
- **Border:** 1px Rampart Edge
- **Internal Padding:** 1.25rem (p-5), header/content stacked with 0.375rem gaps

### Stat Tile
Compact KPI instrument (`.stat-tile`): dark gradient fill, 12px radius, a 3px accent-colored top edge with matching glow (`--tile-accent`, default cyan), and a soft accent bloom in the top-right corner. Hover lifts 3px and brightens the accent. Values follow the Mono Numerals Rule.

### Inputs / Fields
- **Style:** 1px Rampart Edge stroke on translucent dark fill, radius 0.625rem; terminal command input is mono-first
- **Focus:** 2px Aurora Cyan ring, offset from the surface
- **Error / Disabled:** Ember Red border/text; disabled drops to 50% opacity with pointer events off

### Navigation
Pills and docks rather than bars: the index pill (`.tower-index-pill`) is a 999px-radius chip — cyan text on 10% cyan fill, 1px 28% cyan border, soft glow. Fixed side docks (storey rail, door dock) float over the sky with pointer-events isolation. Active state = cyan; inactive = Mist.

### Living Sky (signature atmosphere)
World surfaces sit under a fixed, time-aware sky: gradient dusk-to-night backdrop, sun/moon discs positioned by a sky engine via CSS custom properties, two parallax starfields with independent twinkle loops, and masked SVG cloud layers with scroll-linked parallax. Panels floating over it use the glass treatment (blur 12px) so the sky stays present. The workspace replaces all of this with `workspace-bg` — two radial cyan washes at 3–4% opacity, nothing more.

## 6. Do's and Don'ts

### Do:
- **Do** express depth as light: `panel` shadow to ground, cyan glow to elevate, exactly per the Earned Glow Rule.
- **Do** set every numeral in JetBrains Mono 800 with a cyan text-glow (the Mono Numerals Rule).
- **Do** give every infinite animation (breathing glows, twinkles, shimmer) a `prefers-reduced-motion: reduce` fallback — the codebase pattern is `animation: none; opacity: 1`.
- **Do** use spring-flavored cubic-bezier easing (e.g. `cubic-bezier(0.34, 1.56, 0.64, 1)`) only for achievement pops and world physics (falling tower pieces); state transitions use `cubic-bezier(0.16, 1, 0.3, 1)` ease-out.
- **Do** keep body prose in Starlight (#ebf6fa) at 0.875rem/1.55 — Mist (#7594a3) is for labels and supporting lines only.

### Don't:
- **Don't** build flat card grids or generic SaaS dashboards — identical icon+heading+text tiles repeated in a grid are the named anti-reference. Use readout rails, metric lines, and instruments instead.
- **Don't** write wordy explainer UI: no tooltip essays, no paragraph-length helper text. Show state, don't narrate it.
- **Don't** drift into cutesy edu-gamification (Duolingo-style): no mascot cheer, no confetti-for-everything. Celebration scales with achievement.
- **Don't** scatter random decoration. Particles, glows, and sparks exist only inside composed set-pieces (loader, completion, sky); a stray glow with no meaning violates the Light-Is-Signal Rule.
- **Don't** use amber in UI chrome — it belongs to the world's windows, doors, and chests (the One Warm Note Rule).
- **Don't** use pure white text or untinted grays; every neutral carries the cold blue cast of the palette.
