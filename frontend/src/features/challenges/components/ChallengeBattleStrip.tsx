import { useEffect, useRef } from 'react'
import { ChevronDown, ChevronUp, Swords } from 'lucide-react'

import { TowerBattleStage } from '@/shared/battle/components/TowerBattleStage'
import { HealthBar } from '@/shared/battle/components/HealthBar'
import { clientChallengeRoster } from '@/shared/battle/deriveBattleEvents'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { labelForMonster } from '@/shared/battle/monsterDescriptors'
import type { ChallengeRun } from '@/shared/level/types'
import { cn } from '@/shared/utils/cn'

/**
 * Challenge adapter for the battle stage: one boss arena (no travel) at the
 * top of the workspace column. Collapsible to a slim HP-only bar for short
 * viewports - collapsed, the actors unmount entirely (their rAF loops stop),
 * but the director's roster state keeps the numbers honest.
 */
export function ChallengeBattleStrip({
  run,
  director,
  open,
  onToggle,
  className,
}: {
  run: ChallengeRun
  director: BattleDirector
  open: boolean
  onToggle: () => void
  className?: string
}) {
  const stagedRunId = useRef<number | null>(null)

  useEffect(() => {
    if (stagedRunId.current === run.id) return
    stagedRunId.current = run.id
    const roster =
      run.battle?.monsters ??
      clientChallengeRoster(run.challenge.level_id, run.counts.maximum_counted_commands)
    director.setEncounter(roster)
  }, [director, run.battle, run.challenge.level_id, run.counts.maximum_counted_commands, run.id])

  const mana = run.review_mode
    ? null
    : { current: run.counts.remaining_counted_commands, max: run.counts.maximum_counted_commands }
  const boss = director.roster[0]
  const bossLabel = labelForMonster(boss)

  if (!open) {
    return (
      <button
        type="button"
        onClick={onToggle}
        className={cn(
          'flex w-full items-center gap-3 rounded-lg border border-primary/20 bg-background/70 px-3 text-left',
          'hover:border-primary/40',
          className,
        )}
        aria-expanded={false}
        aria-label="Expand battle stage"
      >
        <Swords className="size-3.5 shrink-0 text-primary" />
        {mana ? (
          <span className="flex items-center gap-1.5">
            <span className="text-[9px] font-semibold uppercase tracking-widest text-primary/80">Mana</span>
            <HealthBar value={mana.current} max={mana.max} variant="mana" className="w-16" />
          </span>
        ) : null}
        {boss ? (
          <span className="flex min-w-0 items-center gap-1.5">
            <span className="truncate text-[10px] text-muted-foreground">{bossLabel}</span>
            <HealthBar value={boss.hp} max={boss.max_hp} variant="boss" className="w-16" />
          </span>
        ) : null}
        <ChevronDown className="ml-auto size-3.5 shrink-0 text-muted-foreground" />
      </button>
    )
  }

  return (
    <div className={cn('relative', className)}>
      <TowerBattleStage director={director} variant="challenge" mana={mana} stage={run.battle_stage} className="h-full w-full" />
      <button
        type="button"
        onClick={onToggle}
        className="absolute right-2 top-2 z-30 grid size-6 place-items-center rounded-md border border-border bg-background/70 text-muted-foreground backdrop-blur-sm hover:text-primary"
        aria-expanded
        aria-label="Collapse battle stage"
      >
        <ChevronUp className="size-3.5" />
      </button>
    </div>
  )
}
