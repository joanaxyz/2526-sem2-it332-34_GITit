/**
 * Isolated compatibility URLs for product terms that were removed from the
 * current architecture. Do not import these into product UI. Keep them here so
 * old bookmarks can redirect without letting deprecated vocabulary leak into
 * active code.
 *
 * Removal target: 2026-09-30.
 */
export const LEGACY_STORY_ROUTE = '/tower'
export const LEGACY_STORIES_ROUTE = '/towers'
export const LEGACY_ARCHIVE_ROUTE = '/archive'
export const LEGACY_MY_STORY_ROUTE = '/my-tower'
export const LEGACY_DESIGN_PREVIEW_STORY_ROUTE = '/design-preview/tower'

export function isLegacyStoryRoute(pathname: string): boolean {
  return (
    pathname === LEGACY_STORY_ROUTE ||
    pathname.startsWith(`${LEGACY_STORY_ROUTE}/`) ||
    pathname.startsWith(LEGACY_STORIES_ROUTE) ||
    pathname.startsWith(LEGACY_ARCHIVE_ROUTE) ||
    pathname.startsWith(LEGACY_MY_STORY_ROUTE)
  )
}
