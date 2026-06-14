import { useEffect, useRef } from 'react'

import { AdventureProgressBar } from '@/features/command-adventures/components/AdventureProgressBar'
import type { AdventureAttempt, AdventureRun } from '@/features/command-adventures/types'
import { TowerBattleStage } from '@/shared/battle/components/TowerBattleStage'
import { clientAdventureRoster } from '@/shared/battle/deriveBattleEvents'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'

/**
 * Adventure adapter for the battle stage: each level is one encounter, keyed
 * by attempt id. Advancing to a later level plays the travel beat (Blue runs
 * right while the world scrolls). The mastery progress bar lives in the ground
 * slab, below the neon ground line.
 */
export function AdventureBattlePanel({
  run,
  attempt,
  director,
  className,
}: {
  run: AdventureRun
  attempt: AdventureAttempt
  director: BattleDirector
  className?: string
}) {
  const lastEncounter = useRef<{ attemptId: number; levelIndex: number } | null>(null)

  useEffect(() => {
    const prev = lastEncounter.current
    if (prev?.attemptId === attempt.id) return
    lastEncounter.current = { attemptId: attempt.id, levelIndex: run.current_level_index }

    const roster =
      attempt.battle?.monsters ?? clientAdventureRoster(run.current_level_index, run.total_levels)
    director.setEncounter(roster, {
      // Travel only when actually advancing through the tower of levels; a
      // retry of the same level (failed attempt) restages in place.
      travel: prev !== null && run.current_level_index > prev.levelIndex,
    })
  }, [attempt.id, attempt.battle, director, run.current_level_index, run.total_levels])

  const maxMana = attempt.command_budget.max_counted_commands
  const mana = Math.max(0, maxMana - attempt.counts.counted_command_count)

  return (
    <TowerBattleStage
      director={director}
      variant="adventure"
      mana={{ current: mana, max: maxMana }}
      groundFooter={<AdventureProgressBar run={run} variant="battle" />}
      stage={run.battle_stage}
      className={className}
    />
  )
}
