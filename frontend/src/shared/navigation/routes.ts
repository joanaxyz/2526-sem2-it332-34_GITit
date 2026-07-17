import { isLegacyStoryRoute } from './legacyRoutes'

const DEFAULT_STORY_SLUG = 'arcane-spire'

export const HOME_ROUTE = '/home'
export const SHOP_ROUTE = '/shop'
export const STORIES_ROUTE = '/stories'
export const STORY_DETAIL_ROUTE = `${STORIES_ROUTE}/:storySlug`
export const DESIGN_PREVIEW_STORY_MAP_ROUTE = '/design-preview/story-map'

export function storyPath(slug: string = DEFAULT_STORY_SLUG): string {
  return `${STORIES_ROUTE}/${slug}`
}

export function storyPathWithQuery(slug: string = DEFAULT_STORY_SLUG, query: string): string {
  const suffix = query.startsWith('?') ? query : `?${query}`
  return `${storyPath(slug)}${suffix}`
}


export function isStoryMapRoute(pathname: string): boolean {
  if (pathname.includes('/editor')) return false
  return pathname.startsWith(STORIES_ROUTE) || isLegacyStoryRoute(pathname)
}
