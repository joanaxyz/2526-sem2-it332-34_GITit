import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

import { BattleQueue } from '@/shared/battle/battleQueue'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'
import { DEFAULT_STORY_WORLD_SLUG, getStoryWorld } from '@/shared/story-worlds/registry'

import { useBattleActorRefs } from './useBattleActorRefs'
import { useBattleEncounterChoreography } from './useBattleEncounterChoreography'
import { useBattleRosterState } from './useBattleRosterState'
import { useBattleResolveQueue } from './useBattleResolveQueue'
import type { BattleDirector, BattleTransitionCue, BattleTransitionCueConfig } from './battleDirectorTypes'
import type { BattleMonster } from '@/shared/battle/types'

export { missedSpellFloorTarget } from './battleMotion'
export type { BattleDirector, BattleTransitionCue, BattleTransitionCueConfig, EncounterOptions } from './battleDirectorTypes'

/**
 * Translates command-lifecycle calls into sequential stage choreography. In the
 * turn-based duel loop: a counted command attacks the monsters; every unsolved
 * counted turn lets the monster strike Blue back, draining real player HP.
 * Clearing a level scrolls the stage horizontally to the next encounter.
 *
 * All per-frame work happens through imperative handles; React state changes are
 * limited to roster/HP snapshots (<2 per command).
 */
export function useBattleDirector(): BattleDirector {
  const {
    roster,
    rosterRef,
    rosterEpoch,
    playerHp,
    playerMaxHp,
    bumpRosterEpoch,
    currentMonsters,
    setMonster,
    setPlayerHp,
    setPlayerMaxHp,
    setRoster,
  } = useBattleRosterState()
  const [defeated, setDefeated] = useState(false)
  const [animating, setAnimating] = useState(false)
  const [transitionCue, setTransitionCue] = useState<BattleTransitionCue | null>(null)
  const [stagedMonsterIds, setStagedMonsterIds] = useState<ReadonlySet<number>>(() => new Set())
  const [activeMonsterId, setActiveMonsterId] = useState<number | null>(null)
  // The selected story world supplies monster skins/effects (by species). Held
  // in a ref so imperative choreography callbacks read it without re-binding.
  const { companionSlug } = usePlayerLoadout()
  const [storyWorldSlug, setStoryWorldSlugState] = useState(DEFAULT_STORY_WORLD_SLUG)
  const storyWorld = useMemo(() => getStoryWorld(storyWorldSlug), [storyWorldSlug])
  const storyWorldRef = useRef(storyWorld)
  const companionSlugRef = useRef(companionSlug)
  const {
    playerRef,
    backdropRef,
    effectLayerRef,
    effectBackLayerRef,
    monsterHandles,
    bindPlayer,
    bindBackdrop,
    bindCamera,
    bindEffectLayer,
    bindBackEffectLayer,
    bindMonster,
    anchor,
    monsterImpactAnchor,
    monsterFeetAnchor,
    monsterSizeScale,
    missedSpellGroundAnchor,
    measureWideFrame,
    measureClosureRun,
    centerScrollPx,
    panCamera,
    resetCamera,
  } = useBattleActorRefs(rosterRef, storyWorldRef)
  const queue = useMemo(() => new BattleQueue(), [])
  const attackPendingRef = useRef(false)
  const defeatedRef = useRef(false)
  const transitionCueIdRef = useRef(0)
  const disposeTimerRef = useRef<number | null>(null)

  useEffect(() => {
    // Defer disposal so React StrictMode's synchronous unmount+remount does not
    // wipe intro steps a consumer just enqueued. Consumers stage an encounter
    // once, guarded by an encounter signature (so the intro never doubles on
    // refresh) — they will NOT re-enqueue on the StrictMode remount. If dispose()
    // ran synchronously in the cleanup between the two setups it would clear those
    // steps and the guarded remount would leave the queue empty, so the intro /
    // wave cue never plays. A real unmount has no matching remount, so the
    // deferred dispose fires; the StrictMode remount cancels it first.
    if (disposeTimerRef.current !== null) {
      window.clearTimeout(disposeTimerRef.current)
      disposeTimerRef.current = null
    }
    queue.revive()
    return () => {
      disposeTimerRef.current = window.setTimeout(() => {
        disposeTimerRef.current = null
        queue.dispose()
      }, 0)
    }
  }, [queue])

  useEffect(() => queue.subscribe(setAnimating), [queue])

  useEffect(() => {
    storyWorldRef.current = storyWorld
  }, [storyWorld])

  useEffect(() => {
    companionSlugRef.current = companionSlug
  }, [companionSlug])

  const emitTransitionCue = useCallback((cue: BattleTransitionCueConfig) => {
    transitionCueIdRef.current += 1
    setTransitionCue({ ...cue, id: transitionCueIdRef.current })
  }, [])

  const setEntranceHidden = useCallback((monsters: BattleMonster[], hidden: boolean) => {
    setStagedMonsterIds(hidden ? new Set(monsters.map((monster) => monster.id)) : new Set())
  }, [])

  const { playApproach, playCenterBeat, setEncounter } = useBattleEncounterChoreography({
    queue,
    rosterRef,
    playerRef,
    backdropRef,
    monsterHandles,
    measureWideFrame,
    measureClosureRun,
    centerScrollPx,
    panCamera,
    resetCamera,
    emitTransitionCue,
    setDefeated,
    setActiveMonsterId,
    setPlayerHp,
    setPlayerMaxHp,
    setEntranceHidden,
    bumpRosterEpoch,
    setRoster,
    defeatedRef,
  })

  const { onResolve } = useBattleResolveQueue({
    queue,
    rosterRef,
    playerRef,
    backdropRef,
    effectLayerRef,
    effectBackLayerRef,
    monsterHandles,
    storyWorldRef,
    companionSlugRef,
    attackPendingRef,
    defeatedRef,
    anchor,
    monsterImpactAnchor,
    monsterFeetAnchor,
    monsterSizeScale,
    missedSpellGroundAnchor,
    playApproach,
    playCenterBeat,
    emitTransitionCue,
    setDefeated,
    setActiveMonsterId,
    setEntranceHidden,
    bumpRosterEpoch,
    setMonster,
    setPlayerHp,
    setPlayerMaxHp,
    setRoster,
  })

  const onAttackStart = useCallback(() => {
    if (defeatedRef.current) return
    attackPendingRef.current = true
    if (queue.busy) queue.fastForward()
    playerRef.current?.beginAttack()
  }, [playerRef, queue])

  const onError = useCallback(() => {
    attackPendingRef.current = false
    playerRef.current?.cancelAttack()
  }, [playerRef])

  const setStoryWorldSlug = useCallback((slug: string | null | undefined) => {
    setStoryWorldSlugState(slug || DEFAULT_STORY_WORLD_SLUG)
  }, [])

  return {
    roster,
    playerHp,
    playerMaxHp,
    defeated,
    animating,
    transitionCue,
    stagedMonsterIds,
    activeMonsterId,
    rosterEpoch,
    bindPlayer,
    bindBackdrop,
    bindCamera,
    bindEffectLayer,
    bindBackEffectLayer,
    bindMonster,
    currentMonsters,
    onAttackStart,
    onResolve,
    onError,
    setStoryWorldSlug,
    setEncounter,
  }
}
