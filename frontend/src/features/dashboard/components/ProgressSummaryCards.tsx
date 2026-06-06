import { useEffect, useState } from 'react'
import { CheckCircle2, Crosshair, GitPullRequest, RefreshCw, ShieldCheck } from 'lucide-react'

import type { DashboardSummary } from '@/features/dashboard/types'
import { Card, CardContent } from '@/shared/components/Card'

const RING_R = 36
const RING_C = 2 * Math.PI * RING_R // ≈ 226.2

const metricConfig = [
  {
    key: 'scr' as const,
    label: 'Scenario completion',
    Icon: CheckCircle2,
    color: '#00F5D4',
    topBorder: 'rgba(0,245,212,0.55)',
  },
  {
    key: 'car' as const,
    label: 'Command accuracy',
    Icon: Crosshair,
    color: '#00B4D8',
    topBorder: 'rgba(0,180,216,0.55)',
  },
  {
    key: 'hlcr' as const,
    label: 'Hard completion',
    Icon: ShieldCheck,
    color: '#7DD3FC',
    topBorder: 'rgba(125,211,252,0.55)',
  },
  {
    key: 'rta' as const,
    label: 'Retry transfer',
    Icon: GitPullRequest,
    color: '#34D399',
    topBorder: 'rgba(52,211,153,0.55)',
  },
  {
    key: 'arc' as const,
    label: 'Avg retry count',
    Icon: RefreshCw,
    color: '#A78BFA',
    topBorder: 'rgba(167,139,250,0.55)',
    format: 'count' as const,
  },
]

function useCountUp(target: number | null, duration = 1000): number {
  const [value, setValue] = useState(0)
  useEffect(() => {
    if (target === null || target === 0) { setValue(target ?? 0); return }
    const startTime = performance.now()
    const tick = (now: number) => {
      const p = Math.min((now - startTime) / duration, 1)
      setValue(Math.round((1 - Math.pow(1 - p, 3)) * target))
      if (p < 1) requestAnimationFrame(tick)
    }
    const id = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(id)
  }, [target, duration])
  return value
}

function RadialRing({
  counted,
  hasData,
  color,
}: {
  counted: number
  hasData: boolean
  color: string
}) {
  const offset = hasData ? RING_C * (1 - counted / 100) : RING_C

  return (
    <div className="relative flex-shrink-0" style={{ width: 82, height: 82 }}>
      <svg width="82" height="82" viewBox="0 0 88 88" fill="none">
        {/* Track ring */}
        <circle
          cx="44"
          cy="44"
          r={RING_R}
          stroke={hasData ? 'rgba(255,255,255,0.07)' : 'rgba(255,255,255,0.12)'}
          strokeWidth="6.5"
          strokeDasharray={hasData ? undefined : '5 3.8'}
          strokeLinecap="round"
        />
        {/* Progress arc – offset driven by useCountUp so it fills in sync with the number */}
        {hasData && (
          <circle
            cx="44"
            cy="44"
            r={RING_R}
            stroke={color}
            strokeWidth="6.5"
            strokeLinecap="round"
            strokeDasharray={RING_C}
            strokeDashoffset={offset}
            transform="rotate(-90 44 44)"
            style={{ filter: `drop-shadow(0 0 5px ${color}99)` }}
          />
        )}
      </svg>
      {/* Dim glow saucer behind ring when data is present */}
      {hasData && (
        <div
          className="absolute inset-0 rounded-full pointer-events-none"
          style={{
            background: `radial-gradient(ellipse at center, ${color}0f 0%, transparent 70%)`,
          }}
        />
      )}
    </div>
  )
}

function StatCard({
  config,
  value,
  detail,
  index,
}: {
  config: (typeof metricConfig)[number]
  value: number | null
  detail: string
  index: number
}) {
  const isCount = 'format' in config && config.format === 'count'
  const hasData = value !== null
  const counted = useCountUp(isCount ? null : value)

  return (
    <Card
      className="stat-card-hover group shadow-none"
      style={{
        borderTop: `2px solid ${config.topBorder}`,
        animationDelay: `${index * 80}ms`,
      }}
    >
      <CardContent className="p-4">
        <div className="flex items-center justify-between gap-3">
          {/* Left: label + number + detail */}
          <div className="flex flex-col gap-0.5 min-w-0">
            <div className="flex items-center gap-1.5 mb-1">
              <config.Icon
                className="size-3.5 flex-shrink-0 transition-colors duration-200 group-hover:drop-shadow-[0_0_6px_currentColor]"
                style={{ color: config.color }}
              />
              <p className="font-mono text-[0.63rem] uppercase tracking-[0.11em] text-aurora-blue/80 truncate">
                {config.label}
              </p>
            </div>

            {hasData ? (
              <p
                className="text-[1.85rem] font-extrabold tracking-tight leading-none"
                style={{
                  color: config.color,
                  textShadow: `0 0 20px ${config.color}55`,
                }}
              >
                {isCount ? value!.toFixed(2) : `${counted}%`}
              </p>
            ) : (
              <p className="text-sm text-muted-foreground/50 font-mono leading-none mt-1">
                No data
              </p>
            )}

            <p className="mt-1.5 text-[0.7rem] text-muted-foreground leading-snug">
              {detail}
            </p>
          </div>

          {/* Right: animated radial ring — suppressed for count-format metrics */}
          <RadialRing counted={counted} hasData={isCount ? false : hasData} color={config.color} />
        </div>
      </CardContent>
    </Card>
  )
}

export function ProgressSummaryCards({ summary }: { summary: DashboardSummary }) {
  return (
    <section className="grid grid-cols-2 gap-3 2xl:grid-cols-3 max-md:grid-cols-1">
      {metricConfig.map((config, index) => {
        const metric = summary.kpis[config.key]
        const isCount = 'format' in config && config.format === 'count'
        const detail = isCount
          ? `${metric.denominator} completed sessions`
          : config.key === 'car'
            ? `${metric.denominator} completed attempts`
            : `${metric.numerator}/${metric.denominator} attempts`
        return (
          <StatCard
            key={config.key}
            config={config}
            value={metric.value}
            detail={metric.denominator ? detail : 'Waiting for practice'}
            index={index}
          />
        )
      })}
    </section>
  )
}
