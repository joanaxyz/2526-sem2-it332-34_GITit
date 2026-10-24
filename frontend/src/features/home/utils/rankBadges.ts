import { warmImage } from '@/shared/sprites/preload'

type BadgeLoader = () => Promise<{ default: string }>

// Each badge is imported lazily so the art stays out of Home's entry chunk.
export const RANK_BADGE_LOADERS: Record<string, BadgeLoader> = {
  '1': () => import('@/assets/images/rank1.webp'),
  '2': () => import('@/assets/images/rank2.webp'),
  '3': () => import('@/assets/images/rank3.webp'),
  '4': () => import('@/assets/images/rank4.webp'),
  '5': () => import('@/assets/images/rank5.webp'),
  '6': () => import('@/assets/images/rank6.webp'),
}

/**
 * Badge URLs already resolved and decoded this session. A badge read from here
 * paints on its first render instead of one effect later, which is what keeps
 * the rank crest and ladder from popping in after Home opens.
 */
const resolvedBadges = new Map<string, string>()

export function resolvedRankBadge(key: string): string | null {
  return resolvedBadges.get(key) ?? null
}

/** Resolve and decode every badge the rank ladder paints. Never rejects. */
export function warmRankBadges(): Promise<void> {
  return Promise.all(
    Object.entries(RANK_BADGE_LOADERS).map(async ([key, load]) => {
      if (resolvedBadges.has(key)) return
      try {
        const { default: src } = await load()
        await warmImage(src)
        resolvedBadges.set(key, src)
      } catch {
        // A missing badge falls back to the lazy path; it must not hold Home.
      }
    }),
  ).then(() => undefined)
}
