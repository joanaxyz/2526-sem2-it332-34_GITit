import { CalendarRange } from 'lucide-react'

import type { KpiDateRange } from '@/features/admin/types'
import { ALL_TIME, kpiRangeLabel } from '@/features/admin/utils/kpiRange'
import type { ApiSchemas } from '@/shared/api/generated/apiTypes'

type AppliedRange = ApiSchemas['AdminKpiRange']

export function KpiRangePicker({
  value,
  applied,
  onChange,
}: {
  value: KpiDateRange
  applied: AppliedRange | undefined
  onChange: (next: KpiDateRange) => void
}) {
  const isAllTime = !value.startDate && !value.endDate

  // An end before the start would be rejected by the API; keep the last valid range.
  const update = (next: KpiDateRange) => {
    if (next.startDate && next.endDate && next.startDate > next.endDate) return
    onChange(next)
  }

  return (
    <div className="dk-range" role="group" aria-label="KPI date range">
      <p className="dk-range-label" aria-live="polite">
        <CalendarRange aria-hidden="true" />
        <span>
          Showing <strong>{kpiRangeLabel(applied)}</strong>
        </span>
        <span className="dk-range-tz">Philippine time (UTC+8)</span>
      </p>
      <div className="dk-range-fields">
        <label>
          <span>From</span>
          <input
            type="date"
            value={value.startDate ?? ''}
            max={value.endDate ?? undefined}
            onChange={(event) => update({ ...value, startDate: event.target.value || null })}
          />
        </label>
        <label>
          <span>To</span>
          <input
            type="date"
            value={value.endDate ?? ''}
            min={value.startDate ?? undefined}
            onChange={(event) => update({ ...value, endDate: event.target.value || null })}
          />
        </label>
        <button
          type="button"
          className="dk-range-reset"
          onClick={() => onChange(ALL_TIME)}
          disabled={isAllTime}
        >
          All time
        </button>
      </div>
    </div>
  )
}
