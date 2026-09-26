import { CheckCircle2, XCircle } from 'lucide-react'

import type { KpiRate, UserKpisResponse } from '@/features/admin/api/adminApi'
import { SUPPLEMENTARY_KPI } from '@/features/admin/utils/kpiCatalogue'
import { kpiEvidence } from '@/features/admin/utils/kpiEvidence'

// ─── KPI catalogue ───────────────────────────────────────────────────────────
const KPI_META = {
  scr:  { abbr: 'SCR',  name: 'Scenario Completion Rate',  target: 80, up: true,  pct: true  },
  car:  { abbr: 'CAR',  name: 'Command Accuracy Rate',     target: 70, up: true,  pct: true  },
  hlcr: { abbr: 'HLCR', name: 'Hard-Level Completion Rate',target: 70, up: true,  pct: true  },
  arc:  { abbr: 'ARC',  name: 'Avg Retry Count',           target: 2,  up: false, pct: false },
  rta:  { abbr: 'RTA',  name: 'Retry Transfer Accuracy',   target: 65, up: true,  pct: true  },
} as const

type KpiKey = keyof typeof KPI_META
type Kpis = NonNullable<UserKpisResponse['kpis']>
type Module = UserKpisResponse['modules'][number]

// Evaluation KPIs only; the supplementary rate is shown but never counted.
const OVERALL_KEYS: KpiKey[] = ['scr', 'car', 'hlcr', 'arc', 'rta']
// CAR is per SO, not per module, so modules have no car column.
const MODULE_KEYS = ['scr', 'hlcr', 'arc', 'rta'] as const satisfies readonly KpiKey[]

function fmtKpi(r: KpiRate, pct: boolean) {
  return r.value === null ? '—' : pct ? `${r.value}%` : r.value.toFixed(2)
}

function kpiStatus(r: KpiRate, key: KpiKey): 'met' | 'miss' | 'none' {
  if (r.value === null || r.denominator === 0) return 'none'
  const { target, up } = KPI_META[key]
  return (up ? r.value >= target : r.value <= target) ? 'met' : 'miss'
}

export function LearnerKpiPanel({ kpis, modules }: { kpis: Kpis; modules: Module[] }) {
  const metCount = OVERALL_KEYS.filter(k => kpiStatus(kpis[k], k) === 'met').length
  const supplementary = kpis.retry_success_rate

  return (
    <div className="kp-wrap">
      {/* met / total: evaluation KPIs only */}
      <div className="kp-summary">
        <span className="kp-summary-label">Targets met</span>
        <span className={`kp-summary-val ${metCount === OVERALL_KEYS.length ? 'kp-val--all' : ''}`}>
          {metCount}/{OVERALL_KEYS.length}
        </span>
      </div>

      {/* overall grid */}
      <div className="kp-grid">
        {OVERALL_KEYS.map(key => {
          const m = KPI_META[key]
          const r = kpis[key]
          const s = kpiStatus(r, key)
          return (
            <div key={key} className={`kp-cell kp-cell--${s}`} title={m.name}>
              <span className="kp-cell-abbr">{m.abbr}</span>
              <strong className={`kp-cell-val kp-val--${s}`}>{fmtKpi(r, m.pct)}</strong>
              <span className="kp-cell-target">{m.up ? '≥' : '≤'}{m.target}{m.pct ? '%' : ''}</span>
              <span className="kp-cell-evidence">{kpiEvidence(key, r)}</span>
              <span className={`kp-cell-icon kp-icon--${s}`} aria-hidden="true">
                {s === 'met'  ? <CheckCircle2 /> : s === 'miss' ? <XCircle /> : null}
              </span>
            </div>
          )
        })}
        <div className="kp-cell kp-cell--supplementary" title={SUPPLEMENTARY_KPI.tooltip}>
          <span className="kp-cell-abbr">{SUPPLEMENTARY_KPI.abbr}</span>
          <strong className="kp-cell-val">{fmtKpi(supplementary, SUPPLEMENTARY_KPI.pct)}</strong>
          <span className="kp-cell-tag">No target</span>
          <span className="kp-cell-evidence">{kpiEvidence('retry_success_rate', supplementary)}</span>
        </div>
      </div>

      {/* per-module table */}
      {modules.length > 0 && (
        <div className="kp-mod-wrap">
          <p className="kp-mod-label">By module</p>
          <table className="kp-mod-table">
            <thead>
              <tr>
                <th>Mod</th>
                {MODULE_KEYS.map(k => <th key={k}>{KPI_META[k].abbr}</th>)}
                <th title={SUPPLEMENTARY_KPI.tooltip}>{SUPPLEMENTARY_KPI.abbr}</th>
              </tr>
            </thead>
            <tbody>
              {modules.map(mod => (
                <tr key={mod.number}>
                  <td className="kp-mod-num">M{mod.number}</td>
                  {MODULE_KEYS.map(key => {
                    const r = mod[key]
                    const s = kpiStatus(r, key)
                    return (
                      <td key={key} className={`kp-mod-cell kp-mod-cell--${s}`} title={kpiEvidence(key, r)}>
                        {fmtKpi(r, KPI_META[key].pct)}
                      </td>
                    )
                  })}
                  <td
                    className="kp-mod-cell kp-mod-cell--supplementary"
                    title={kpiEvidence('retry_success_rate', mod.retry_success_rate)}
                  >
                    {fmtKpi(mod.retry_success_rate, SUPPLEMENTARY_KPI.pct)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
