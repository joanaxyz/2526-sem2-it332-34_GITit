import { useEffect, useState } from 'react'
import { BarChart2, CheckCircle2, GitPullRequest, RefreshCw, ShieldCheck } from 'lucide-react'

import type { DashboardSummary, RateMetric } from '@/features/dashboard/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'

type TowerKey = '1' | '2' | '3' | '4'

const TOWER_KEYS: TowerKey[] = ['1', '2', '3', '4']

const SCR_COLOR = '#00F5D4'
const HLCR_COLOR = '#7DD3FC'
const RTA_COLOR = '#34D399'
const ARC_COLOR = '#A78BFA'

function useAnimatedWidth(value: number | null, delay: number) {
  const [width, setWidth] = useState(0)
  useEffect(() => {
    const timer = setTimeout(() => setWidth(value ?? 0), delay)
    return () => clearTimeout(timer)
  }, [value, delay])
  return width
}

function useCountUp(target: number | null, duration = 900, delay = 0): number {
  const [value, setValue] = useState(0)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (target === null || target === 0) {
        setValue(target ?? 0)
        return
      }
      const startTime = performance.now()
      const tick = (now: number) => {
        const p = Math.min((now - startTime) / duration, 1)
        setValue(Math.round((1 - Math.pow(1 - p, 3)) * target))
        if (p < 1) requestAnimationFrame(tick)
      }
      const id = requestAnimationFrame(tick)
      return () => cancelAnimationFrame(id)
    }, delay)
    return () => clearTimeout(timer)
  }, [target, duration, delay])
  return value
}

function MetricBar({
  label,
  Icon,
  metric,
  color,
  hasData,
  barDelay,
}: {
  label: string
  Icon: typeof ShieldCheck
  metric: RateMetric
  color: string
  hasData: boolean
  barDelay: number
}) {
  const barWidth = useAnimatedWidth(metric.value, barDelay)
  const counted = useCountUp(metric.value, 900, barDelay)
  const pct = metric.value ?? 0
  const valueLabel = metric.value === null ? 'No data' : `${metric.value}%`

  return (
    <div className="flex flex-col gap-1.5" aria-label={`${label}: ${valueLabel}`}>
      {/* Label row */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5">
          <Icon
            className="size-3.5 flex-shrink-0"
            style={{ color: hasData ? color : 'rgba(255,255,255,0.2)' }}
          />
          <span
            className="text-[0.65rem] font-semibold uppercase tracking-[0.1em]"
            style={{ color: hasData ? 'rgba(200,220,240,0.75)' : 'rgba(255,255,255,0.2)' }}
          >
            {label}
          </span>
        </div>
        <span
          className="text-xs font-bold tabular-nums"
          style={{ color: hasData ? color : 'rgba(255,255,255,0.18)' }}
        >
          {hasData ? `${counted}%` : '—'}
        </span>
      </div>

      {/* Animated bar */}
      <div
        className="h-2 rounded-full overflow-hidden"
        style={{ background: 'rgba(255,255,255,0.06)' }}
      >
        <div
          className="h-full rounded-full"
          style={{
            width: `${barWidth}%`,
            background: hasData
              ? `linear-gradient(90deg, ${color}88, ${color})`
              : 'rgba(255,255,255,0.08)',
            boxShadow:
              hasData && pct > 0
                ? `0 0 8px ${color}55, 0 0 2px ${color}99`
                : undefined,
            transition: 'width 1.1s cubic-bezier(0.16, 1, 0.3, 1)',
          }}
        />
      </div>

      {/* Attempt count */}
      <p className="text-[0.63rem] text-muted-foreground">
        {metric.denominator
          ? `${metric.numerator}/${metric.denominator} attempts`
          : 'Waiting for practice'}
      </p>
    </div>
  )
}

function TowerPanel({
  towerKey,
  scr,
  hlcr,
  rta,
  arc,
  index,
}: {
  towerKey: TowerKey
  scr: RateMetric
  hlcr: RateMetric
  rta: RateMetric
  arc: RateMetric
  index: number
}) {
  const hasAnyData = scr.denominator > 0 || hlcr.denominator > 0 || rta.denominator > 0 || arc.denominator > 0
  const barDelay = 200 + index * 120

  return (
    <div
      className="tower-performance-hover rounded-lg p-4 transition-all duration-200"
      style={{
        background: hasAnyData
          ? 'rgba(0,180,216,0.05)'
          : 'rgba(255,255,255,0.02)',
        border: hasAnyData
          ? '1px solid rgba(0,180,216,0.2)'
          : '1px solid rgba(255,255,255,0.06)',
        borderTop: hasAnyData
          ? '1px solid rgba(0,245,212,0.22)'
          : '1px solid rgba(255,255,255,0.06)',
        opacity: hasAnyData ? 1 : 0.45,
      }}
    >
      {/* Storey header badge */}
      <div className="flex items-center gap-2 mb-3.5">
        <div
          className="flex items-center gap-1.5 rounded-md px-2 py-0.5"
          style={{
            background: hasAnyData
              ? 'rgba(0,245,212,0.1)'
              : 'rgba(255,255,255,0.06)',
            border: hasAnyData
              ? '1px solid rgba(0,245,212,0.2)'
              : '1px solid rgba(255,255,255,0.08)',
          }}
        >
          <span
            className="font-mono text-[0.6rem] font-bold uppercase tracking-[0.14em]"
            style={{ color: hasAnyData ? 'rgba(0,245,212,0.85)' : 'rgba(255,255,255,0.28)' }}
          >
            Storey {towerKey}
          </span>
        </div>
        {!hasAnyData && (
          <span className="text-[0.6rem] text-muted-foreground/40 font-mono uppercase tracking-widest">
            no data yet
          </span>
        )}
      </div>

      {/* SCR bar — validity gate, full width */}
      <div className="mb-3">
        <MetricBar
          label="Scenario completion"
          Icon={CheckCircle2}
          metric={scr}
          color={SCR_COLOR}
          hasData={scr.denominator > 0}
          barDelay={barDelay}
        />
      </div>

      {/* HLCR + RTA side by side */}
      <div className="grid grid-cols-2 gap-4 max-md:grid-cols-1">
        <MetricBar
          label="Hard completion"
          Icon={ShieldCheck}
          metric={hlcr}
          color={HLCR_COLOR}
          hasData={hlcr.denominator > 0}
          barDelay={barDelay}
        />
        <MetricBar
          label="Retry transfer"
          Icon={GitPullRequest}
          metric={rta}
          color={RTA_COLOR}
          hasData={rta.denominator > 0}
          barDelay={barDelay + 80}
        />
      </div>

      {/* ARC row — full width, raw count (not a percentage) */}
      <div
        className="flex items-center justify-between gap-2 pt-2.5"
        style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}
      >
        <div className="flex items-center gap-1.5">
          <RefreshCw
            className="size-3.5 flex-shrink-0"
            style={{ color: arc.denominator > 0 ? ARC_COLOR : 'rgba(255,255,255,0.2)' }}
          />
          <span
            className="text-[0.65rem] font-semibold uppercase tracking-[0.1em]"
            style={{ color: arc.denominator > 0 ? 'rgba(200,220,240,0.75)' : 'rgba(255,255,255,0.2)' }}
          >
            Avg retries
          </span>
        </div>
        <div className="text-right">
          <span
            className="text-xs font-bold tabular-nums"
            style={{ color: arc.denominator > 0 ? ARC_COLOR : 'rgba(255,255,255,0.18)' }}
          >
            {arc.denominator > 0 ? (arc.value?.toFixed(2) ?? '—') : '—'}
          </span>
          {arc.denominator > 0 && (
            <p className="text-[0.6rem] text-muted-foreground">
              {arc.denominator} completed sessions
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

function formatPercent(value: number | null) {
  return value === null ? 'No data' : `${value}%`
}

export function TowerPerformanceCard({ summary }: { summary: DashboardSummary }) {
  const towerKpis = summary.storey_kpis ?? {}

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart2
            className="size-5"
            style={{ color: '#00F5D4', filter: 'drop-shadow(0 0 6px rgba(0,245,212,0.5))' }}
          />
          Storey hard + retry performance
        </CardTitle>
        <CardDescription className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-0.5">
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="size-3.5" style={{ color: HLCR_COLOR }} />
            <span>Overall hard completion:</span>
            <span
              className="font-semibold"
              style={{ color: HLCR_COLOR }}
            >
              {formatPercent(summary.kpis.hlcr.value)}
            </span>
          </span>
          <span className="text-muted-foreground/30 select-none">·</span>
          <span className="flex items-center gap-1.5">
            <GitPullRequest className="size-3.5" style={{ color: RTA_COLOR }} />
            <span>Overall retry transfer:</span>
            <span
              className="font-semibold"
              style={{ color: RTA_COLOR }}
            >
              {formatPercent(summary.kpis.rta.value)}
            </span>
          </span>
          <span className="text-muted-foreground/30 select-none">·</span>
          <span className="flex items-center gap-1.5">
            <RefreshCw className="size-3.5" style={{ color: ARC_COLOR }} />
            <span>Overall avg retries:</span>
            <span
              className="font-semibold"
              style={{ color: ARC_COLOR }}
            >
              {summary.kpis.arc.denominator === 0 || summary.kpis.arc.value === null
                ? '—'
                : summary.kpis.arc.value.toFixed(2)}
            </span>
          </span>
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {TOWER_KEYS.map((towerKey, index) => {
          const towerMetrics = towerKpis[towerKey]
          if (!towerMetrics) return null
          return (
            <TowerPanel
              key={towerKey}
              towerKey={towerKey}
              scr={towerMetrics.scr}
              hlcr={towerMetrics.hlcr}
              rta={towerMetrics.rta}
              arc={towerMetrics.arc}
              index={index}
            />
          )
        })}
      </CardContent>
    </Card>
  )
}

export const ModulePerformanceCard = TowerPerformanceCard
