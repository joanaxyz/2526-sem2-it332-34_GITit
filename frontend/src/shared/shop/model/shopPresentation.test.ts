import { describe, expect, it } from 'vitest'

import type { ShopItem } from '@/shared/shop/api/shopApi'
import {
  hasLocalDefinition,
  statusLabel,
  toDisplayItem,
} from '@/shared/shop/model/shopPresentation'

const baseItem = {
  kind: 'companion',
  label: 'Item',
  price: 0,
  owned: false,
  active: false,
} satisfies Omit<ShopItem, 'slug'>

describe('shopPresentation', () => {
  it('hides companions with no registered art so no slide renders broken', () => {
    expect(hasLocalDefinition({ ...baseItem, slug: 'blue' })).toBe(true)
    expect(hasLocalDefinition({ ...baseItem, slug: 'not-render-ready' })).toBe(false)
  })

  it('derives companion tone, art, and status', () => {
    const companion: ShopItem = {
      ...baseItem,
      slug: 'black',
      price: 150,
      owned: true,
      active: true,
    }

    expect(toDisplayItem(companion)).toMatchObject({ tone: 'shadow' })
    expect(toDisplayItem({ ...baseItem, slug: 'white' })).toMatchObject({ tone: 'ice' })
    expect(toDisplayItem({ ...baseItem, slug: 'blue' }).art).toBeDefined()
    expect(statusLabel(toDisplayItem(companion))).toBe('Equipped')
    expect(statusLabel(toDisplayItem({ ...baseItem, slug: 'blue', price: 150 }))).toBe('150 GitCoins')
  })
})
