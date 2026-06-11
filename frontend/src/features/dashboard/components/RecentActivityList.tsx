import { ListChecks } from 'lucide-react'
import { useEffect, useState } from 'react'

import type { DashboardSummary } from '@/features/dashboard/types'
import { GamePanel } from '@/shared/components/GamePanel'

function useCountUp(target: number, duration = 900): number {
  const [value, setValue] = useState(0)
  useEffect(() => {
    const startTime = performance.now()
    const tick = (now: number) => {
      if (target === 0) {
        setValue(0)
        return
      }
      const p = Math.min((now - startTime) / duration, 1)
      setValue(Math.round((1 - Math.pow(1 - p, 3)) * target))
      if (p < 1) requestAnimationFrame(tick)
    }
    const id = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(id)
  }, [target, duration])
  return value
}

type OutcomeStyle = { color: string; label: string }

const OUTCOMES: { key: 'started' | 'completed' | 'failed'; style: OutcomeStyle }[] = [
  { key: 'started', style: { color: '#00F5D4', label: 'Started' } },
  { key: 'completed', style: { color: '#34D399', label: 'Completed' } },
  { key: 'failed', style: { color: '#FB7185', label: 'Failed' } },
]

function Outcome({ label, value, color }: { label: string; value: number; color: string }) {
  const count = useCountUp(value)
  return (
    <div
      className="stat-tile p-3"
      style={{ ['--tile-accent' as string]: color }}
    >
      <div className="relative z-[1] text-xs text-muted-foreground">{label}</div>
      <div
        className="relative z-[1] mt-1 text-2xl font-extrabold leading-none"
        style={{ color, textShadow: `0 0 18px ${color}55` }}
      >
        {count}
      </div>
    </div>
  )
}

export function RecentActivityList({ summary }: { summary: DashboardSummary }) {
  return (
    <GamePanel className="p-5">
      <div className="relative z-[1] mb-4 flex items-center gap-2">
        <span className="game-chip size-8">
          <ListChecks className="size-4 text-aurora-cyan" />
        </span>
        <div>
          <h3 className="text-lg font-bold leading-none tracking-tight">Your quests</h3>
          <p className="mt-1 text-xs text-muted-foreground">How your quest attempts have gone so far.</p>
        </div>
      </div>
      <div className="relative z-[1] grid grid-cols-3 gap-3">
        {OUTCOMES.map(({ key, style }) => (
          <Outcome key={key} label={style.label} value={summary.counts[key]} color={style.color} />
        ))}
      </div>
    </GamePanel>
  )
}
