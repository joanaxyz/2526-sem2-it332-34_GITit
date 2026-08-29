import { useMemo } from 'react'
import { ChevronDown, ChevronUp, Swords } from 'lucide-react'

import type { ChallengeRun } from '@/features/challenges/types'
import { BattleStage } from '@/shared/battle/components/BattleStage'
import { GameplayBattlePanel } from '@/shared/battle/components/GameplayBattlePanel'
import { HealthBar } from '@/shared/battle/components/HealthBar'
import { clientChallengeRoster } from '@/shared/battle/deriveBattleEvents'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { useBattleEncounterSetup } from '@/shared/battle/hooks/useBattleEncounterSetup'
import { labelForMonster } from '@/shared/battle/monsterDescriptors'
import { getStoryWorld } from '@/shared/story-worlds/registry'
import { cn } from '@/shared/utils/cn'

/**
 * Challenge adapter for the shared battle stage. Challenges own opponent roster
 * selection and collapse behavior; rendering, choreography, and sizing stay in
 * the shared battle system.
 */
export function ChallengeBattlePanel({
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
  const storyWorld = getStoryWorld(run.story?.world_slug ?? run.story?.slug)
  const encounterKey = `${run.id}:${storyWorld.slug}`
  const encounterRoster = useMemo(
    () =>
      clientChallengeRoster(
        run.challenge.level_id,
        run.counts.maximum_counted_commands,
        Object.keys(storyWorld.battle.monsters),
        {
          seed: `${storyWorld.slug}:${run.id}:${run.challenge.level_id}`,
          storyWorldSlug: storyWorld.slug,
        },
      ),
    [
      run.challenge.level_id,
      run.counts.maximum_counted_commands,
      run.id,
      storyWorld,
    ],
  )

  useBattleEncounterSetup({
    director,
    storyWorldSlug: storyWorld.slug,
    encounterKey,
    roster: encounterRoster,
    entry: 'run',
    playerHp: run.replay ? null : run.counts.remaining_counted_commands,
    playerMaxHp: run.replay ? null : run.counts.maximum_counted_commands,
  })

  if (!open) {
    return (
      <ChallengeBattleSummary
        run={run}
        director={director}
        onToggle={onToggle}
        className={className}
      />
    )
  }

  return (
    <GameplayBattlePanel variant="challenge" className={className}>
      <BattleStage
        director={director}
        variant="challenge"
        stage={run.battle_stage}
        storyWorldSlug={storyWorld.slug}
        className="h-full w-full"
      />
      <button
        type="button"
        onClick={onToggle}
        className="challenge-battle-collapse"
        aria-expanded
        aria-label="Collapse battle stage"
      >
        <ChevronUp aria-hidden="true" />
      </button>
    </GameplayBattlePanel>
  )
}

function ChallengeBattleSummary({
  run,
  director,
  onToggle,
  className,
}: {
  run: ChallengeRun
  director: BattleDirector
  onToggle: () => void
  className?: string
}) {
  const playerMeter = run.replay
    ? null
    : {
        current: director.playerHp ?? run.counts.remaining_counted_commands,
        max: director.playerMaxHp ?? run.counts.maximum_counted_commands,
      }
  const opponent = director.roster[0]
  const opponentLabel = labelForMonster(opponent)

  return (
    <button
      type="button"
      onClick={onToggle}
      className={cn('challenge-battle-summary', className)}
      aria-expanded={false}
      aria-label="Expand battle stage"
    >
      <Swords aria-hidden="true" />
      {playerMeter ? (
        <span className="challenge-mini-health">
          <span>HP</span>
          <HealthBar
            value={playerMeter.current}
            max={playerMeter.max}
            variant="hp"
            className="challenge-mini-meter"
          />
        </span>
      ) : null}
      {opponent ? (
        <span className="challenge-mini-health">
          <span>{opponentLabel}</span>
          <HealthBar
            value={opponent.hp}
            max={opponent.max_hp}
            variant="enemy"
            className="challenge-mini-meter"
          />
        </span>
      ) : null}
      <ChevronDown aria-hidden="true" />
    </button>
  )
}
