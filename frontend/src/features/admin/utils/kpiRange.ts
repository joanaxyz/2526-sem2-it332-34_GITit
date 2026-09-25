import type { KpiDateRange } from '@/features/admin/types'
import type { ApiSchemas } from '@/shared/api/generated/apiTypes'

export const ALL_TIME: KpiDateRange = { startDate: null, endDate: null }

const DATE_LABEL = new Intl.DateTimeFormat('en-US', {
  month: 'short',
  day: 'numeric',
  year: 'numeric',
  timeZone: 'UTC',
})

/** "2026-10-01" -> "Oct 1, 2026". Parsed as UTC so the day never shifts. */
function formatDay(isoDate: string) {
  return DATE_LABEL.format(new Date(`${isoDate}T00:00:00Z`))
}

/** Human label for the range the server actually applied. */
export function kpiRangeLabel(applied: ApiSchemas['AdminKpiRange'] | undefined) {
  const start = applied?.start_date
  const end = applied?.end_date
  if (start && end) return start === end ? formatDay(start) : `${formatDay(start)} – ${formatDay(end)}`
  if (start) return `From ${formatDay(start)}`
  if (end) return `Until ${formatDay(end)}`
  return 'All time'
}
