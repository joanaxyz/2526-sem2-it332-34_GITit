import { useEffect, useMemo, useState } from 'react'

import { AdventureMasteryOverlay } from '@/features/adventures/components/AdventureMasteryOverlay'
import { AdventureProgressBar } from '@/features/adventures/components/AdventureProgressBar'
import type { AdventureAttempt, AdventureRun } from '@/features/adventures/types'
import { BattleStage } from '@/shared/battle/components/BattleStage'
import { GameplayBattlePanel } from '@/shared/battle/components/GameplayBattlePanel'
import { clientAdventureRoster } from '@/shared/battle/deriveBattleEvents'
import { getStoryWorld } from '@/shared/story-worlds/registry'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { useBattleEncounterSetup } from '@/shared/battle/hooks/useBattleEncounterSetup'

const WAVE_CUE_MS = 1550

/**
 * Adventure adapter for the battle stage: every playable wave gets its own
 * encounter staging beat. Advancing to a later wave plays the travel beat (Blue
 * flies back while the world scrolls), then the next wave receives its intro.
 * The mastery progress bar lives in the ground slab, below the neon ground line.
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
  const [expiredCueId, setExpiredCueId] = useState<number | null>(null)

  const displayWave = Math.max(1, run.current_wave || attempt.wave + 1)
  const displayTotal = Math.max(displayWave, run.total_waves || displayWave)
  const storyWorld = getStoryWorld(run.story?.world_slug ?? run.story?.slug)

  const encounterKey = `${attempt.id}:${attempt.wave}:${run.current_wave}`
  const maxHp = attempt.command_budget.max_counted_commands
  const encounterRoster = useMemo(
    () =>
      clientAdventureRoster(
        attempt.wave,
        run.total_waves,
        Object.keys(storyWorld.battle.monsters),
        {
          // Wave-independent base seed: clientAdventureRoster rotates by the wave
          // index (attempt.wave) so consecutive waves always show a new monster.
          seed: `${storyWorld.slug}:${run.id}:${attempt.id}`,
          storyWorldSlug: storyWorld.slug,
          maxHp,
        },
      ),
    [
      attempt.id,
      attempt.wave,
      maxHp,
      run.id,
      run.total_waves,
      storyWorld,
    ],
  )

  const hp = Math.max(0, maxHp - attempt.counts.counted_command_count)

  useBattleEncounterSetup({
    director,
    storyWorldSlug: storyWorld.slug,
    encounterKey,
    roster: encounterRoster,
    entry: 'run',
    travelOnEncounterChange: true,
    transitionCue: displayTotal > 1 ? { wave: displayWave, total: displayTotal } : null,
    playerHp: hp,
    playerMaxHp: maxHp,
  })

  useEffect(() => {
    const cue = director.transitionCue
    if (!cue) return undefined

    const timeout = window.setTimeout(() => {
      setExpiredCueId((current) => (current === cue.id ? current : cue.id))
    }, WAVE_CUE_MS)

    return () => window.clearTimeout(timeout)
  }, [director.transitionCue])

  const activeWaveCue =
    director.transitionCue && director.transitionCue.id !== expiredCueId ? director.transitionCue : null

  return (
    <GameplayBattlePanel variant="adventure" className={className}>
      <BattleStage
        director={director}
        variant="adventure"
        groundFooter={
          <AdventureProgressBar
            run={run}
            variant="battle"
            currentWave={displayWave}
            totalWaves={displayTotal}
          />
        }
        centerOverlay={
          activeWaveCue ? (
            <WaveTransitionCue
              key={`transition-${activeWaveCue.id}`}
              wave={activeWaveCue.wave}
              total={activeWaveCue.total}
            />
          ) : null
        }
        topRight={<AdventureMasteryOverlay run={run} />}
        stage={run.battle_stage}
        storyWorldSlug={storyWorld.slug}
        className="h-full w-full"
      />
    </GameplayBattlePanel>
  )
}

function WaveTransitionCue({ wave, total }: { wave: number; total: number }) {
  return (
    <div className="battle-wave-cue" aria-live="polite" aria-atomic="true">
      <div className="battle-wave-cue__label">Wave transition</div>
      <div className="battle-wave-cue__title">Wave {wave}</div>
      <div className="battle-wave-cue__count">
        {wave}
        <span>/</span>
        {total}
      </div>
    </div>
  )
}
