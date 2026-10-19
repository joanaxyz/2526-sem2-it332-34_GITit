import { describe, expect, it } from 'vitest'

import { DESIGN_PREVIEW_STORY_MAP_ROUTE, STORIES_ROUTE, isStoryMapRoute, storyPath, storyPathWithQuery } from './routes'

describe('current story routes', () => {
  it('uses the active Arcane Spire story by default', () => {
    expect(storyPath()).toBe('/stories/arcane-spire')
    expect(storyPath('another-story')).toBe('/stories/another-story')
    expect(STORIES_ROUTE).toBe('/stories')
    expect(DESIGN_PREVIEW_STORY_MAP_ROUTE).toBe('/design-preview/story-map')
  })

  it('keeps gameplay return links on their story and chapter', () => {
    expect(storyPathWithQuery(undefined, 'chapter=35')).toBe('/stories/arcane-spire?chapter=35')
    expect(storyPathWithQuery('another-story', '?chapter=8')).toBe('/stories/another-story?chapter=8')
  })

  it.each(['/stories', '/stories/', '/stories/arcane-spire', '/stories/arcane-spire/'])(
    'recognizes the current story-map URL %s',
    (pathname) => expect(isStoryMapRoute(pathname)).toBe(true),
  )

  it.each([
    '/stories-old',
    '/stories/arcane-spire/editor',
    '/stories/arcane-spire/extra',
    '/home',
    '/shop',
    '/tower',
    '/towers/arcane-spire',
    '/archive/shared/1',
  ])('does not apply story-map chrome to %s', (pathname) => {
    expect(isStoryMapRoute(pathname)).toBe(false)
  })
})
