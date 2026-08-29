---
name: GIT it!
description: A scenario-driven Git learning platform — a wizard's observatory rendered in neon.
colors:
  neon-blue: "#00A3FF"
  ocean-blue: "#00B4D8"
  deep-blue: "#0077B6"
  arcane-purple: "#B04AFF"
  rail-blue: "#358FFF"
  window-amber: "#F3D27A"
  ember-red: "#FF5C5C"
  success-blue: "#47D4FF"
  night-sky: "#0A1014"
  editor-night: "#080C14"
  observatory-wall: "#0F1724"
  observatory-stone: "#1A2638"
  starlight: "#E8F6FA"
  mist: "#758F9F"
  hairline: "#253141"
typography:
  display:
    fontFamily: "Chakra Petch, Inter, system-ui, sans-serif"
    fontSize: "clamp(1.8rem, 3vw, 2.4rem)"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "normal"
  body:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
  label:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.78rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "normal"
  numeral:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "1.35rem"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "normal"
  eyebrow:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "0.72rem"
    fontWeight: 800
    lineHeight: 1.4
    letterSpacing: "0.12em"
rounded:
  sm: "0.45rem"
  md: "0.6rem"
  base: "0.75rem"
  lg: "0.9rem"
  pill: "999px"
spacing:
  "1": "0.25rem"
  "2": "0.5rem"
  "3": "0.75rem"
  "4": "1rem"
  "5": "1.5rem"
  "6": "2rem"
  "8": "3rem"
components:
  button-primary:
    backgroundColor: "{colors.ocean-blue}"
    textColor: "#FFFFFF"
    rounded: "{rounded.base}"
    height: "2.5rem"
    padding: "0 1rem"
  button-outline:
    backgroundColor: "{colors.night-sky}"
    textColor: "{colors.starlight}"
    rounded: "{rounded.base}"
    height: "2.5rem"
    padding: "0 1rem"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.mist}"
    rounded: "{rounded.base}"
    height: "2.5rem"
    padding: "0 1rem"
  input:
    backgroundColor: "{colors.night-sky}"
    textColor: "{colors.starlight}"
    rounded: "{rounded.sm}"
    padding: "0.4rem 0.55rem"
  chip-filter:
    backgroundColor: "{colors.observatory-stone}"
    textColor: "{colors.mist}"
    rounded: "{rounded.pill}"
    padding: "0.25rem 0.6rem"
  card:
    backgroundColor: "{colors.observatory-wall}"
    textColor: "{colors.starlight}"
    rounded: "{rounded.lg}"
    padding: "1rem 1.1rem"
  status-chip:
    backgroundColor: "transparent"
    textColor: "{colors.mist}"
    rounded: "{rounded.sm}"
    padding: "0.05rem 0.45rem"
---

# Design System: GIT it!

## 1. Overview

**Creative North Star: "The Arcane Observatory"**

A floating arcane level map at night. The learner studies under a living sky — sun and moon
arcing, stars fading, clouds drifting in parallax — while glowing instruments report
the state of their work. Every surface is deep night-navy stone; every signal is light:
neon-blue edges, warm window glow, neon numerals. GIT it! is a medieval-fantasy world
rendered in neon, where learning Git is a journey through a level map of glowing chapters, not a
worksheet.

The system runs at **two intensities, one vocabulary: immersion outside, clarity inside.**
Atmospheric surfaces — home hub, level map, quest selection — carry the world: living sky,
depth, aurora glow, weighty motion. The practice workspace (terminal, DAG) and the
authoring tools invert the ratio: a faint atmospheric wash behind ruthlessly legible
controls. Both modes share the same palette, type system, and single accent; only their
density and motion change.

This system explicitly rejects the **flat SaaS dashboard** (rows of identical stat
cards, icon-heading-paragraph tiles), **wordy explainer UI** (tooltip essays, walls of
helper text), **cutesy edu-gamification** (mascot cheer, confetti-for-everything,
streak guilt), and **random decoration** (scattered glow with no compositional intent).
Every glow has a reason and a place.

**Key Characteristics:**
- Deep night-navy darkness as the canvas; light as the only signal vocabulary.
- One accent — neon blue — and one warm counterpoint (window amber).
- Three type voices: a squared techno **display** (Chakra Petch), a humanist **interface** sans (Inter), a **machine** mono (JetBrains Mono).
- Container-less by preference: hairline-split rows over boxed cards; one glass plaque max.
- Depth via tonal layering and earned accent glow, not heavy drop shadows.
- Motion conveys state and has physical weight; every animation has a reduced-motion fallback.

## 2. Colors

A drenched night-navy canvas where light is the only signal. One cyan accent, one warm
note, state colours for everything else. (Canonical values are HSL in
`src/styles/tokens.css`; the hexes here are the sRGB equivalents.)

### Primary
- **Neon Blue** (`#00A3FF`, `--primary` / `--theme-primary-rgb`): The brand's one accent. Current selection, focus rings, active states, eyebrows, links, neon numerals, and every glowing edge in the level-map world. Its rarity against the dark is the point.

### Secondary
- **Ocean Blue** (`#00B4D8`, `--accent`) → **Deep Blue** (`#0077B6`): The primary-button gradient and forward motion. The only place this blue gradient appears.
- **Rail Blue** (`#358FFF`, `--theme-rail-rgb`): Structure inside the level-map world — rails, the line Blue walks. Never text.

### Tertiary
- **Arcane Purple** (`#B04AFF`, `--theme-challenge-rgb`): The Challenge accent — level-map gizmo, Challenge viewboxes, the staged/pending outline. Reserved for the level-map world.
- **Window Amber** (`#F3D27A`, `--warning`): The single warm counterpoint to the cyan field — window light, doors, and chests in the world; caution and the "testable" state in the UI.

### Neutral
- **Night Sky** (`#0A1014`, `--background`) and **Editor Night** (`#080C14`): The body and the focused-workspace canvas. Near-black, faintly cool.
- **Observatory Wall** (`#0F1724`, `--card`) / **Observatory Stone** (`#1A2638`, `--secondary`): Tonal layers for plaques, toolbars, rails — depth by lightness, not shadow.
- **Starlight** (`#E8F6FA`, `--foreground`): Cool-white body and headings.
- **Mist** (`#758F9F`, `--muted-foreground`): Secondary text, hints, labels. ~6:1 on Night Sky — the floor for body text; never lighter.
- **Hairline** (`#253141`, `--border`): Dividers and the 1px row borders the container-less layouts lean on.

### State
- **Success Mint** (`#8FF7E6`, `--success`): Published / passed / ok.
- **Window Amber** (`#F3D27A`, `--warning`): Needs attention — validation warnings, the "testable" status.
- **Ember Red** (`#FF5C5C`, `--destructive`): Errors and destructive actions.

### Named Rules
**The One Accent Rule.** There is exactly one neon accent: `#00A3FF`. `--theme-primary-rgb` is its compatibility alias and `--primary` resolves to it. The legacy aurora cyan (`#00F5D4`) and sky-cyan (`rgb(45,245,255)`) are deprecated — never reintroduce a second cyan/blue accent, and reference `var(--theme-primary-rgb)`/`--primary` rather than hardcoding a triple.

**The Light-Is-Signal Rule.** Cyan and blue are never decoration-by-default. A glow means the element is interactive, alive (in progress), or earned. If none apply, it stays stone.

**The One Warm Note Rule.** Amber is the only warm hue. In the world it is light (windows, doors, chests); in the UI it is caution. It never becomes a third "brand colour" or a primary action.

**The State-Earns-Colour Rule.** Outside the accent, colour means a state (success/warning/error). Pass/fail must also carry text or icon — never colour alone.

## 3. Typography

**Display Font:** Chakra Petch (with Inter, system-ui fallback) — squared, chamfered, techno-military caps.
**Body / Interface Font:** Inter (with system-ui fallback).
**Numeral / Eyebrow / Machine Font:** JetBrains Mono (with ui-monospace fallback).

**Character:** A wide, machined display against a clean humanist sans, with a monospace for everything the machine "says." The contrast axis (squared-techno vs. humanist vs. monospace) keeps the three legible as distinct voices — never two sans that look almost alike.

### Hierarchy
- **Display** (Chakra Petch 700, `clamp(1.8rem, 3vw, 2.4rem)`, `-0.01em`): Page titles and brand moments only — hub hero, track name, "Manage your track", "New adventure". The one place the world's voice enters a workspace.
- **Title** (Inter 800, ~1.05rem): Section, card, and level headings.
- **Body** (Inter 400–500, 0.9375rem, line-height 1.6): Prose, summaries, descriptions. Cap prose at 65–75ch.
- **Label** (Inter 700, ~0.78rem): Field labels, button text, chips.
- **Numeral / Eyebrow** (JetBrains Mono 600–800, uppercase, `0.12em` for eyebrows): Eyebrows, status pills, coin counts, metrics, numeric transform fields, and the terminal/DAG — the machine voice.

### Named Rules
**The Three-Voice Rule.** Chakra Petch for titles & brand, Inter for the interface, JetBrains Mono for the machine (data, code, eyebrows). Never a fourth family; never Inter where a page title wants the display voice; never the display face on body or controls.

**The Mono Numerals Rule.** Every quantity — coins, scores, percentages, counts, transform values — renders in JetBrains Mono. Inter never carries a stat.

**The Minimum-Size Rule.** No interface text below `--text-2xs` (0.6875rem / 11px). Tiny tracked mono labels are the system's biggest legibility risk; if a label "needs" to be 9px, the layout is too dense.

## 4. Elevation

Depth is built from **tonal layering and earned accent glow**, not heavy drop shadows.
Surfaces step up by lightness (Night Sky → Observatory Wall → Observatory Stone), and
accent elements emit a faint cyan glow rather than casting a dark shadow. Real drop
shadows are reserved for true overlays (modals, dropdowns, toasts). In the editor
canvas, pieces deliberately carry **no** box-shadow — selection is shown by outline/gizmo,
so glow never competes with the art.

### Shadow Vocabulary
- **Focus ring** (`0 0 0 2px rgba(var(--theme-primary-rgb), 0.22)`): Keyboard/active focus.
- **Neon glow — sm** (`0 0 12px rgba(0,163,255,0.25)`): Hover/focus accents.
- **Neon glow — md** (`0 0 22px rgba(0,163,255,0.35), 0 0 44px rgba(0,180,216,0.15)`): Earned moments — rewards, completions.
- **Raised plaque** (`inset 0 1px 0 rgba(255,255,255,0.05), 0 12px 30px rgba(0,0,0,0.4)`): Glass plaques, floating rails.
- **Overlay** (`0 18px 40px rgba(0,0,0,0.5)`): Modals, dropdowns, toasts only.

### Named Rules
**The Earned Glow Rule.** Glow intensity scales with meaning: rest < hover < alive < earned. The brightest pulses are reserved for achievement moments and are never ambient.

**The Glow-Not-Shadow Rule.** At rest, surfaces are flat and tonally layered. Lift is accent glow, not a darker, blurrier drop shadow. If it looks like a 2014 Material card, the shadow is wrong. Dark drop shadows appear only on things that truly float.

## 5. Components

### Buttons
- **Shape:** Rounded (`--radius` 0.75rem; `sm` uses `--radius-sm` 0.45rem). Height 2.5rem default, 2rem small.
- **Primary:** Ocean→Deep blue gradient (`#00B4D8`→`#0077B6`), white text; an ocean shadow that warms to a cyan glow on hover. The single "go forward" action.
- **Secondary:** Solid Observatory Stone, ink text. **Outline:** 1px hairline on translucent Night Sky. **Ghost:** muted ink, hover fills. **Destructive:** Ember Red.
- **Hover / Focus:** 150ms transitions; `focus-visible` shows a 2px cyan ring offset from the surface. Never ship a control without hover + focus-visible.

### Chips
- **Style:** Pill (`--radius-pill`), Observatory Stone background, Mist text, hairline border.
- **State:** Selected/active fills with **neon blue**, text flips to Night Sky (`is-active`). Used for filter tag pickers and multi-select rosters; the portrait-bearing roster chip seats art at the leading edge.

### Cards / Containers
- **Corner Style:** `--radius-lg` (0.9rem). **Background:** faint top-lit gradient over Observatory Wall; 1px cyan-tinted hairline. **Shadow:** none at rest (see Elevation). **Padding:** `--space-4` (1rem)–1.1rem.
- **Signature world panel:** the HUD slab (`game-panel`) — neon light-bar, faint scanlines, corner brackets, glass blur — is the atmospheric counterpart for hub/level-map surfaces.
- **Caution:** Cards are the *fallback*, not the default. Prefer container-less hairline-split rows. Nested cards are forbidden.

### Inputs / Fields
- **Style:** Translucent Night Sky fill, 1px cyan-tinted hairline, `--radius-sm`. Interface inputs use **Inter**; numeric/transform/code inputs use **JetBrains Mono**.
- **Focus:** Border brightens to cyan + 2px cyan ring. **Error:** rendered as text near the field — never colour-only. **Disabled:** ~0.4 opacity.

### Navigation
- **Hub chrome (atmospheric):** a floating, centered "launcher blade" (HOME · TRACKS · SHOP) with the brand badge and wallet/profile loose in the corners (Halo-style), over the living sky. Atmospheric pages only.
- **Workspace chrome:** focused tools (the level editor) use their own solid command bar (`ite-cmdbar`) — a docked, opaque blade with identity, history, and apply/publish. Dense, scrolling surfaces must NOT sit under the floating hub blade.

### Signature: The Editor Inspector
A right rail of **hairline-split sections** (`ite-section`, no inner panels): a mono eyebrow + title per section, a 2-col numeric transform grid (X/Y/W/H/Rotation/Z) in mono, and the draft model (`Apply edits (N)` / Discard / Undo-Redo) in the command bar. This is the reference pattern for any structured editing surface — content authoring should adopt the same hairline sections and numeric+drag controls rather than boxed cards.

## 6. Do's and Don'ts

### Do:
- **Do** use exactly one neon accent — `#00A3FF` via `var(--theme-primary-rgb)` / `--primary`. Reference the token; never hardcode `rgb(45,245,255)` or a raw triple.
- **Do** keep the three type voices distinct: Chakra Petch (titles/brand), Inter (interface), JetBrains Mono (data/code/eyebrows). Every numeral is mono.
- **Do** express depth as light: tonal layers + cyan glow per the Earned Glow Rule; reserve dark drop shadows for true overlays.
- **Do** prefer container-less, hairline-split rows; reserve cards for real grouping and never nest them.
- **Do** give every interactive element hover, `focus-visible`, disabled, and (where relevant) loading/error states.
- **Do** keep motion 150–250ms ease-out (`cubic-bezier(0.16, 1, 0.3, 1)`), state-only, with a `prefers-reduced-motion` fallback; spring easing only for achievement pops and world physics.
- **Do** use the semantic z-index scale (`--z-sticky` 20 → `--z-tooltip` 80).
- **Do** keep body text ≥ 4.5:1 (Starlight for prose, Mist only for labels/support) and never smaller than `--text-2xs` (11px).

### Don't:
- **Don't** introduce a second cyan, spend arcane purple on generic chrome, or make amber a third brand colour (it's the one warm note).
- **Don't** build flat SaaS dashboards — rows of identical stat cards or icon-heading-paragraph tiles. If a surface could pass for an admin template, it has failed.
- **Don't** write wordy explainer UI — tooltip essays or walls of helper text. Show state; don't narrate it.
- **Don't** do cutesy edu-gamification (mascot cheer, confetti-for-everything, streak guilt). Rewards feel earned and premium.
- **Don't** scatter particles/glow with no compositional intent — that violates the Light-Is-Signal Rule.
- **Don't** use `border-left`/`border-right` > 1px as a coloured accent stripe, gradient text (`background-clip: text`), or glassmorphism as a default decoration.
- **Don't** put dense, scrolling forms under the floating hub blade — they collide with it. Give workspaces their own solid chrome.
- **Don't** use raw z-index values (`9999`, `2000000`); they break the stacking contract.
