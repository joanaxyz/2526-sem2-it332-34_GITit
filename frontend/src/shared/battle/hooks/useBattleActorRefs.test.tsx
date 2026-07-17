import { renderHook } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import type { MonsterActorHandle } from '@/shared/battle/components/MonsterActor'
import type { BattleMonster } from '@/shared/battle/types'
import { DEFAULT_STORY_WORLD_SLUG, getStoryWorld } from '@/shared/story-worlds/registry'

import { useBattleActorRefs } from './useBattleActorRefs'

function rect(left: number, top: number, width: number, height: number): DOMRect {
  return {
    x: left,
    y: top,
    left,
    top,
    right: left + width,
    bottom: top + height,
    width,
    height,
    toJSON: () => ({}),
  }
}

function monsterHandle(bodyBounds: ReturnType<MonsterActorHandle['bodyBounds']>): MonsterActorHandle {
  const done = () => Promise.resolve()
  return {
    attack: done,
    recover: done,
    hurt: done,
    die: done,
    prepOffscreen: vi.fn(),
    walkIn: done,
    slideTo: done,
    bodyBounds: () => bodyBounds,
    element: () => document.createElement('div'),
  }
}

describe('useBattleActorRefs monster effect anchors', () => {
  it('centers body impacts and feet effects on visible pixel bounds', () => {
    const roster: BattleMonster[] = [
      { id: 7, species: 'bone-soldier', hp: 2, max_hp: 2, alive: true },
    ]
    const rosterRef = { current: roster }
    const storyWorldRef = { current: getStoryWorld(DEFAULT_STORY_WORLD_SLUG) }
    const layer = document.createElement('div')
    vi.spyOn(layer, 'getBoundingClientRect').mockReturnValue(rect(10, 20, 500, 400))

    const { result } = renderHook(() => useBattleActorRefs(rosterRef, storyWorldRef))
    result.current.bindEffectLayer(layer)
    result.current.bindMonster(
      7,
      monsterHandle({ left: 210, top: 120, right: 310, bottom: 320, width: 100, height: 200 }),
    )

    expect(result.current.monsterImpactAnchor(7)).toEqual({ x: 250, y: 200 })
    expect(result.current.monsterFeetAnchor(7)).toEqual({ x: 250, y: 298 })
    expect(result.current.monsterSizeScale(7)).toBe(1.25)
  })
})
