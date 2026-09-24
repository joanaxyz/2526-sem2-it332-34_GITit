import type { ApiSchemas } from '@/shared/api/generated/apiTypes'

type Rate = ApiSchemas['RateMetric']

const RETRY_SUCCESS_LABEL = 'Retry Success Rate (supplementary)'

const RETRY_SUCCESS_TOOLTIP =
  'Share of retry sessions that eventually ended in completion, any variant, any attempt. ' +
  'Supplementary indicator only; RTA is the evaluation KPI for SO 3.5, SO 4.5 and RQ4.'

function formatRate(rate: Rate) {
  return rate.value === null ? '—' : `${rate.value}%`
}

function evidence(rate: Rate) {
  return rate.denominator > 0 ? `${rate.numerator} / ${rate.denominator} retry sessions` : 'No data yet'
}

/** The old RTR measure, shown for context. Deliberately secondary: no target,
 * no met/missed status, and not counted in "targets met". */
export function SupplementaryRetryCard({ rate }: { rate: Rate }) {
  return (
    <aside className="dk-supp-card" title={RETRY_SUCCESS_TOOLTIP} aria-label={RETRY_SUCCESS_LABEL}>
      <div className="dk-supp-head">
        <span className="dk-supp-name">{RETRY_SUCCESS_LABEL}</span>
        <span className="dk-supp-tag">No target</span>
      </div>
      <div className="dk-supp-value">{formatRate(rate)}</div>
      <p className="dk-supp-evidence">{evidence(rate)}</p>
      <p className="dk-supp-note">{RETRY_SUCCESS_TOOLTIP}</p>
    </aside>
  )
}

export function SupplementaryRetryModuleRow({ rate }: { rate: Rate }) {
  return (
    <div className="dk-supp-row" title={RETRY_SUCCESS_TOOLTIP}>
      <span className="dk-supp-name">{RETRY_SUCCESS_LABEL}</span>
      <span className="dk-supp-row-value">
        {formatRate(rate)}
        <small>{rate.denominator > 0 ? ` (${rate.numerator}/${rate.denominator})` : ''}</small>
      </span>
    </div>
  )
}
