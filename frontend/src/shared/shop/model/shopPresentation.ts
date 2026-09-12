import { COMPANIONS } from '@/shared/cosmetics/companions/registry'
import type { ShopItem } from '@/shared/shop/api/shopApi'

export type ShopDisplayItem = ShopItem & {
  art?: string
  tone?: 'blue' | 'ice' | 'shadow'
}

function companionTone(slug: string): ShopDisplayItem['tone'] {
  if (slug === 'white') return 'ice'
  if (slug === 'black') return 'shadow'
  return 'blue'
}

export function toDisplayItem(item: ShopItem): ShopDisplayItem {
  const companion = COMPANIONS[item.slug]
  return {
    ...item,
    art: companion?.sprites.portrait?.src ?? companion?.sprites.idle?.src,
    tone: companionTone(item.slug),
  }
}

export function hasLocalDefinition(item: ShopItem) {
  // Companion card art has no placeholder path, so an unregistered companion
  // would render as a visibly broken slide - hide it instead.
  return Boolean(COMPANIONS[item.slug])
}

export function statusLabel(item: ShopDisplayItem): string {
  if (item.active) return 'Equipped'
  if (item.owned) return 'Owned'
  if (item.price === 0) return 'Free'
  return `${item.price.toLocaleString()} GitCoins`
}
