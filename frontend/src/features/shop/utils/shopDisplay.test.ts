import { describe, expect, it } from 'vitest'

import { actionDisabled, actionLabel } from './shopDisplay'
import type { ShopItem } from '@/shared/shop/api/shopApi'

const baseItem = {
  kind: 'companion',
  label: 'Item',
  price: 0,
  owned: false,
  active: false,
} satisfies Omit<ShopItem, 'slug'>

describe('shopDisplay', () => {
  it('keeps owned management links active while blocking pending or unaffordable purchases', () => {
    const activeItem = { ...baseItem, slug: 'blue', active: true } satisfies ShopItem
    const paidItem = { ...baseItem, slug: 'blue', price: 500 } satisfies ShopItem
    const ownedItem = { ...baseItem, slug: 'white', owned: true } satisfies ShopItem

    expect(actionDisabled(activeItem, false, 999, false)).toBe(false)
    expect(actionDisabled(paidItem, true, 999, false)).toBe(true)
    expect(actionDisabled(paidItem, false, 100, false)).toBe(true)
    expect(actionDisabled(paidItem, false, 100, true)).toBe(false)
    expect(actionLabel(paidItem, 100, false)).toBe('Need 400 more')
    expect(actionLabel(ownedItem, 999, false)).toBe('Manage in Loadout')
  })
})
