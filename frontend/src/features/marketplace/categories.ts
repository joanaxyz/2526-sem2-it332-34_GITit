import { BookOpen, Castle, Gem, Ghost, ScrollText, Sparkles, Swords, Trophy, User, type LucideIcon } from 'lucide-react'

import type { MarketplaceListing } from '@/features/marketplace/api/marketplaceApi'

export type Category = 'relic' | 'lore' | 'spire'

export const CATEGORY_ITEM_KIND: Record<Category, MarketplaceListing['item_kind']> = {
  relic: 'asset',
  lore: 'content_definition',
  spire: 'tower_design',
}

export const CATEGORIES: { id: Category; label: string; icon: LucideIcon }[] = [
  { id: 'relic', label: 'Relics', icon: Gem },
  { id: 'lore', label: 'Lore', icon: ScrollText },
  { id: 'spire', label: 'Spires', icon: Castle },
]

/** Sub-kinds shown as a second hairline row per category. */
export const SUBKINDS: Record<Category, { id: string; label: string; icon: LucideIcon }[]> = {
  relic: [
    { id: 'monster', label: 'Monsters', icon: Ghost },
    { id: 'character', label: 'Characters', icon: User },
    { id: 'tower_artifact', label: 'Artifacts', icon: Sparkles },
    { id: 'tower_piece', label: 'Pieces', icon: Castle },
  ],
  lore: [
    { id: 'adventure', label: 'Adventures', icon: Swords },
    { id: 'challenge', label: 'Challenges', icon: Trophy },
    { id: 'tome', label: 'Tomes', icon: BookOpen },
  ],
  spire: [],
}

const SUBKIND_ICON: Record<string, LucideIcon> = {
  monster: Ghost,
  character: User,
  tower_artifact: Sparkles,
  tower_piece: Castle,
  adventure: Swords,
  challenge: Trophy,
  tome: BookOpen,
}

export function listingSigil(listing: MarketplaceListing): LucideIcon {
  if (listing.item_kind === 'tower_design') return Castle
  const kind = listing.item.kind
  return (kind && SUBKIND_ICON[kind]) || Gem
}

export function listingTitle(listing: MarketplaceListing): string {
  return (
    listing.item.title ||
    listing.item.label ||
    listing.item.slug ||
    `${listing.item_kind} #${listing.item_id}`
  )
}
