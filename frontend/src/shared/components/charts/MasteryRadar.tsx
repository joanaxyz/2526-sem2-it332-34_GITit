import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  Tooltip,
  type BaseTickContentProps,
  type DotItemDotProps,
  type TooltipContentProps,
} from 'recharts'

import { ChartSurface } from './ChartSurface'
import { chartAnimationDuration } from './chartMotion'
import { ChartTooltipCard } from './ChartTooltip'

export type RadarAxis = {
  key: string
  /** Full name, e.g. "Stage Changes". */
  label: string
  /** Machine name for the rim, e.g. "add". */
  short: string
  /** 0-100; null reads as untouched, which is a real 0 on the shape. */
  value: number | null
  caption?: string
}

function RadarTooltip({ active, payload }: TooltipContentProps) {
  const axis = payload?.[0]?.payload as RadarAxis | undefined
  if (!active || !axis) return null

  return (
    <ChartTooltipCard
      title={axis.label}
      caption={axis.caption}
      rows={[
        {
          key: 'mastery',
          label: 'Mastery',
          value: axis.value === null ? 'Not started' : `${Math.round(axis.value)}%`,
          tone: 'progress',
        },
      ]}
    />
  )
}

/**
 * The skill profile as a shape rather than a column of bars: one glance says
 * whether a learner is even across the command set or spiked on the few they
 * keep reaching for. The bar list beside it stays the precise readout — this is
 * the silhouette, and it is one series, so it needs no legend.
 */
export function MasteryRadar({
  axes,
  label,
  activeKey,
}: {
  axes: RadarAxis[]
  label: string
  /** Rim label + vertex to emphasise while its row is hovered or focused. */
  activeKey?: string | null
}) {
  const data = axes.map((axis) => ({ ...axis, plotted: axis.value ?? 0 }))
  const animation = chartAnimationDuration()

  function renderTick({ x, y, textAnchor, index }: BaseTickContentProps) {
    const axis = data[index]
    return (
      <text
        className="ref-chart-rim-label"
        data-active={axis && axis.key === activeKey ? 'true' : undefined}
        dominantBaseline="central"
        textAnchor={textAnchor}
        x={x}
        y={y}
      >
        {axis?.short}
      </text>
    )
  }

  function renderDot({ cx, cy, payload, key }: DotItemDotProps) {
    const active = (payload as RadarAxis | undefined)?.key === activeKey
    return (
      <circle
        className="ref-chart-vertex"
        cx={cx}
        cy={cy}
        data-active={active ? 'true' : undefined}
        key={key}
        r={active ? 4.5 : 2.5}
      />
    )
  }

  return (
    <ChartSurface className="ref-chart-radar" fallbackWidth={320} height={302} label={label}>
      {({ width, height }) => (
        <RadarChart cx="50%" cy="50%" data={data} height={height} outerRadius="72%" width={width}>
          <PolarGrid gridType="polygon" radialLines />
          <PolarAngleAxis dataKey="short" tick={renderTick} tickLine={false} />
          {/* No radius ticks: at twelve axes every ring label lands within 15 degrees
              of a rim label. The bar list beside the shape carries the numbers. */}
          <PolarRadiusAxis axisLine={false} domain={[0, 100]} tick={false} />
          <Tooltip content={RadarTooltip} cursor={false} />
          <Radar
            animationDuration={animation}
            className="ref-chart-shape"
            dataKey="plotted"
            dot={renderDot}
            activeDot={{ r: 4.5, strokeWidth: 2 }}
            isAnimationActive={animation > 0}
            name="Mastery"
            strokeWidth={2}
          />
        </RadarChart>
      )}
    </ChartSurface>
  )
}
