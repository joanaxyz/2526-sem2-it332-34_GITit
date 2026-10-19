/** Keep every star display on the same bounded, half-star scale. */
export function normalizeStarScore(stars: number | undefined): number {
  if (stars === undefined || !Number.isFinite(stars)) return 0
  return Math.round(Math.max(0, Math.min(3, stars)) * 2) / 2
}
