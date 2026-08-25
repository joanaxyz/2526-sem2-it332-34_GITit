import { describe, expect, it, vi } from 'vitest'

import type { PlayerActorHandle } from '@/shared/battle/components/PlayerActor'
import type { EffectContext } from '@/shared/battle/effects/effectRegistry'
import type { CompanionSkill } from '@/shared/cosmetics/companions/companionSkills'

const { effectForSkillMock, effectPlacementForSkillMock, playEffectMock, preloadSpriteSheetMock } = vi.hoisted(() => ({
  effectForSkillMock: vi.fn(),
  effectPlacementForSkillMock: vi.fn(),
  playEffectMock: vi.fn<(context: EffectContext) => Promise<void>>(),
  preloadSpriteSheetMock: vi.fn<() => Promise<void>>(),
}))

vi.mock('@/shared/battle/effects/effectRegistry', () => ({
  effectForSkill: effectForSkillMock,
  effectPlacementForSkill: effectPlacementForSkillMock,
}))

vi.mock('@/shared/battle/effects/skill-effects/spriteDom', () => ({
  preloadSpriteSheet: preloadSpriteSheetMock,
}))

import { playCompanionSkillCast } from './companionCombatPlayback'

const skill: CompanionSkill = {
  family: 'add',
  command: 'git add .',
  tint: '#68d8ff',
  playback: 'projectile',
  anchor: 'feet',
  impactStartFrame: 12,
  animation: {
    name: 'add.skill',
    src: '/add.png',
    frameWidth: 256,
    frameHeight: 256,
    columns: 5,
    rows: 5,
    frameCount: 25,
    fps: 18,
    loop: false,
  },
}

function rect(left: number, top: number, width: number, height: number): DOMRect {
  return {
    x: left,
    y: top,
    left,
    top,
    width,
    height,
    right: left + width,
    bottom: top + height,
    toJSON: () => ({}),
  } as DOMRect
}

describe('playCompanionSkillCast', () => {
  it('finishes the attack windup before launching FX and attack-end together', async () => {
    const order: string[] = []
    const layer = document.createElement('div')
    const backLayer = document.createElement('div')
    const actor = document.createElement('div')
    vi.spyOn(layer, 'getBoundingClientRect').mockReturnValue(rect(100, 50, 500, 400))
    vi.spyOn(actor, 'getBoundingClientRect').mockReturnValue(rect(120, 130, 180, 220))
    preloadSpriteSheetMock.mockImplementation(async () => {
      order.push('preload')
    })
    effectPlacementForSkillMock.mockReturnValue({ playback: 'projectile', anchor: 'feet' })
    playEffectMock.mockImplementation(async () => {
      order.push('effect')
    })
    effectForSkillMock.mockReturnValue(playEffectMock)
    const player = {
      attack: vi.fn(async () => {
        order.push('attack')
      }),
      endAttack: vi.fn(async () => {
        order.push('attack-end')
      }),
      element: () => actor,
    } as unknown as PlayerActorHandle

    await playCompanionSkillCast({ skill, companionSlug: 'blue', player, layer, backLayer })

    expect(order).toEqual(['preload', 'attack', 'effect', 'attack-end'])
    expect(effectForSkillMock).toHaveBeenCalledWith('add', 'blue')
    expect(effectPlacementForSkillMock).toHaveBeenCalledWith('add', 'blue')
    const context = playEffectMock.mock.calls[0]?.[0]
    expect(context).toMatchObject({
      layer,
      backLayer,
      to: { x: 360, y: 188 },
      impactTo: { x: 360, y: 328 },
      sizeScale: 3,
    })
    expect(context?.from.x).toBeCloseTo(196.4)
    expect(context?.from.y).toBeCloseTo(172.4)
    expect(player.endAttack).toHaveBeenCalledWith(false)
  })
})
