import { useEffect, useRef, useState, type ReactNode } from 'react'

export type ChartSize = { width: number; height: number }

/**
 * Pixel dimensions for a chart that has to survive being measured badly.
 *
 * Recharts needs a concrete width. Its own `ResponsiveContainer` asks a
 * ResizeObserver, which reports 0 in jsdom and in headless renders, and a
 * zero-width chart ships as an empty box. This measures the element the same
 * way but keeps a real fallback width until a measurement arrives, so the chart
 * always has geometry to draw with.
 */
export function ChartSurface({
  height,
  fallbackWidth = 620,
  className,
  label,
  children,
}: {
  height: number
  fallbackWidth?: number
  className?: string
  /** Describes the plot for screen readers; the marks themselves are decorative. */
  label: string
  children: (size: ChartSize) => ReactNode
}) {
  const hostRef = useRef<HTMLDivElement>(null)
  const [width, setWidth] = useState(0)

  useEffect(() => {
    const host = hostRef.current
    if (!host || typeof ResizeObserver === 'undefined') return

    const observer = new ResizeObserver((entries) => {
      const measured = Math.round(entries[0]?.contentRect.width ?? 0)
      if (measured > 0) setWidth(measured)
    })
    observer.observe(host)
    return () => observer.disconnect()
  }, [])

  return (
    <div className={className ? `ref-chart ${className}` : 'ref-chart'} ref={hostRef} role="img" aria-label={label}>
      {children({ width: width > 0 ? width : fallbackWidth, height })}
    </div>
  )
}
