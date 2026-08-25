import { COMPANIONS } from '@/shared/cosmetics/companions/registry'
import type { ShopItem } from '@/shared/shop/api/shopApi'
import { STORY_WORLDS } from '@/shared/story-worlds/registry'
import { storyPreview } from '@/shared/story-worlds/storyPreviews'

export type ShopDisplayItem = ShopItem & {
  art?: string
  tone?: 'blue' | 'ice' | 'shadow' | 'neon'
}

function companionTone(slug: string): ShopDisplayItem['tone'] {
  if (slug === 'white') return 'ice'
  if (slug === 'black') return 'shadow'
  return 'blue'
}

export function toDisplayItem(item: ShopItem): ShopDisplayItem {
  if (item.kind === 'story') {
    const worldSlug = item.unlocks_story?.world_slug ?? item.slug
    const preview = storyPreview(worldSlug)
    return {
      ...item,
      art: preview?.storyMap,
      tone: STORY_WORLDS[worldSlug]?.tone ?? 'blue',
    }
  }

  const companion = COMPANIONS[item.slug]
  return {
    ...item,
    art: companion?.sprites.portrait?.src ?? companion?.sprites.idle?.src,
    tone: companionTone(item.slug),
  }
}

export function hasLocalDefinition(item: ShopItem) {
  if (item.kind === 'story') {
    const worldSlug = item.unlocks_story?.world_slug ?? item.slug
    return Boolean(STORY_WORLDS[worldSlug])
  }
  return Boolean(COMPANIONS[item.slug])
}

export function statusLabel(item: ShopDisplayItem): string {
  if (item.active) return 'Equipped'
  if (item.owned) return 'Owned'
  if (item.price === 0) return 'Free'
  return `${item.price.toLocaleString()} GitCoins`
}
