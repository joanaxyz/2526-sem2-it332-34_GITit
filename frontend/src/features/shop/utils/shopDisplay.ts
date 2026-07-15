import { BookOpen, User, type LucideIcon } from 'lucide-react'

import type { ShopItem, UnlocksStory } from '@/features/shop/api/shopApi'
import { COMPANIONS } from '@/shared/cosmetics/companions/registry'
import { STORY_WORLDS } from '@/shared/story-worlds/registry'
import { storyPreview } from '@/shared/story-worlds/storyPreviews'

export type ShopTab = 'stories' | 'companions' | 'gitcoins'

export type ShopDisplayItem = ShopItem & {
  art?: string
  tone?: 'blue' | 'ice' | 'shadow' | 'neon'
}

export type ShopTabConfig = {
  id: ShopTab
  label: string
  description: string
  Icon?: LucideIcon
}

export const shopTabs: ShopTabConfig[] = [
  { id: 'stories', label: 'Stories', description: 'World bundles', Icon: BookOpen },
  { id: 'companions', label: 'Companions', description: 'Adventurers', Icon: User },
  { id: 'gitcoins', label: 'GitCoin', description: 'Wallet' },
]

const transactionLabels: Record<string, string> = {
  adventure_level_reward: 'Adventure reward',
  challenge_trial_reward: 'Challenge reward',
  chapter_chest: 'Chapter chest',
  shop_purchase: 'Shop purchase',
  cosmetic_purchase: 'Shop purchase',
  signup_grant: 'Signup grant',
}

export function unlocksLabel(unlocksStory: UnlocksStory | null | undefined): string | null {
  if (!unlocksStory) return null
  const chapters = unlocksStory.chapter_count
  const chapterText =
    chapters > 0 ? `${chapters} chapter${chapters === 1 ? '' : 's'}` : 'chapters coming soon'
  return `Unlocks ${unlocksStory.title} — ${chapterText}`
}

export function formatCoins(value: number) {
  return value.toLocaleString()
}

export function formatTransactionReason(reason: string) {
  return transactionLabels[reason] ?? reason.replaceAll('_', ' ')
}

export function formatTransactionDate(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

export function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : 'The shop action failed.'
}

export function isShopTab(value: string | null): value is ShopTab {
  return value === 'gitcoins' || value === 'stories' || value === 'companions'
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
  return `${formatCoins(item.price)} GitCoins`
}

export function actionLabel(item: ShopDisplayItem, balance: number, walletPending: boolean) {
  if (item.owned && item.kind === 'story') return 'View in Stories'
  if (item.owned && item.kind === 'companion') return 'Manage in Loadout'
  if (item.price === 0) return 'Claim'
  if (!walletPending && item.price > balance) return `Need ${formatCoins(item.price - balance)} more`
  return 'Purchase'
}

export function actionDisabled(item: ShopDisplayItem, pending: boolean, balance: number, walletPending: boolean) {
  return pending || (!item.owned && item.price > 0 && !walletPending && item.price > balance)
}
