/**
 * Returns what percentage of the command budget has been consumed beyond the minimum path.
 * Returns 0 when counted_commands_used <= min_threshold (clamped at zero, not capped at 100).
 */
export function computeBudgetConsumedPct(
  counted_commands_used: number,
  min_threshold: number,
  max_limit: number,
): number {
  if (counted_commands_used <= min_threshold) return 0
  const denominator = max_limit - min_threshold
  if (denominator <= 0) return 0
  return ((counted_commands_used - min_threshold) / denominator) * 100
}
