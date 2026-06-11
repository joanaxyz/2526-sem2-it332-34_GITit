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
    <GamePanel className="flex flex-col p-5">
      <div className="relative z-[1] mb-1">
        <div className="flex items-center gap-2">
          <span className="game-chip size-7">
            <span className="size-3 rounded-[3px]" style={{ background: CYAN, boxShadow: `0 0 8px ${CYAN}` }} />
          </span>
          <h2 className="text-lg font-bold tracking-tight">Your skill profile</h2>
        </div>
        <p className="mt-1 text-xs text-muted-foreground">
          Six qualities that grow as you play. The wider the shape, the stronger you are.
        </p>
      </div>

      <div className="relative z-[1] mx-auto w-full max-w-[420px]" style={{ height: 320 }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} outerRadius="72%" margin={{ top: 24, right: 36, bottom: 24, left: 36 }}>
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

      {!hasAny && (
        <p className="relative z-[1] -mt-4 text-center text-sm text-muted-foreground/70">
          Play a few quests and your profile will start to take shape.
        </p>
      )}

      {/* Plain-language legend */}
      <ul className="relative z-[1] mt-3 grid grid-cols-2 gap-x-4 gap-y-1.5 max-sm:grid-cols-1">
        {axes.map((axis) => (
          <li key={axis.key} className="flex items-baseline gap-1.5 text-[0.7rem] leading-snug text-muted-foreground">
            <span className="font-semibold text-foreground/80">{axis.label}:</span>
            <span>{axis.hint}</span>
          </li>
        ))}
      </ul>
    </GamePanel>
  )
}
