import { useEffect, useState } from 'react'

/**
 * Compact neon ring gauge for rate metrics (0–100). Animates from empty on
 * mount; renders a dimmed dashed track with "—" semantics when value is null.
 * Shared by the dashboard KPI strip and the stats headline band.
 */
export function RingGauge({
  value,
  size = 46,
  strokeWidth = 4.5,
  color = '#00F5D4',
  showValue = true,
  label,
}: {
  value: number | null
  size?: number
  strokeWidth?: number
  color?: string
  /** Render the % in the ring's center. */
  showValue?: boolean
  /** Accessible label, e.g. "Command accuracy". */
  label?: string
}) {
  const [mounted, setMounted] = useState(false)
  useEffect(() => {
    const id = requestAnimationFrame(() => setMounted(true))
    return () => cancelAnimationFrame(id)
  }, [])

  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const clamped = value === null ? 0 : Math.max(0, Math.min(100, value))
  const shown = mounted ? clamped : 0
  const dashOffset = circumference * (1 - shown / 100)
  const hasData = value !== null

  return (
    <div
      className="relative grid shrink-0 place-items-center"
      style={{ width: size, height: size }}
      role="img"
      aria-label={label ? `${label}: ${hasData ? `${Math.round(clamped)}%` : 'no data yet'}` : undefined}
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden="true">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={hasData ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.06)'}
          strokeWidth={strokeWidth}
          strokeDasharray={hasData ? undefined : '2.5 4'}
        />
        {hasData && (
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            transform={`rotate(-90 ${size / 2} ${size / 2})`}
            style={{
              transition: 'stroke-dashoffset 1.1s cubic-bezier(0.16, 1, 0.3, 1)',
              filter: `drop-shadow(0 0 4px ${color}66)`,
            }}
          />
        )}
      </svg>
      {showValue && (
        <span
          className="absolute font-mono font-bold leading-none"
          style={{
            fontSize: size * 0.26,
            color: hasData ? color : 'rgba(255,255,255,0.35)',
          }}
          aria-hidden="true"
        >
          {hasData ? Math.round(clamped) : '—'}
        </span>
      )}
    </div>
  )
}
