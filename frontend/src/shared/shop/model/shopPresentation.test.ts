import { describe, expect, it } from 'vitest'

import type { ShopItem } from '@/shared/shop/api/shopApi'
import {
  hasLocalDefinition,
  statusLabel,
  toDisplayItem,
} from '@/shared/shop/model/shopPresentation'

const baseItem = {
  label: 'Item',
  price: 0,
  owned: false,
  active: false,
} satisfies Omit<ShopItem, 'kind' | 'slug'>

describe('shopPresentation', () => {
  it('maps only render-ready story worlds through exact generated unlock fields', () => {
    const realStory: ShopItem = {
      ...baseItem,
      kind: 'story',
      slug: 'arcane-spire',
      unlocks_story: {
        slug: 'arcane-spire',
        title: 'Arcane Spire',
        chapter_count: 7,
        world_slug: 'arcane-spire',
        difficulty: 'intermediate',
        prerequisite_story: null,
      },
    }
    const fakeStory: ShopItem = { ...baseItem, kind: 'story', slug: 'not-render-ready' }

    expect(hasLocalDefinition(realStory)).toBe(true)
    expect(hasLocalDefinition(fakeStory)).toBe(false)
    expect(toDisplayItem(realStory)).toMatchObject({
      kind: 'story',
      slug: 'arcane-spire',
      tone: 'blue',
      art: '/cosmetics/story-worlds/arcane-spire/backgrounds/level-map.png',
    })
  })

  it('keeps companion definitions separate and derives their status', () => {
    const companion: ShopItem = {
      ...baseItem,
      kind: 'companion',
      slug: 'black',
      price: 150,
      owned: true,
      active: true,
    }
    const sameSlugStory: ShopItem = { ...baseItem, kind: 'story', slug: 'black' }

    expect(hasLocalDefinition(companion)).toBe(true)
    expect(hasLocalDefinition(sameSlugStory)).toBe(false)
    expect(toDisplayItem(companion)).toMatchObject({ tone: 'shadow' })
    expect(statusLabel(toDisplayItem(companion))).toBe('Equipped')
  })
})
