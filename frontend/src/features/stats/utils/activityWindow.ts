import type { ActivityWindow } from '@/features/stats/types'

export type { ActivityWindow }

export type ActivityWindowOption = {
  id: ActivityWindow
  /** Control label. */
  label: string
  /** Band heading, e.g. "Last 30 days". */
  heading: string
  /** What one plotted point is, for the caption under the plot. */
  bucket: 'days' | 'months'
}

/**
 * The windows the activity band offers, in span order. The backend owns the
 * same three names and resolves anything else to the default, so a stale
 * bookmark degrades to a month rather than erroring.
 */
export const ACTIVITY_WINDOWS: readonly ActivityWindowOption[] = [
  { id: 'week', label: 'Week', heading: 'Last 7 days', bucket: 'days' },
  { id: 'month', label: 'Month', heading: 'Last 30 days', bucket: 'days' },
  { id: 'year', label: 'Year', heading: 'Last 12 months', bucket: 'months' },
] as const

export const DEFAULT_ACTIVITY_WINDOW: ActivityWindow = 'month'

export function activityWindowFromParam(value: string | null): ActivityWindow {
  const match = ACTIVITY_WINDOWS.find((option) => option.id === value)
  return match ? match.id : DEFAULT_ACTIVITY_WINDOW
}

export function activityWindowOption(window: ActivityWindow): ActivityWindowOption {
  return ACTIVITY_WINDOWS.find((option) => option.id === window) ?? ACTIVITY_WINDOWS[1]
}
