import { useEffect, useRef } from 'react'

import type { BattleDirector, BattleTransitionCueConfig, EncounterOptions } from '@/shared/battle/hooks/useBattleDirector'
import type { BattleMonster } from '@/shared/battle/types'

export type BattleEncounterSetup = {
  director: BattleDirector
  storyWorldSlug: string
  encounterKey: string
  roster: BattleMonster[]
  entry?: EncounterOptions['entry']
  travelOnEncounterChange?: boolean
  transitionCue?: BattleTransitionCueConfig | null
  playerHp?: number | null
  playerMaxHp?: number | null
}

/**
 * Stages one visual encounter per encounter/roster identity.
 *
 * Adventure and challenge adapters still own their distinct roster rules and
 * feature UI. This hook owns the shared director lifecycle: synchronizing the
 * StoryWorld, guarding against StrictMode duplicate staging, and replacing the
 * encounter only when its stable identity changes.
 */
export function useBattleEncounterSetup({
  director,
  storyWorldSlug,
  encounterKey,
  roster,
  entry = 'run',
  travelOnEncounterChange = false,
  transitionCue = null,
  playerHp = null,
  playerMaxHp = null,
}: BattleEncounterSetup) {
  const lastEncounterKeyRef = useRef<string | null>(null)
  const { setEncounter, setStoryWorldSlug } = director
  const lastStageSignatureRef = useRef<string | null>(null)

  const rosterIdentity = roster.map((monster) => monster.id).join(',')
  const stageSignature = roster.length > 0 ? `${encounterKey}|${rosterIdentity}` : ''
  const transitionWave = transitionCue?.wave ?? null
  const transitionTotal = transitionCue?.total ?? null

  useEffect(() => {
    setStoryWorldSlug(storyWorldSlug)

    if (!stageSignature || lastStageSignatureRef.current === stageSignature) return

    const encounterChanged =
      lastEncounterKeyRef.current !== null && lastEncounterKeyRef.current !== encounterKey

    lastStageSignatureRef.current = stageSignature
    lastEncounterKeyRef.current = encounterKey

    setEncounter(roster, {
      entry,
      travel: travelOnEncounterChange && encounterChanged,
      transitionCue:
        transitionWave !== null && transitionTotal !== null
          ? { wave: transitionWave, total: transitionTotal }
          : null,
      playerHp,
      playerMaxHp,
    })
  }, [
    encounterKey,
    entry,
    playerHp,
    playerMaxHp,
    roster,
    stageSignature,
    setEncounter,
    setStoryWorldSlug,
    storyWorldSlug,
    transitionTotal,
    transitionWave,
    travelOnEncounterChange,
  ])
}

