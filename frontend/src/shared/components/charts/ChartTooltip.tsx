import type { ReactNode } from 'react'

export type ChartTooltipRow = {
  key: string
  label: string
  value: string
  /** Paints the swatch beside the row; identity never rides the text colour. */
  tone?: 'accent' | 'progress' | 'muted'
}

/**
 * The one tooltip body every chart in the app uses: a title line, then
 * swatch + label + value rows. Values stay in the mono numeral voice, labels in
 * the interface sans, and the series colour lives in the swatch so no text has
 * to wear a light accent hue.
 */
export function ChartTooltipCard({
  title,
  caption,
  rows,
  children,
}: {
  title: string
  caption?: string
  rows?: ChartTooltipRow[]
  children?: ReactNode
}) {
  return (
    <div className="ref-chart-tip">
      <p className="ref-chart-tip-title">{title}</p>
      {caption ? <p className="ref-chart-tip-caption">{caption}</p> : null}
      {rows?.length ? (
        <dl>
          {rows.map((row) => (
            <div key={row.key} data-tone={row.tone ?? 'accent'}>
              <dt>
                <i aria-hidden="true" />
                {row.label}
              </dt>
              <dd>{row.value}</dd>
            </div>
          ))}
        </dl>
      ) : null}
      {children}
    </div>
  )
}
