import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from 'recharts'

import type { SkillAxis } from '@/features/stats/types'

const CYAN = '#00F5D4'
const BLUE = '#00B4D8'

type AxisDatum = { key: string; label: string; hint: string; value: number; shown: number | null }

type TextAnchor = 'start' | 'middle' | 'end' | 'inherit'

function AxisTick({
  x,
  y,
  textAnchor,
  payload,
  data,
}: {
  x?: string | number
  y?: string | number
  textAnchor?: string
  payload?: { value: string }
  data: AxisDatum[]
}) {
  const px = Number(x) || 0
  const py = Number(y) || 0
  const anchor = (textAnchor as TextAnchor) ?? 'middle'
  const item = data.find((d) => d.label === payload?.value)
  const val = item?.shown ?? null
  return (
    <g>
      <text x={px} y={py} textAnchor={anchor} dominantBaseline="central" fill="#7DD3FC" fontSize={11} fontWeight={700}>
        {payload?.value}
      </text>
      <text
        x={px}
        y={py + 13}
        textAnchor={anchor}
        dominantBaseline="central"
        fill={val === null ? 'rgba(255,255,255,0.32)' : CYAN}
        fontSize={10}
        fontWeight={600}
        fontFamily="JetBrains Mono, ui-monospace, monospace"
      >
        {val === null ? '-' : Math.round(val)}
      </text>
    </g>
  )
}

export function SkillProfileRadar({ axes }: { axes: SkillAxis[] }) {
  const hasAny = axes.some((a) => a.value !== null)
  const data: AxisDatum[] = axes.map((a) => ({
    key: a.key,
    label: a.label,
    hint: a.hint,
    value: a.value ?? 0,
    shown: a.value,
  }))

  return (
    <section className="stats-radar-panel flex h-full flex-col" aria-label="Skill profile">
      <div className="flex items-center gap-2.5">
        <span
          className="size-2.5 rotate-45 rounded-[2px]"
          style={{ background: CYAN, boxShadow: `0 0 8px ${CYAN}` }}
          aria-hidden="true"
        />
        <h2 className="text-[0.95rem] font-bold leading-tight tracking-tight">Skill Profile</h2>
      </div>

      <div className="mx-auto w-full max-w-[440px] flex-1" style={{ minHeight: 330 }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} outerRadius="74%" margin={{ top: 26, right: 38, bottom: 26, left: 38 }}>
            <defs>
              <radialGradient id="radar-fill" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor={CYAN} stopOpacity={0.5} />
                <stop offset="100%" stopColor={BLUE} stopOpacity={0.12} />
              </radialGradient>
            </defs>
            <PolarGrid gridType="polygon" stroke="rgba(255,255,255,0.08)" />
            <PolarAngleAxis dataKey="label" tick={(props) => <AxisTick {...props} data={data} />} />
            <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
            {hasAny && (
              <Radar
                dataKey="value"
                stroke={CYAN}
                strokeWidth={2}
                fill="url(#radar-fill)"
                fillOpacity={1}
                dot={{ r: 3, fill: CYAN, stroke: CYAN }}
                isAnimationActive
                animationBegin={120}
                animationDuration={850}
                animationEasing="ease-out"
                style={{ filter: `drop-shadow(0 0 6px ${CYAN}88)` }}
              />
            )}
          </RadarChart>
        </ResponsiveContainer>
      </div>

      <p className="sr-only">
        {hasAny
          ? `Skill profile: ${data
              .map((d) => `${d.label} ${d.shown === null ? 'no data' : `${Math.round(d.shown)} out of 100`}`)
              .join(', ')}.`
          : 'Skill profile: no data yet.'}
      </p>

      {!hasAny && (
        <p className="-mt-3 text-center text-sm text-muted-foreground/85">
          Play a few levels and your profile will start to take shape.
        </p>
      )}
    </section>
  )
}
