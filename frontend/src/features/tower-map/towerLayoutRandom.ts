// Shared deterministic helpers for the tower's procedural scatter (clouds in
// TowerMapPage, windows in TowerStoreySection). Seeded so layouts are generated
// once and stay put across renders - no reshuffle / flicker.

export const clamp = (value: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, value))
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t

// Tiny deterministic PRNG (mulberry32).
export function mulberry32(seed: number) {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}
