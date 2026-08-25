import { useCallback, useRef } from 'react'
import type { MutableRefObject } from 'react'

import type { BattleBackdropHandle } from '@/shared/battle/components/BattleBackdrop'
import type { MonsterActorHandle } from '@/shared/battle/components/MonsterActor'
import type { PlayerActorHandle } from '@/shared/battle/components/PlayerActor'
import { definitionForMonster } from '@/shared/battle/monsterDescriptors'
import type { BattleMonster } from '@/shared/battle/types'
import { monsterSkin } from '@/shared/story-worlds/registry'
import type { StoryWorldDef } from '@/shared/story-worlds/types'

import {
  boundedAnimation,
  CENTER_SCROLL_FRAC,
  clamp01,
  missedSpellFloorTarget,
  MONSTER_PEEK_VISIBLE,
  parseBattleRailY,
  prefersReducedMotion,
  readTranslateX,
} from './battleMotion'

export function useBattleActorRefs(
  rosterRef: MutableRefObject<BattleMonster[]>,
  storyWorldRef: MutableRefObject<StoryWorldDef>,
) {
  const playerRef = useRef<PlayerActorHandle | null>(null)
  const backdropRef = useRef<BattleBackdropHandle | null>(null)
  const cameraRef = useRef<HTMLDivElement | null>(null)
  const cameraOffsetRef = useRef(0)
  const effectLayerRef = useRef<HTMLDivElement | null>(null)
  const effectBackLayerRef = useRef<HTMLDivElement | null>(null)
  const monsterHandles = useRef(new Map<number, MonsterActorHandle>())

  const bindPlayer = useCallback((handle: PlayerActorHandle | null) => {
    playerRef.current = handle
  }, [])
  const bindBackdrop = useCallback((handle: BattleBackdropHandle | null) => {
    backdropRef.current = handle
  }, [])
  const bindCamera = useCallback((node: HTMLDivElement | null) => {
    cameraRef.current = node
  }, [])
  const bindEffectLayer = useCallback((node: HTMLDivElement | null) => {
    effectLayerRef.current = node
  }, [])
  const bindBackEffectLayer = useCallback((node: HTMLDivElement | null) => {
    effectBackLayerRef.current = node
  }, [])
  const bindMonster = useCallback((id: number, handle: MonsterActorHandle | null) => {
    if (handle) monsterHandles.current.set(id, handle)
    else monsterHandles.current.delete(id)
  }, [])

  // Real camera pan: translate the actor layer to follow Blue as he runs, so the
  // panel visibly sweeps (the parallax backdrop scrolls independently for depth).
  // Cumulative offset; resetCamera eases it back to the centred duel framing.
  const panCamera = useCallback((px: number, ms: number): Promise<void> => {
    const node = cameraRef.current
    if (!node || prefersReducedMotion()) return Promise.resolve()
    const from = cameraOffsetRef.current
    const to = from + px
    cameraOffsetRef.current = to
    const animation = node.animate(
      [{ transform: `translateX(${from}px)` }, { transform: `translateX(${to}px)` }],
      { duration: ms, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'forwards' },
    )
    return boundedAnimation(animation.finished.then(() => undefined, () => undefined), ms + 120).then(() => {
      node.style.transform = `translateX(${to}px)`
      animation.cancel()
    })
  }, [])

  const resetCamera = useCallback((ms: number): Promise<void> => {
    const node = cameraRef.current
    const from = cameraOffsetRef.current
    cameraOffsetRef.current = 0
    if (!node || from === 0 || prefersReducedMotion()) {
      if (node) node.style.transform = 'translateX(0px)'
      return Promise.resolve()
    }
    const animation = node.animate(
      [{ transform: `translateX(${from}px)` }, { transform: 'translateX(0px)' }],
      { duration: ms, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'forwards' },
    )
    return boundedAnimation(animation.finished.then(() => undefined, () => undefined), ms + 120).then(() => {
      node.style.transform = 'translateX(0px)'
      animation.cancel()
    })
  }, [])

  /** Layer-local point of an element, for effect launch/impact points. */
  const anchor = useCallback((el: Element | null, dx = 0, dy = 0, xFrac = 0.5, yFrac = 0.5) => {
    const layer = effectLayerRef.current
    if (!layer || !el) return { x: 0, y: 0 }
    const layerBox = layer.getBoundingClientRect()
    const box = el.getBoundingClientRect()
    return {
      x: box.left + box.width * clamp01(xFrac) - layerBox.left + dx,
      y: box.top + box.height * clamp01(yFrac) - layerBox.top + dy,
    }
  }, [])

  /** Layer-local point inside already-measured viewport bounds. */
  const boundsAnchor = useCallback(
    (
      box: { left: number; top: number; width: number; height: number } | null,
      dx = 0,
      dy = 0,
      xFrac = 0.5,
      yFrac = 0.5,
    ) => {
      const layer = effectLayerRef.current
      if (!layer || !box) return { x: 0, y: 0 }
      const layerBox = layer.getBoundingClientRect()
      return {
        x: box.left + box.width * clamp01(xFrac) - layerBox.left + dx,
        y: box.top + box.height * clamp01(yFrac) - layerBox.top + dy,
      }
    },
    [],
  )

  const monsterBodyFraction = useCallback((monster: BattleMonster | undefined) => {
    if (!monster) return 0.62
    const def = definitionForMonster(monster, monsterSkin(storyWorldRef.current, monster.species))
    return Math.min(0.88, Math.max(0.22, def.metrics.hpBarFraction))
  }, [storyWorldRef])

  const monsterImpactAnchor = useCallback(
    (monsterId: number, side: 'left' | 'center' | 'right' = 'center') => {
      const monster = rosterRef.current.find((m) => m.id === monsterId)
      const handle = monsterHandles.current.get(monsterId)
      const bodyBounds = handle?.bodyBounds() ?? null
      const bodyX = side === 'left' ? 0.12 : side === 'right' ? 0.88 : 0.5
      if (bodyBounds) return boundsAnchor(bodyBounds, 0, 0, bodyX, 0.5)

      const targetEl = handle?.element() ?? null
      const body = monsterBodyFraction(monster)
      const xFrac = side === 'left' ? 0.5 - body / 2 : side === 'right' ? 0.5 + body / 2 : 0.5
      return anchor(targetEl, 0, 0, xFrac, 0.62)
    },
    [anchor, boundsAnchor, monsterBodyFraction, rosterRef],
  )

  // Ground line under a monster - where feet-anchored and ground-travel spells
  // plant their base so they sit on the floor rather than the monster's body.
  const monsterFeetAnchor = useCallback(
    (monsterId: number) => {
      const handle = monsterHandles.current.get(monsterId)
      const bodyBounds = handle?.bodyBounds() ?? null
      if (bodyBounds) return boundsAnchor(bodyBounds, 0, -2, 0.5, 1)
      const targetEl = handle?.element() ?? null
      return anchor(targetEl, 0, -2, 0.5, 0.95)
    },
    [anchor, boundsAnchor],
  )

  // Scale spell effects to the monster's rendered size, with a neutral baseline
  // and clamps that keep effects readable across differently padded artwork.
  const monsterSizeScale = useCallback((monsterId: number) => {
    const handle = monsterHandles.current.get(monsterId)
    const visibleHeight = handle?.bodyBounds()?.height
    if (visibleHeight) return Math.min(2.2, Math.max(0.7, visibleHeight / 160))
    const el = handle?.element() ?? null
    if (!el) return 1
    const height = el.getBoundingClientRect().height
    if (!height) return 1
    return Math.min(2.2, Math.max(0.7, height / 160))
  }, [])

  const battleStageEl = useCallback(
    () => effectLayerRef.current?.closest('[data-testid="battle-stage"]') as HTMLElement | null,
    [],
  )

  const missedSpellGroundAnchor = useCallback((playerEl: Element | null, enemyEl: Element | null) => {
    const layer = effectLayerRef.current
    if (!layer || !playerEl || !enemyEl) return { x: 0, y: 0 }
    const layerBox = layer.getBoundingClientRect()
    return missedSpellFloorTarget({
      layerBox,
      playerBox: playerEl.getBoundingClientRect(),
      enemyBox: enemyEl.getBoundingClientRect(),
      floorY: parseBattleRailY(battleStageEl(), layerBox),
    })
  }, [battleStageEl])

  /** Wide frame: foe fully off-screen right, then peeks from the rim. */
  const measureWideFrame = useCallback(() => {
    const stage = battleStageEl()
    const lead = rosterRef.current[0]
    const monsterEl = lead ? monsterHandles.current.get(lead.id)?.element() : null
    if (!stage || !monsterEl) {
      return { monsterEntryFromPx: 420, monsterPeekPx: 280 }
    }
    const stageBox = stage.getBoundingClientRect()
    const monsterBox = monsterEl.getBoundingClientRect()
    const slotCenter = monsterBox.left + monsterBox.width / 2
    const visibleWidth = monsterBox.width * MONSTER_PEEK_VISIBLE
    const peekCenter = stageBox.right - visibleWidth * 0.45
    const monsterPeekPx = Math.max(200, Math.round(peekCenter - slotCenter))
    const offScreenCenter = stageBox.right + monsterBox.width * 0.55
    const monsterEntryFromPx = Math.max(monsterPeekPx + 140, Math.round(offScreenCenter - slotCenter))
    return { monsterEntryFromPx, monsterPeekPx }
  }, [battleStageEl, rosterRef])

  /** How far Blue runs from the left edge to close on the edge-pinned foe. */
  const measureClosureRun = useCallback(() => {
    const playerEl = playerRef.current?.element()
    const lead = rosterRef.current[0]
    const monsterEl = lead ? monsterHandles.current.get(lead.id)?.element() : null
    if (!playerEl || !monsterEl) {
      return { blueClosurePx: 180 }
    }
    const playerBox = playerEl.getBoundingClientRect()
    const monsterBox = monsterEl.getBoundingClientRect()
    const playerShift = readTranslateX(playerEl)
    const monsterShift = readTranslateX(monsterEl)
    const playerRestCenter = playerBox.left + playerBox.width / 2 - playerShift
    const monsterRestCenter = monsterBox.left + monsterBox.width / 2 - monsterShift
    const monsterCurrentCenter = monsterBox.left + monsterBox.width / 2
    const combatGapPx = Math.max(0, monsterRestCenter - playerRestCenter)
    const blueClosurePx = Math.round(monsterCurrentCenter - combatGapPx - playerRestCenter)
    return { blueClosurePx: Math.max(playerShift + 48, blueClosurePx) }
  }, [rosterRef])

  const centerScrollPx = useCallback(() => {
    const stage = battleStageEl()
    if (!stage) return 280
    return Math.round(stage.getBoundingClientRect().width * CENTER_SCROLL_FRAC)
  }, [battleStageEl])

  return {
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
  }
}
