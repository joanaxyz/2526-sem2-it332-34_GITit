/** Show only whole stars earned on the game's zero-to-three scale. */
export function normalizeStarScore(stars: number | undefined): number {
  if (stars === undefined || !Number.isFinite(stars)) return 0
  return Math.floor(Math.max(0, Math.min(3, stars)))
}
