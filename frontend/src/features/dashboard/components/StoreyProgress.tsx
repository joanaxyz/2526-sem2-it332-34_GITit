import { Castle } from 'lucide-react'
import { Link } from 'react-router-dom'

import type { DashboardSummary, RateMetric } from '@/features/dashboard/types'
import { GamePanel } from '@/shared/components/GamePanel'

function MiniBar({ label, metric, color }: { label: string; metric: RateMetric; color: string }) {
  const hasData = metric.value !== null
  const pct = Math.max(0, Math.min(100, metric.value ?? 0))
  return (
    <div className="flex items-center gap-2">
      <span className="w-9 shrink-0 font-mono text-[0.56rem] font-semibold uppercase tracking-[0.08em] text-muted-foreground/70">
        {label}
      </span>
      <div className="h-1.5 min-w-0 flex-1 overflow-hidden rounded-full bg-white/[0.06]">
        {hasData && (
          <div
            className="h-full rounded-full"
            style={{
              width: `${pct}%`,
              background: `linear-gradient(90deg, ${color}88, ${color})`,
              boxShadow: `0 0 6px ${color}66`,
              transition: 'width 1s cubic-bezier(0.16, 1, 0.3, 1)',
            }}
          />
        )}
      </div>
      <span
        className="w-8 shrink-0 text-right font-mono text-[0.6rem] font-bold"
        style={{ color: hasData ? color : 'rgba(255,255,255,0.3)' }}
      >
        {hasData ? `${Math.round(pct)}%` : '—'}
      </span>
    </div>
  )
}

/**
 * Per-storey tower record — glowing door motif per floor with scenario/hard
 * clear bars and retry micro-stats. The "Most Played" analog.
 */
export function StoreyProgress({ summary }: { summary: DashboardSummary }) {
  const storeys = Object.entries(summary.storey_kpis)
    .map(([storey, kpis]) => ({ storey: Number(storey), kpis }))
    .filter(({ storey }) => Number.isFinite(storey))
    .sort((a, b) => a.storey - b.storey)

  return (
    <GamePanel className="flex flex-col p-5">
      <div className="relative z-[1] mb-3">
        <h3 className="font-mono text-[0.66rem] font-semibold uppercase tracking-[0.2em] text-aurora-blue/80">
          Tower Record
        </h3>
        <p className="mt-1 text-xs text-muted-foreground">Floor-by-floor performance.</p>
      </div>

      {storeys.length > 0 ? (
        <ol className="relative z-[1] flex flex-col gap-2.5" aria-label="Per-storey performance">
          {storeys.map(({ storey, kpis }, i) => (
            <li
              key={storey}
              className="animate-fade-in-up flex items-center gap-3 rounded-lg border border-white/[0.05] bg-white/[0.02] p-2.5"
              style={{ animationDelay: `${i * 60}ms` }}
            >
              <span className="storey-door-chip" aria-hidden="true">
                {storey}
              </span>
              <div className="min-w-0 flex-1">
                <div className="mb-1 flex items-baseline justify-between gap-2">
                  <p className="text-xs font-bold tracking-tight">Storey {storey}</p>
                  <p className="font-mono text-[0.56rem] text-muted-foreground/60">
                    rta {kpis.rta.value === null ? '—' : `${Math.round(kpis.rta.value)}%`} · ret{' '}
                    {kpis.arc.value === null ? '—' : `${kpis.arc.value.toFixed(1)}×`}
                  </p>
                </div>
                <div className="flex flex-col gap-1">
                  <MiniBar label="SCR" metric={kpis.scr} color="#00F5D4" />
                  <MiniBar label="HARD" metric={kpis.hlcr} color="#A78BFA" />
                </div>
              </div>
            </li>
          ))}
        </ol>
      ) : (
        <div className="relative z-[1] flex flex-col items-center gap-3 rounded-lg border border-dashed border-aurora-blue/20 px-6 py-7 text-center">
          <span className="game-chip size-11">
            <Castle aria-hidden="true" className="size-5 text-aurora-cyan" />
          </span>
          <p className="text-sm font-semibold">No floors climbed yet</p>
          <p className="max-w-xs text-xs leading-5 text-muted-foreground">
            Each storey you enter starts its own record of clears and retries.
          </p>
          <Link
            to="/tower"
            className="font-mono text-[0.64rem] font-semibold uppercase tracking-[0.1em] text-aurora-cyan/80 transition-colors hover:text-aurora-cyan"
          >
            Climb the tower →
          </Link>
        </div>
      )}
    </GamePanel>
  )
}
