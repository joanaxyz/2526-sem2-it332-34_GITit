import { useEffect, useState } from 'react'

import type { SkillAxis } from '@/features/stats/types'
import { Card, CardContent } from '@/shared/components/Card'

const SIZE = 320
const CENTER = SIZE / 2
const RADIUS = 110
const RINGS = [0.25, 0.5, 0.75, 1]
const CYAN = '#00F5D4'
const BLUE = '#00B4D8'

/** Vertex position for an axis at a given radius fraction (0..1). Axis 0 points up. */
function vertex(index: number, total: number, frac: number): [number, number] {
  const angle = (-90 + (index * 360) / total) * (Math.PI / 180)
  return [CENTER + RADIUS * frac * Math.cos(angle), CENTER + RADIUS * frac * Math.sin(angle)]
}

function polygon(total: number, frac: number): string {
  return Array.from({ length: total }, (_, i) => vertex(i, total, frac).join(',')).join(' ')
}

export function SkillProfileRadar({ axes }: { axes: SkillAxis[] }) {
  const [mounted, setMounted] = useState(false)
  useEffect(() => {
    const id = requestAnimationFrame(() => setMounted(true))
    return () => cancelAnimationFrame(id)
  }, [])

  const total = axes.length
  const hasAny = axes.some((a) => a.value !== null)
  const dataPoints = axes
    .map((axis, i) => vertex(i, total, (axis.value ?? 0) / 100).join(','))
    .join(' ')

  return (
    <Card className="overflow-hidden shadow-none">
      <CardContent className="p-5">
        <div className="mb-1 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold tracking-tight">Your skill profile</h2>
            <p className="text-xs text-muted-foreground">
              Six qualities that grow as you play. The wider the shape, the stronger you are.
            </p>
          </div>
        </div>

        <div className="flex justify-center">
          <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`} className="max-w-full">
            <defs>
              <radialGradient id="radar-fill" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor={CYAN} stopOpacity="0.45" />
                <stop offset="100%" stopColor={BLUE} stopOpacity="0.12" />
              </radialGradient>
              <filter id="radar-glow" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            {/* Grid rings */}
            {RINGS.map((frac) => (
              <polygon
                key={frac}
                points={polygon(total, frac)}
                fill="none"
                stroke="rgba(255,255,255,0.08)"
                strokeWidth={1}
              />
            ))}

            {/* Spokes + axis labels */}
            {axes.map((axis, i) => {
              const [sx, sy] = vertex(i, total, 1)
              const [lx, ly] = vertex(i, total, 1.16)
              const anchor = lx > CENTER + 4 ? 'start' : lx < CENTER - 4 ? 'end' : 'middle'
              return (
                <g key={axis.key}>
                  <line x1={CENTER} y1={CENTER} x2={sx} y2={sy} stroke="rgba(255,255,255,0.07)" strokeWidth={1} />
                  <text
                    x={lx}
                    y={ly}
                    textAnchor={anchor}
                    dominantBaseline="middle"
                    className="fill-aurora-blue"
                    style={{ fontSize: 11, fontWeight: 600 }}
                  >
                    {axis.label}
                  </text>
                  <text
                    x={lx}
                    y={ly + 13}
                    textAnchor={anchor}
                    dominantBaseline="middle"
                    style={{ fontSize: 10, fill: axis.value === null ? 'rgba(255,255,255,0.3)' : CYAN }}
                  >
                    {axis.value === null ? '—' : Math.round(axis.value)}
                  </text>
                </g>
              )
            })}

            {/* Data polygon — grows out of the centre on mount */}
            {hasAny && (
              <g
                style={{
                  transformOrigin: `${CENTER}px ${CENTER}px`,
                  transform: mounted ? 'scale(1)' : 'scale(0.1)',
                  opacity: mounted ? 1 : 0,
                  transition: 'transform 850ms cubic-bezier(0.16,1,0.3,1), opacity 600ms ease',
                }}
              >
                <polygon points={dataPoints} fill="url(#radar-fill)" stroke={CYAN} strokeWidth={2} filter="url(#radar-glow)" />
                {axes.map((axis, i) => {
                  if (axis.value === null) return null
                  const [px, py] = vertex(i, total, axis.value / 100)
                  return <circle key={axis.key} cx={px} cy={py} r={3} fill={CYAN} style={{ filter: `drop-shadow(0 0 4px ${CYAN})` }} />
                })}
              </g>
            )}
          </svg>
        </div>

        {!hasAny && (
          <p className="mt-2 text-center text-sm text-muted-foreground/70">
            Play a few quests and your profile will start to take shape.
          </p>
        )}

        {/* Plain-language legend */}
        <ul className="mt-3 grid grid-cols-2 gap-x-4 gap-y-1.5 max-sm:grid-cols-1">
          {axes.map((axis) => (
            <li key={axis.key} className="flex items-baseline gap-1.5 text-[0.7rem] leading-snug text-muted-foreground">
              <span className="font-semibold text-foreground/80">{axis.label}:</span>
              <span>{axis.hint}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}
