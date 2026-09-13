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

function formatValue(value: number | null) {
  return value === null ? '--' : `${Math.round(value)}%`
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
 *
 * It is drawn as a dial rather than a filled disc, and the inner radius does two
 * jobs: a command at 0% reads as an empty ring instead of collapsing to a spike
 * at the centre, and the centre is freed for the one figure the panel is about.
 * That figure follows the pointer, so the shape and the numbers beside it read
 * as one instrument rather than two views of the same list.
 */
export function MasteryRadar({
  axes,
  label,
  activeKey,
  onActiveKeyChange,
  overall,
}: {
  axes: RadarAxis[]
  label: string
  /** Rim label, vertex and hub to emphasise while its command is pointed at. */
  activeKey?: string | null
  /** Reports the axis under the pointer, so the dial can drive its own hub. */
  onActiveKeyChange?: (key: string | null) => void
  /** 0-100, shown in the hub whenever no single command is being pointed at. */
  overall: number
}) {
  const data = axes.map((axis) => ({ ...axis, plotted: axis.value ?? 0 }))
  const animation = chartAnimationDuration()
  const active = activeKey ? data.find((axis) => axis.key === activeKey) : undefined

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
    const dotAxis = payload as RadarAxis | undefined
    const isActive = dotAxis?.key === activeKey
    return (
      <circle
        className="ref-chart-vertex"
        cx={cx}
        cy={cy}
        data-active={isActive ? 'true' : undefined}
        data-empty={!dotAxis?.value ? 'true' : undefined}
        key={key}
        r={isActive ? 5 : 2.75}
      />
    )
  }

  return (
    <div className="ref-chart-dial">
      <div className="ref-chart-dial-plot">
      {/* Square and self-sizing: `height` is the cap, and the dial takes
          whatever width its rail gives it up to that, so the instrument grows
          with the screen instead of sitting at one hard-coded size. */}
      <ChartSurface className="ref-chart-radar" fallbackWidth={520} height={560} label={label}>
        {({ width, height }) => (
          <RadarChart
            cx="50%"
            cy="50%"
            data={data}
            height={Math.max(300, Math.min(width, height))}
            innerRadius="27%"
            onMouseLeave={() => onActiveKeyChange?.(null)}
            onMouseMove={(state) => {
              // Polar charts report the active index as a string, cartesian ones
              // as a number, so it is read through Number() either way.
              const index = state.activeTooltipIndex == null ? NaN : Number(state.activeTooltipIndex)
              const axis = state.isTooltipActive && Number.isInteger(index) ? data[index] : undefined
              onActiveKeyChange?.(axis?.key ?? null)
            }}
            outerRadius="76%"
            width={width}
          >
            <defs>
              <radialGradient id="ref-chart-dial-fill">
                <stop className="ref-chart-dial-from" offset="0%" />
                <stop className="ref-chart-dial-to" offset="100%" />
              </radialGradient>
            </defs>
            <PolarGrid gridType="polygon" radialLines />
            <PolarAngleAxis dataKey="short" tick={renderTick} tickLine={false} />
            {/* No ring labels: at eighteen axes every one of them lands within
                ten degrees of a rim label. The caption under the dial says what
                the rings are, and the list beside it carries every value. */}
            <PolarRadiusAxis axisLine={false} domain={[0, 100]} tick={false} />
            <Tooltip content={RadarTooltip} cursor={false} />
            <Radar
              animationDuration={animation}
              className="ref-chart-shape"
              dataKey="plotted"
              dot={renderDot}
              activeDot={{ r: 5, strokeWidth: 2 }}
              isAnimationActive={animation > 0}
              name="Mastery"
              strokeWidth={2}
            />
          </RadarChart>
        )}
      </ChartSurface>

        {/* Decorative: the panel's own label states the overall figure, and the
            bar list beside the dial states every per-command one. */}
        <p className="ref-chart-hub" aria-hidden="true" data-active={active ? 'true' : undefined}>
          <strong>{active ? formatValue(active.value) : `${overall}%`}</strong>
          <span>{active ? active.short : 'mastery'}</span>
        </p>
      </div>
      <p className="ref-chart-rings">Rings mark 25 · 50 · 75 · 100%</p>
    </div>
  )
}
