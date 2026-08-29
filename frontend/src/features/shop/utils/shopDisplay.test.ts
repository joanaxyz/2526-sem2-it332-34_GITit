import { describe, expect, it } from 'vitest'

import {
  actionDisabled,
  actionLabel,
  isShopTab,
  shopTabs,
} from './shopDisplay'
import type { ShopItem } from '@/shared/shop/api/shopApi'

const baseItem = {
  label: 'Item',
  price: 0,
  owned: false,
  active: false,
} satisfies Omit<ShopItem, 'kind' | 'slug'>

describe('shopDisplay', () => {
  it('offers only the stories and companions shop tabs', () => {
    expect(shopTabs.map((tab) => tab.id)).toEqual(['stories', 'companions'])
    expect(isShopTab('gitcoins')).toBe(false)
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
