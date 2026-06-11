import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from 'recharts'

import type { SkillAxis } from '@/features/stats/types'
import { GamePanel } from '@/shared/components/GamePanel'

const CYAN = '#00F5D4'
const BLUE = '#00B4D8'

type AxisDatum = { key: string; label: string; hint: string; value: number; shown: number | null }

type TextAnchor = 'start' | 'middle' | 'end' | 'inherit'

/** Axis label with its current score stacked underneath. Recharts hands us loose
 *  tick props (x/y as string|number), so we coerce them here. */
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
        {val === null ? '—' : Math.round(val)}
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
    <GamePanel className="flex h-full flex-col p-5">
      <div className="relative z-[1]">
        <div className="flex items-center gap-2.5">
          <span className="game-chip size-8">
            <span
              className="size-3.5 rotate-45 rounded-[3px]"
              style={{ background: CYAN, boxShadow: `0 0 8px ${CYAN}` }}
            />
          </span>
          <div>
            <p className="font-mono text-[0.6rem] font-semibold uppercase tracking-[0.2em] text-aurora-blue/80">
              Skill Profile
            </p>
            <h2 className="text-base font-bold leading-tight tracking-tight">Six disciplines of the tower</h2>
          </div>
        </div>
      </div>

      <div className="relative z-[1] mx-auto w-full max-w-[440px] flex-1" style={{ minHeight: 340 }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} outerRadius="74%" margin={{ top: 26, right: 38, bottom: 26, left: 38 }}>
            <defs>
              <radialGradient id="radar-fill" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor={CYAN} stopOpacity={0.5} />
                <stop offset="100%" stopColor={BLUE} stopOpacity={0.12} />
              </radialGradient>
            </defs>
            <PolarGrid gridType="polygon" stroke="rgba(255,255,255,0.08)" />
            <PolarAngleAxis
              dataKey="label"
              tick={(props) => <AxisTick {...props} data={data} />}
            />
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

      {/* Accessible fallback for the chart */}
      <p className="sr-only">
        {hasAny
          ? `Skill profile: ${data
              .map((d) => `${d.label} ${d.shown === null ? 'no data' : `${Math.round(d.shown)} out of 100`}`)
              .join(', ')}.`
          : 'Skill profile: no data yet.'}
      </p>

      {!hasAny && (
        <p className="relative z-[1] -mt-3 text-center text-sm text-muted-foreground/70">
          Play a few quests and your profile will start to take shape.
        </p>
      )}

      {/* Compact legend — hover a chip for what each axis measures */}
      <ul className="relative z-[1] mt-2 flex flex-wrap justify-center gap-1.5">
        {axes.map((axis) => (
          <li key={axis.key}>
            <span
              className="inline-flex cursor-help items-center gap-1.5 rounded-full border border-white/[0.08] bg-white/[0.03] px-2.5 py-1 font-mono text-[0.6rem] font-semibold uppercase tracking-[0.06em] text-muted-foreground transition-colors hover:border-aurora-cyan/40 hover:text-foreground"
              title={axis.hint}
            >
              <span
                className="size-1.5 rounded-full"
                style={{
                  background: axis.value === null ? 'rgba(255,255,255,0.2)' : CYAN,
                  boxShadow: axis.value === null ? 'none' : `0 0 4px ${CYAN}`,
                }}
                aria-hidden="true"
              />
              {axis.label}
              <span style={{ color: axis.value === null ? 'rgba(255,255,255,0.3)' : CYAN }}>
                {axis.value === null ? '—' : Math.round(axis.value)}
              </span>
            </span>
          </li>
        ))}
      </ul>
    </GamePanel>
  )
}
