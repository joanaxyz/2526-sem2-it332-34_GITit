import { describe, expect, it } from 'vitest'

import {
  actionDisabled,
  actionLabel,
  hasLocalDefinition,
  isShopTab,
  shopTabs,
  toDisplayItem,
} from './shopDisplay'
import type { ShopItem } from '@/features/shop/types'

const baseItem = {
  label: 'Item',
  price: 0,
  owned: false,
  active: false,
  unlocks_story: null,
} satisfies Omit<ShopItem, 'kind' | 'slug'>

describe('shopDisplay', () => {
  it('offers only the stories and companions shop tabs', () => {
    expect(shopTabs.map((tab) => tab.id)).toEqual(['stories', 'companions'])
    expect(isShopTab('gitcoins')).toBe(false)
  })

  it('keeps story catalog entries limited to render-ready story worlds', () => {
    const realStory: ShopItem = { ...baseItem, kind: 'story', slug: 'arcane-spire' }
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

  it('keeps companion slugs separate from story slugs', () => {
    const blackCompanion: ShopItem = { ...baseItem, kind: 'companion', slug: 'black' }
    const blackStory: ShopItem = { ...baseItem, kind: 'story', slug: 'black' }

    expect(hasLocalDefinition(blackCompanion)).toBe(true)
    expect(hasLocalDefinition(blackStory)).toBe(false)
    expect(toDisplayItem(blackCompanion)).toMatchObject({
      kind: 'companion',
      slug: 'black',
      tone: 'shadow',
    })
  })

  it('keeps owned management links active while blocking pending or unaffordable purchases', () => {
    const activeItem = { ...baseItem, kind: 'companion', slug: 'blue', active: true } satisfies ShopItem
    const paidItem = { ...baseItem, kind: 'companion', slug: 'blue', price: 500 } satisfies ShopItem
    const ownedStory = { ...baseItem, kind: 'story', slug: 'arcane-spire', owned: true } satisfies ShopItem

    expect(actionDisabled(activeItem, false, 999, false)).toBe(false)
    expect(actionDisabled(paidItem, true, 999, false)).toBe(true)
    expect(actionDisabled(paidItem, false, 100, false)).toBe(true)
    expect(actionDisabled(paidItem, false, 100, true)).toBe(false)
    expect(actionLabel(paidItem, 100, false)).toBe('Need 400 more')
    expect(actionLabel(ownedStory, 999, false)).toBe('View in Stories')
  })
})
