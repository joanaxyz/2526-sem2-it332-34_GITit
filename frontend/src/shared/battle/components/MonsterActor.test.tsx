import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { BattleMonster } from '@/shared/battle/types'
import { DEFAULT_STORY_WORLD_SLUG, getStoryWorld } from '@/shared/story-worlds/registry'
import { MonsterActor } from './MonsterActor'

const storyWorld = getStoryWorld(DEFAULT_STORY_WORLD_SLUG)

function monster(): BattleMonster {
  return {
    id: 7,
    species: 'bone-soldier',
    tier: 'mob',
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
