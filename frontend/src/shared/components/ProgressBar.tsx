import { useEffect, useState } from 'react'
import * as ProgressPrimitive from '@radix-ui/react-progress'

import { cn } from '@/shared/utils/cn'

export function ProgressBar({
  value,
  className,
  glow,
  fillAnimate,
  fillFrom,
  fillTo,
  segments,
}: {
  value: number
  className?: string
  glow?: boolean
  fillAnimate?: boolean
  /** Override gradient start color (hex). Requires fillTo. */
  fillFrom?: string
  /** Override gradient end color (hex). Requires fillFrom. */
  fillTo?: string
  /** Number of checkpoints along the track. Renders landmark marks at each boundary. */
  segments?: number
}) {
  const normalized = Math.max(0, Math.min(100, value))
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    const id = requestAnimationFrame(() => setMounted(true))
    return () => cancelAnimationFrame(id)
  }, [])

  const displayed = fillAnimate ? (mounted ? normalized : 0) : normalized
  const showGlowTip = glow && displayed > 0
  const hasCustomColor = fillFrom && fillTo

  const customFillStyle = hasCustomColor
    ? {
        background: `linear-gradient(to right, ${fillFrom}, ${fillTo})`,
        ...(showGlowTip
          ? { boxShadow: `0 0 8px ${fillFrom}80, 0 0 16px ${fillFrom}40, 0 0 2px ${fillFrom}99` }
          : {}),
      }
    : undefined

  const landmarks =
    segments && segments > 1
      ? Array.from({ length: segments - 1 }, (_, index) => ((index + 1) / segments) * 100)
      : []

  const root = (
    <ProgressPrimitive.Root
      className={cn('h-2 overflow-hidden rounded-full bg-secondary', className)}
      value={normalized}
    >
      <ProgressPrimitive.Indicator
        className={cn(
          'h-full rounded-full',
          !hasCustomColor && (showGlowTip ? 'progress-glow-tip' : 'bg-gradient-to-r from-primary to-accent'),
        )}
        style={{
          transform: `translateX(-${100 - displayed}%)`,
          transition: fillAnimate
            ? 'transform 1.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.5s ease'
            : 'transform 0.15s ease, box-shadow 0.2s ease',
          ...customFillStyle,
        }}
      />
    </ProgressPrimitive.Root>
  )

  if (!landmarks.length) return root

  return (
    <div className="relative">
      {root}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0">
        {landmarks.map((position) => (
          <span
            key={position}
            className="progress-landmark"
            data-reached={displayed >= position - 0.5}
            style={{ left: `${position}%` }}
          />
        ))}
      </div>
    </div>
  )
}
