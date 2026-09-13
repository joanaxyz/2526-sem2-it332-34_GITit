import { Bar, BarChart, CartesianGrid, LabelList, Tooltip, XAxis, YAxis, type TooltipContentProps } from 'recharts'

import { ChartSurface } from './ChartSurface'
import { chartAnimationDuration } from './chartMotion'
import { ChartTooltipCard } from './ChartTooltip'

export type ColumnPoint = {
  key: string
  /** Tick under the column, e.g. "M2". */
  label: string
  /** Tooltip title, e.g. "Module 2 - Branching Basics". */
  caption: string
  /** null means "never attempted", which is not the same fact as 0. */
  value: number | null
  /** What the value was measured over, e.g. "3 of 6 runs". */
  detail: string
  display: string
}

type LabelProps = {
  x?: number | string
  y?: number | string
  width?: number | string
  index?: number
}

function toNumber(value: number | string | undefined) {
  return typeof value === 'number' ? value : Number.parseFloat(String(value ?? 0)) || 0
}

/**
 * One measure across a handful of categories, direct-labelled so every value is
 * readable without hovering. Four of these side by side beat one grouped chart
 * here: the measures have different units, and a shared axis would have to lie
 * about at least one of them.
 */
export function MiniColumnChart({
  points,
  title,
  label,
  max,
}: {
  points: ColumnPoint[]
  title: string
  label: string
  /** Upper bound of the y-axis; omit to let the data set it. */
  max?: number
}) {
  const animation = chartAnimationDuration()
  const data = points.map((point) => ({ ...point, plotted: point.value ?? 0 }))

  function renderValue({ x, y, width, index = 0 }: LabelProps) {
    const point = data[index]
    if (!point) return null
    return (
      <text
        className="ref-chart-column-value"
        data-empty={point.value === null ? 'true' : undefined}
        textAnchor="middle"
        x={toNumber(x) + toNumber(width) / 2}
        y={toNumber(y) - 6}
      >
        {point.display}
      </text>
    )
  }

  function renderTooltip({ active, payload }: TooltipContentProps) {
    const point = payload?.[0]?.payload as ColumnPoint | undefined
    if (!active || !point) return null
    return (
      <ChartTooltipCard
        title={point.caption}
        caption={title}
        rows={[{ key: 'value', label: point.display, value: point.detail, tone: 'progress' }]}
      />
    )
  }

  return (
    <figure className="ref-chart-mini">
      <figcaption>{title}</figcaption>
      <ChartSurface fallbackWidth={240} height={124} label={label}>
        {({ width, height }) => (
          <BarChart
            accessibilityLayer
            barCategoryGap="30%"
            data={data}
            height={height}
            margin={{ top: 18, right: 4, bottom: 0, left: 4 }}
            width={width}
          >
            <CartesianGrid horizontal vertical={false} />
            <XAxis axisLine={false} dataKey="label" tickLine={false} tickMargin={6} />
            <YAxis domain={[0, max ?? 'auto']} hide />
            <Tooltip content={renderTooltip} cursor={{ fillOpacity: 0.08 }} />
            <Bar
              animationDuration={animation}
              isAnimationActive={animation > 0}
              className="ref-chart-column"
              dataKey="plotted"
              maxBarSize={24}
              minPointSize={1}
              name={title}
              radius={[4, 4, 0, 0]}
            >
              <LabelList content={renderValue} dataKey="plotted" />
            </Bar>
          </BarChart>
        )}
      </ChartSurface>
    </figure>
  )
}
