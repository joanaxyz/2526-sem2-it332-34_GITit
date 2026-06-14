// Living-sky engine. A single `timeOfDay` value (0..24 hours) drives the whole
// backdrop: gradient, cloud tint/opacity, star + window glow, and the sun/moon
// arc. Everything is interpolated between the keyframes below so the sky eases
// from night -> dawn -> day -> sunset -> dusk like an RPG day-night cycle.

export type RGB = readonly [number, number, number]

export type SkyPhase = {
  /** Hour on a 24h clock this palette is anchored to. */
  hour: number
  skyTop: RGB
  skyMid: RGB
  skyBottom: RGB
  /** Ambient radial wash color (consumed via `rgba(var(--sky-glow), )`). */
  skyGlow: RGB
  /** Cloud fill color for this time of day. */
  cloudTint: RGB
  /** 0..1 multipliers / strengths. */
  cloudOpacity: number
  starOpacity: number
  sunOpacity: number
  moonOpacity: number
  /** Warm interior light behind the tower's medieval windows. */
  windowGlow: number
}

// Anchored, sorted by hour. The gap between the last (22:00) and first (5:00)
// keyframe wraps through midnight - handled in `computeSky`.
export const SKY_PHASES: readonly SkyPhase[] = [
  {
    hour: 0, // deep night
    skyTop: [5, 8, 29],
    skyMid: [17, 26, 68],
    skyBottom: [36, 48, 102],
    skyGlow: [70, 96, 168],
    cloudTint: [120, 134, 180],
    cloudOpacity: 0.5,
    starOpacity: 1,
    sunOpacity: 0,
    moonOpacity: 1,
    windowGlow: 1,
  },
  {
    hour: 5, // pre-dawn, first warmth on the horizon
    skyTop: [12, 16, 46],
    skyMid: [40, 38, 86],
    skyBottom: [92, 68, 112],
    skyGlow: [126, 92, 172],
    cloudTint: [150, 140, 182],
    cloudOpacity: 0.58,
    starOpacity: 0.65,
    sunOpacity: 0,
    moonOpacity: 0.65,
    windowGlow: 0.85,
  },
  {
    hour: 6.5, // sunrise - pink / orange
    skyTop: [60, 78, 150],
    skyMid: [222, 132, 132],
    skyBottom: [255, 182, 122],
    skyGlow: [255, 162, 120],
    cloudTint: [255, 204, 184],
    cloudOpacity: 0.82,
    starOpacity: 0.12,
    sunOpacity: 0.92,
    moonOpacity: 0.18,
    windowGlow: 0.5,
  },
  {
    hour: 9, // morning
    skyTop: [58, 122, 202],
    skyMid: [112, 172, 230],
    skyBottom: [184, 214, 242],
    skyGlow: [150, 202, 255],
    cloudTint: [244, 250, 255],
    cloudOpacity: 0.95,
    starOpacity: 0,
    sunOpacity: 1,
    moonOpacity: 0,
    windowGlow: 0.18,
  },
  {
    hour: 12, // midday - bright azure
    skyTop: [40, 110, 210],
    skyMid: [92, 162, 236],
    skyBottom: [178, 216, 246],
    skyGlow: [122, 192, 255],
    cloudTint: [255, 255, 255],
    cloudOpacity: 1,
    starOpacity: 0,
    sunOpacity: 1,
    moonOpacity: 0,
    windowGlow: 0.1,
  },
  {
    hour: 16.5, // golden hour
    skyTop: [72, 112, 192],
    skyMid: [182, 172, 212],
    skyBottom: [255, 212, 152],
    skyGlow: [255, 202, 142],
    cloudTint: [255, 226, 192],
    cloudOpacity: 0.95,
    starOpacity: 0,
    sunOpacity: 1,
    moonOpacity: 0,
    windowGlow: 0.24,
  },
  {
    hour: 18.5, // sunset - pink / orange / red
    skyTop: [40, 50, 112],
    skyMid: [202, 92, 122],
    skyBottom: [255, 142, 92],
    skyGlow: [255, 122, 112],
    cloudTint: [255, 172, 150],
    cloudOpacity: 0.85,
    starOpacity: 0.1,
    sunOpacity: 0.78,
    moonOpacity: 0.26,
    windowGlow: 0.55,
  },
  {
    hour: 20, // dusk - violet
    skyTop: [12, 16, 50],
    skyMid: [48, 40, 96],
    skyBottom: [96, 70, 122],
    skyGlow: [122, 82, 162],
    cloudTint: [140, 130, 176],
    cloudOpacity: 0.6,
    starOpacity: 0.7,
    sunOpacity: 0.08,
    moonOpacity: 0.8,
    windowGlow: 0.85,
  },
  {
    hour: 22, // night
    skyTop: [6, 9, 32],
    skyMid: [18, 27, 70],
    skyBottom: [38, 50, 104],
    skyGlow: [74, 98, 170],
    cloudTint: [122, 136, 182],
    cloudOpacity: 0.52,
    starOpacity: 0.95,
    sunOpacity: 0,
    moonOpacity: 0.96,
    windowGlow: 0.96,
  },
]

const clamp = (value: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, value))
const lerp = (a: number, b: number, t: number) => a + (b - a) * t

function lerpRGB(a: RGB, b: RGB, t: number): RGB {
  return [
    Math.round(lerp(a[0], b[0], t)),
    Math.round(lerp(a[1], b[1], t)),
    Math.round(lerp(a[2], b[2], t)),
  ]
}

const rgb = (c: RGB) => `rgb(${c[0]}, ${c[1]}, ${c[2]})`
const triplet = (c: RGB) => `${c[0]}, ${c[1]}, ${c[2]}`

// Normalise to [0, 24).
function wrapHour(hour: number) {
  return ((hour % 24) + 24) % 24
}

// Find the two phases bracketing `hour` and the 0..1 blend between them,
// wrapping across midnight (22:00 -> 5:00).
function bracket(hour: number): { from: SkyPhase; to: SkyPhase; t: number } {
  const h = wrapHour(hour)
  const phases = SKY_PHASES
  for (let i = 0; i < phases.length; i += 1) {
    const from = phases[i]
    const to = phases[(i + 1) % phases.length]
    const start = from.hour
    // The wrap segment (last->first) spans from 22:00 up to 5:00+24.
    const end = to.hour > from.hour ? to.hour : to.hour + 24
    const hh = h >= start ? h : h + 24
    if (hh >= start && hh < end) {
      return { from, to, t: (hh - start) / (end - start) }
    }
  }
  return { from: phases[0], to: phases[1], t: 0 }
}

// Sun/moon travel a shallow arc. `param` runs 0 (rising at the eastern horizon)
// -> 1 (setting at the western horizon); the peak sits at param 0.5.
function arc(param: number) {
  const x = lerp(8, 92, clamp(param, -0.2, 1.2))
  const y = 80 - Math.sin(clamp(param, 0, 1) * Math.PI) * 66 // 80% (low) -> 14% (high)
  return { x, y }
}

function phaseLabelFor(hour: number) {
  const h = wrapHour(hour)
  if (h < 5) return 'Night'
  if (h < 6.5) return 'Dawn'
  if (h < 8) return 'Sunrise'
  if (h < 11) return 'Morning'
  if (h < 14) return 'Midday'
  if (h < 16.5) return 'Afternoon'
  if (h < 18) return 'Golden hour'
  if (h < 19.5) return 'Sunset'
  if (h < 21) return 'Dusk'
  return 'Night'
}

export type SkyVars = Record<string, string>

export type SkyState = {
  vars: SkyVars
  phaseLabel: string
  isNight: boolean
}

/**
 * Pure: turn a `timeOfDay` (0..24) into a bag of CSS custom properties plus a
 * couple of derived flags. Cheap enough to call every animation frame.
 */
export function computeSky(timeOfDay: number): SkyState {
  const { from, to, t } = bracket(timeOfDay)

  const skyTop = lerpRGB(from.skyTop, to.skyTop, t)
  const skyMid = lerpRGB(from.skyMid, to.skyMid, t)
  const skyBottom = lerpRGB(from.skyBottom, to.skyBottom, t)
  const skyGlow = lerpRGB(from.skyGlow, to.skyGlow, t)
  const cloudTint = lerpRGB(from.cloudTint, to.cloudTint, t)

  const cloudOpacity = lerp(from.cloudOpacity, to.cloudOpacity, t)
  const starOpacity = lerp(from.starOpacity, to.starOpacity, t)
  const sunOpacity = lerp(from.sunOpacity, to.sunOpacity, t)
  const moonOpacity = lerp(from.moonOpacity, to.moonOpacity, t)
  const windowGlow = lerp(from.windowGlow, to.windowGlow, t)

  const h = wrapHour(timeOfDay)
  const sun = arc((h - 6) / 12) // sun is up ~06:00 -> 18:00
  const moon = arc(wrapHour(h - 18) / 12) // moon is up ~18:00 -> 06:00

  const vars: SkyVars = {
    '--sky-top': rgb(skyTop),
    '--sky-mid': rgb(skyMid),
    '--sky-bottom': rgb(skyBottom),
    '--sky-glow': triplet(skyGlow),
    '--cloud-tint': rgb(cloudTint),
    '--cloud-opacity': cloudOpacity.toFixed(3),
    '--star-opacity': starOpacity.toFixed(3),
    '--sun-x': `${sun.x.toFixed(2)}%`,
    '--sun-y': `${sun.y.toFixed(2)}%`,
    '--sun-opacity': sunOpacity.toFixed(3),
    '--moon-x': `${moon.x.toFixed(2)}%`,
    '--moon-y': `${moon.y.toFixed(2)}%`,
    '--moon-opacity': moonOpacity.toFixed(3),
    '--window-glow': windowGlow.toFixed(3),
  }

  return {
    vars,
    phaseLabel: phaseLabelFor(timeOfDay),
    isNight: starOpacity > 0.5,
  }
}
