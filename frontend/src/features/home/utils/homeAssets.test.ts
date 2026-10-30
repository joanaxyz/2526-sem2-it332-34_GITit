import { describe, expect, it } from 'vitest'

import { ACHIEVEMENT_IMAGES } from '@/features/home/utils/achievementImages'
import { companionAvatarSrc, homeAssetManifest, homeBackdropSrc } from '@/features/home/utils/homeAssets'
import { COMPANIONS } from '@/shared/cosmetics/companions/registry'
import type { ShopCatalog } from '@/shared/shop/api/shopApi'

function catalog(overrides: Partial<ShopCatalog>): ShopCatalog {
  return {
    active_companion: null,
    items: [],
    ...overrides,
  } as ShopCatalog
}

function companionItem(slug: string, owned: boolean, active = false) {
  return { kind: 'companion', slug, owned, active } as ShopCatalog['items'][number]
}

describe('homeAssetManifest', () => {
  it('warms the backdrop even before the catalog arrives', () => {
    const manifest = homeAssetManifest({ catalog: undefined, view: 'profile' })

    expect(manifest.images).toEqual([homeBackdropSrc()])
    expect(manifest.anchored).toEqual([])
  })

  it('warms the equipped companion and every owned roster avatar', () => {
    const manifest = homeAssetManifest({
      catalog: catalog({
        active_companion: 'blue',
        items: [
          companionItem('blue', true, true),
          companionItem('white', true),
          companionItem('black', false),
          companionItem('not-registered', true),
        ],
      }),
      view: 'profile',
    })

    const blue = COMPANIONS.blue.sprites
    expect(manifest.images).toContain(blue.portrait?.src ?? blue.idle?.src)
    expect(manifest.images).toContain(companionAvatarSrc('blue'))
    expect(manifest.images).toContain(companionAvatarSrc('white'))
    expect(manifest.images).not.toContain(companionAvatarSrc('black'))
    expect(manifest.anchored.map((sheet) => sheet.src)).toContain(blue.idle?.src)
    expect(new Set(manifest.images).size).toBe(manifest.images.length)
  })

  it('warms achievement art only when Home opens on skills', () => {
    const achievementArt = Object.values(ACHIEVEMENT_IMAGES)

    expect(homeAssetManifest({ catalog: undefined, view: 'profile' }).images)
      .not.toContain(achievementArt[0])
    expect(homeAssetManifest({ catalog: undefined, view: 'skills' }).images)
      .toEqual(expect.arrayContaining(achievementArt))
  })
})
