import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceDot,
  Tooltip,
  XAxis,
  YAxis,
  type TooltipContentProps,
} from 'recharts'

import { ChartSurface } from './ChartSurface'
import { chartAnimationDuration } from './chartMotion'
import { ChartTooltipCard } from './ChartTooltip'

export type ActivityPoint = {
  /** ISO date of the bucket's first day. */
  date: string
  /** Axis tick, e.g. "Jun 9" or "Jun". */
  label: string
  /** Tooltip title, spelled out. */
  caption: string
  commandsRun: number
  levelsCompleted: number
}

/** Both plots share these so a column always sits under its own day. */
const MARGIN = { top: 10, right: 14, bottom: 0, left: 0 }
const AXIS_WIDTH = 30

function ActivityTooltip({ active, payload }: TooltipContentProps) {
  const point = payload?.[0]?.payload as ActivityPoint | undefined
  if (!active || !point || !point.date) return null

  return (
    <ChartTooltipCard
      title={point.caption}
      rows={[
        {
          key: 'commands',
          label: 'Commands run',
          value: point.commandsRun.toLocaleString(),
          tone: 'progress',
        },
        {
          key: 'levels',
          label: 'Levels finished',
          value: point.levelsCompleted.toLocaleString(),
          tone: 'muted',
        },
      ]}
    />
  )
}

/**
 * Two measures of different size (commands run in the tens, levels finished in
 * the ones) never share a y-axis: the second scale would be arbitrary and would
 * invent a correlation. They are small multiples instead — one plot each, one
 * shared day axis, one synchronised crosshair.
 */
export function ActivityTrendChart({
  points,
  label,
  peakIndex,
  peakLabel,
}: {
  points: ActivityPoint[]
  label: string
  /** Direct-labels the busiest bucket; -1 when there is nothing to call out. */
  peakIndex: number
  peakLabel?: string | null
}) {
  const animation = chartAnimationDuration()
  const peak = peakIndex >= 0 ? points[peakIndex] : undefined
  // Aim for about seven ticks whatever the span: every day over a week, every
  // fifth over a month, every other month over a year.
  const tickInterval = Math.max(0, Math.ceil(points.length / 7) - 1)

  return (
    <ChartSurface className="ref-chart-activity" height={196} label={label}>
      {({ width }) => (
        <>
          <AreaChart
            accessibilityLayer
            data={points}
            height={124}
            margin={MARGIN}
            syncId="activity-trend"
            width={width}
          >
            <defs>
              <linearGradient id="ref-chart-activity-fill" x1="0" x2="0" y1="0" y2="1">
                <stop className="ref-chart-fill-from" offset="0%" />
                <stop className="ref-chart-fill-to" offset="100%" />
              </linearGradient>
            </defs>
            <CartesianGrid horizontal vertical={false} />
            <XAxis dataKey="label" hide />
            <YAxis allowDecimals={false} axisLine={false} tickCount={3} tickLine={false} width={AXIS_WIDTH} />
            <Tooltip content={ActivityTooltip} cursor={{ strokeWidth: 1 }} />
            <Area
              activeDot={{ r: 4, strokeWidth: 2 }}
              animationDuration={animation}
              isAnimationActive={animation > 0}
              className="ref-chart-area"
              dataKey="commandsRun"
              dot={false}
              fill="url(#ref-chart-activity-fill)"
              name="Commands run"
              strokeWidth={2}
              type="linear"
            />
            {peak && peakLabel ? (
              <ReferenceDot
                className="ref-chart-peak"
                label={{ position: 'top', value: peakLabel }}
                r={3.5}
                x={peak.label}
                y={peak.commandsRun}
              />
            ) : null}
          </AreaChart>

          <BarChart
            accessibilityLayer
            barCategoryGap="28%"
            data={points}
            height={72}
            margin={MARGIN}
            syncId="activity-trend"
            width={width}
          >
            <XAxis dataKey="label" interval={tickInterval} tickLine={false} tickMargin={6} />
            {/* Mirrors the area plot's gutter exactly — `hide` would drop the
                reserved width and slide every column off its own day. */}
            <YAxis allowDecimals={false} axisLine={false} tick={false} tickLine={false} width={AXIS_WIDTH} />
            {/* No second Tooltip: the shared syncId already raises the one above,
                and two cards for one day read as a rendering fault. */}
            <Bar
              animationDuration={animation}
              isAnimationActive={animation > 0}
              className="ref-chart-column"
              dataKey="levelsCompleted"
              name="Levels finished"
              radius={[3, 3, 0, 0]}
            />
          </BarChart>
        </>
      )}
    </ChartSurface>
  )
}
