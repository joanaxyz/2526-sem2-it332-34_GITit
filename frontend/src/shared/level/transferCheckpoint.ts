/** Where a ready transfer checkpoint opens: its started run, or a fresh start. */
export function transferCheckpointPath(point: { tier_id: number; run_id: number | null }) {
  return point.run_id
    ? `/adventure-tier-runs/${point.run_id}`
    : `/adventure-level-tiers/${point.tier_id}/runs?transfer=1`
}

/** Ungraded practice of a checkpoint whose result is already recorded. */
export function transferPracticePath(tierId: number) {
  return `/adventure-level-tiers/${tierId}/runs?transfer=1&practice=1`
}
