import { SUPPLEMENTARY_KPI } from '@/features/admin/utils/kpiCatalogue'
import { kpiEvidence } from '@/features/admin/utils/kpiEvidence'
import type { ApiSchemas } from '@/shared/api/generated/apiTypes'

type Rate = ApiSchemas['RateMetric']

/** Per-module value of the supplementary Retry Success Rate. Full contrast
 * like the objective rows, but with a neutral "No target" tag and no status. */
export function SupplementaryRetryModuleRow({ rate }: { rate: Rate }) {
  return (
    <div className="dk-supp-row" title={SUPPLEMENTARY_KPI.tooltip}>
      <div className="dk-supp-row-label">
        <span className="dk-supp-name">{SUPPLEMENTARY_KPI.name}</span>
        <span className="dk-kpi-tag">No target</span>
      </div>
      <div className="dk-supp-row-value">
        <strong>{rate.value === null ? '—' : `${rate.value}%`}</strong>
        <small>{kpiEvidence('retry_success_rate', rate)}</small>
      </div>
    </div>
  )
}
