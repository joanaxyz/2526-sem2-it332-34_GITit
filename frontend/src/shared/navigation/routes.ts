import { matchPath } from 'react-router-dom'

const DEFAULT_STORY_SLUG = 'arcane-spire'

export const HOME_ROUTE = '/home'
export const SHOP_ROUTE = '/shop'
export const STORY_DETAIL_ROUTE = '/stories/:storySlug'
export const DESIGN_PREVIEW_STORY_MAP_ROUTE = '/design-preview/story-map'
export const ADMIN_ROUTES = {
  dashboard: '/admin',
  users: '/admin/users',
  economy: '/admin/economy',
  curriculum: '/admin/curriculum',
  analytics: '/admin/analytics',
  settings: '/admin/settings',
} as const

export function storyPath(slug: string = DEFAULT_STORY_SLUG): string {
  return `/stories/${slug}`
}

export function storyPathWithQuery(slug: string = DEFAULT_STORY_SLUG, query: string): string {
  const suffix = query.startsWith('?') ? query : `?${query}`
  return `${storyPath(slug)}${suffix}`
}

export function isStoryMapRoute(pathname: string): boolean {
  return matchPath(STORY_DETAIL_ROUTE, pathname) !== null
}
