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

/** Ownership state only. The price belongs beside the purchase CTA, where the
 *  decision is made - repeating it as a caption chip prints it twice on one
 *  screen. */
export function statusLabel(item: ShopDisplayItem): string {
  if (item.active) return 'Equipped'
  if (item.owned) return 'Owned'
  return 'Not owned'
}
