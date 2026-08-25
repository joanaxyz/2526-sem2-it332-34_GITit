import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { BattleMonster } from '@/shared/battle/types'
import { DEFAULT_STORY_WORLD_SLUG, getStoryWorld } from '@/shared/story-worlds/registry'
import { MonsterActor } from './MonsterActor'
import { projectMonsterBodyBounds } from './monsterBodyBounds'

const storyWorld = getStoryWorld(DEFAULT_STORY_WORLD_SLUG)

function monster(): BattleMonster {
  return {
    id: 7,
    species: 'bone-soldier',
    hp: 2,
    max_hp: 2,
    alive: true,
  }
}

function actorWrap(): HTMLElement {
  const sprite = screen.getByRole('img', { name: /bone soldier/i })
  const wrap = sprite.closest('.relative')
  if (!(wrap instanceof HTMLElement)) throw new Error('Monster wrapper not found')
  return wrap
}

describe('MonsterActor visibility', () => {
  afterEach(() => {
    cleanup()
    vi.useRealTimers()
  })

  it('mounts visible when the director is not staging an entrance', () => {
    render(<MonsterActor monster={monster()} storyWorld={storyWorld} />)

    expect(actorWrap().style.opacity).toBe('1')
  })

  it('hides only while staged for entrance choreography', () => {
    const { rerender } = render(<MonsterActor monster={monster()} stagedHidden storyWorld={storyWorld} />)

    expect(actorWrap().style.opacity).toBe('0')

    rerender(<MonsterActor monster={monster()} stagedHidden={false} storyWorld={storyWorld} />)

    expect(actorWrap().style.opacity).toBe('1')
  })

  it('keeps a defeated monster visible on the death frame', () => {
    render(<MonsterActor monster={{ ...monster(), hp: 0, alive: false }} storyWorld={storyWorld} />)

    expect(actorWrap().style.opacity).toBe('1')
  })
})

describe('projectMonsterBodyBounds', () => {
  it('targets the visible body instead of the transparent frame center', () => {
    const body = projectMonsterBodyBounds(
      { left: 100, top: 40, width: 256, height: 256 },
      { width: 256, height: 256 },
      { left: 40, top: 92, right: 168, bottom: 232 },
      false,
    )

    expect(body).toMatchObject({ left: 140, top: 132, right: 269, bottom: 273, width: 129, height: 141 })
    expect(body && body.top + body.height / 2).toBe(202.5)
    expect(body && body.top + body.height / 2).toBeGreaterThan(40 + 256 / 2)
  })

  it('mirrors asymmetric visible bounds for left-facing monsters', () => {
    const body = projectMonsterBodyBounds(
      { left: 100, top: 40, width: 256, height: 256 },
      { width: 256, height: 256 },
      { left: 40, top: 92, right: 168, bottom: 232 },
      true,
    )

    expect(body).toMatchObject({ left: 187, right: 316 })
  })
})
