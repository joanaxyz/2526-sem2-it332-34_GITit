import { useEffect, useState } from 'react'
import { ArrowRight, BookOpen } from 'lucide-react'
import { Link } from 'react-router-dom'

import type { DashboardSummary } from '@/features/dashboard/types'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'

function useCountUp(target: number, duration = 900): number {
  const [value, setValue] = useState(0)
  useEffect(() => {
    if (target === 0) { setValue(0); return }
    const startTime = performance.now()
    const tick = (now: number) => {
      const p = Math.min((now - startTime) / duration, 1)
      setValue(Math.round((1 - Math.pow(1 - p, 3)) * target))
      if (p < 1) requestAnimationFrame(tick)
    }
    const id = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(id)
  }, [target, duration])
  return value
}

function AuroraParticles() {
  const particles = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    left: `${(i * 41 + 5) % 88}%`,
    top: `${(i * 57 + 8) % 82}%`,
    delay: `${((i * 0.35) % 2.8).toFixed(2)}s`,
    duration: `${(3.5 + (i * 0.6) % 2.5).toFixed(2)}s`,
    size: `${2 + (i % 3)}px`,
  }))
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {particles.map((p) => (
        <div
          key={p.id}
          className="absolute rounded-full bg-aurora-cyan"
          style={{
            left: p.left,
            top: p.top,
            width: p.size,
            height: p.size,
            opacity: 0.22,
            animation: `float-particle ${p.duration} ${p.delay} ease-in-out infinite`,
          }}
        />
      ))}
    </div>
  )
}

export function CurrentTrackCard({ summary }: { summary: DashboardSummary }) {
  const attempted = useCountUp(summary.counts.started)
  const completed = useCountUp(summary.counts.completed)
  const streak = useCountUp(summary.streak.current)

  return (
    <Card
      className="relative overflow-hidden p-7"
      style={{
        background: 'linear-gradient(135deg, #0d1117 0%, #111520 55%, #0d1117 100%)',
      }}
    >
      {/* Layered aurora radial glows */}
      <div className="pointer-events-none absolute -left-20 -top-20 h-80 w-80 rounded-full bg-aurora-cyan opacity-[0.04] blur-3xl" />
      <div className="pointer-events-none absolute -left-6 top-16 h-56 w-56 rounded-full bg-aurora-blue opacity-[0.05] blur-2xl" />
      <div className="pointer-events-none absolute left-52 -top-10 h-44 w-44 rounded-full bg-aurora-cyan opacity-[0.03] blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-64 w-64 rounded-full bg-aurora-deep opacity-[0.04] blur-3xl" />

      {/* Animated shimmer overlay */}
      <div
        className="aurora-shimmer pointer-events-none absolute inset-0"
        style={{
          background:
            'linear-gradient(135deg, transparent 0%, rgba(0,245,212,0.03) 35%, rgba(0,180,216,0.06) 50%, rgba(0,245,212,0.03) 65%, transparent 100%)',
          backgroundSize: '300% 300%',
        }}
      />

      <AuroraParticles />

      <div className="relative flex min-h-52 flex-col justify-between gap-4">
        <div>
          <div
            className="mb-4 inline-flex items-center gap-2 rounded-sm px-3 py-1 text-xs font-semibold"
            style={{
              background: 'rgba(0,245,212,0.1)',
              border: '1px solid rgba(0,245,212,0.3)',
              color: '#00F5D4',
            }}
          >
            <BookOpen className="size-3" />
            Student practice track
          </div>
          <h1
            className="max-w-3xl text-4xl font-extrabold leading-tight tracking-tight"
            style={{ textShadow: '0 0 40px rgba(0,245,212,0.28), 0 0 80px rgba(0,180,216,0.14)' }}
          >
            Build Git confidence through foundations, Command Adventure, and Git it Challenge towers.
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
            Start with foundations, clear command forms, then climb Git it Challenge towers from Easy toward Hard.
          </p>
        </div>

        {/* Quick-stats row */}
        <div
          className="border-t pt-3 text-xs font-medium"
          style={{ borderColor: 'rgba(255,255,255,0.06)', color: 'rgba(0,245,212,0.6)' }}
        >
          <span className="font-bold text-[#00F5D4]">{attempted}</span> sessions started
          <span className="mx-2 opacity-40">·</span>
          <span className="font-bold text-[#00F5D4]">{completed}</span> completed
          <span className="mx-2 opacity-40">·</span>
          <span className="font-bold text-[#00F5D4]">{streak}</span>-day streak
        </div>

        <div className="flex flex-wrap gap-2">
          <Button asChild className="btn-pulse">
            <Link to="/tower">
              Open Tower
              <ArrowRight data-icon="inline-end" />
            </Link>
          </Button>
        </div>
      </div>
    </Card>
  )
}
