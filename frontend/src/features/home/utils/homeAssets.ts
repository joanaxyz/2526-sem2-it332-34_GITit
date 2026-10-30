import heroShowcasePedestalImage from '@/assets/images/hero_showcase_pedestal.png'
import type { HomeView } from '@/features/home/components/home-hub/homeViews'
import { ACHIEVEMENT_IMAGES } from '@/features/home/utils/achievementImages'
import { warmRankBadges } from '@/features/home/utils/rankBadges'
import { COMPANIONS, getCompanion } from '@/shared/cosmetics/companions/registry'
import { companionFromDef } from '@/shared/cosmetics/companionRuntime'
import type { ShopCatalog } from '@/shared/shop/api/shopApi'
import { hasLocalDefinition, toDisplayItem } from '@/shared/shop/model/shopPresentation'
import { warmImages, warmSprite, withBudget } from '@/shared/sprites/preload'
import type { SpriteAnimation } from '@/shared/sprites/types'
import { loadImagePixelBounds } from '@/shared/sprites/usePixelBounds'
import { DEFAULT_STORY_WORLD_SLUG, getStoryWorld } from '@/shared/story-worlds/registry'

/**
 * How long Home waits on art before opening anyway. Long enough that a normal
 * connection never hits it; short enough that one stalled image cannot strand
 * the player behind the loading screen.
 */
export const HOME_ASSET_BUDGET_MS = 12_000

/** Every image Home paints when it opens, split like a battle manifest. */
export type HomeAssetManifest = {
  /** Sheets drawn aligned to their visible pixels, so they are measured too. */
  anchored: SpriteAnimation[]
  images: string[]
}

export function homeBackdropSrc(): string {
  const storyWorld = getStoryWorld(DEFAULT_STORY_WORLD_SLUG)
  return storyWorld.map?.background.src ?? '/cosmetics/story-worlds/arcane-spire/backgrounds/level-map.png'
}

/** Square avatar art, falling back to portrait/idle for companions without one. */
export function companionAvatarSrc(slug: string, fallback?: string): string | undefined {
  const sprites = COMPANIONS[slug]?.sprites
  return sprites?.avatar?.src ?? sprites?.portrait?.src ?? fallback
}

/**
 * The profile workspace is always mounted (only hidden on other views), so its
 * art is part of every entry; achievement art only when Home opens on them.
 */
export function homeAssetManifest({
  catalog,
  view,
}: {
  catalog: ShopCatalog | undefined
  view: HomeView
}): HomeAssetManifest {
  const anchored: SpriteAnimation[] = []
  const images = [homeBackdropSrc()]

  const equippedSlug = catalog?.active_companion
  if (equippedSlug) {
    const companion = getCompanion(equippedSlug)
    const portrait = companion.sprites.portrait?.src ?? companion.sprites.idle?.src
    if (portrait) images.push(portrait)
    // The showcase pins the idle sheet to its measured feet.
    const runtime = companionFromDef(companion)
    if (runtime) anchored.push(runtime.sprites.idle)
  }

  for (const item of catalog?.items.filter(hasLocalDefinition).map(toDisplayItem) ?? []) {
    if (!item.owned) continue
    const avatar = companionAvatarSrc(item.slug, item.art)
    if (avatar) images.push(avatar)
  }

  if (view === 'skills') images.push(...Object.values(ACHIEVEMENT_IMAGES))

  return { anchored, images: Array.from(new Set(images.filter(Boolean))) }
}

/** Decode and measure everything Home opens with. Never rejects. */
export function warmHomeAssets(
  manifest: HomeAssetManifest,
  options: { timeoutMs?: number } = {},
): Promise<void> {
  const work = Promise.all([
    warmRankBadges(),
    loadImagePixelBounds(heroShowcasePedestalImage),
    ...manifest.anchored.map((sheet) => warmSprite(sheet, { measureAnchor: true })),
    warmImages(manifest.images),
  ]).then(
    () => undefined,
    () => undefined,
  )
  return withBudget(work, options.timeoutMs)
}
