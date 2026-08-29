import { DEFAULT_STORY_WORLD_SLUG, STORY_WORLDS } from '@/shared/story-worlds/registry'

export type EnvSlide = { key: string; label: string; kind: 'map' | 'battle'; src: string }

export type StoryPreview = {
  storyMap: string
  battleBackgrounds: string[]
  monsterPoses: string[]
}

function titleCase(value: string): string {
  return value
    .split('-')
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const BACKGROUND_LABEL_OVERRIDES: Record<string, string> = {
  'skyline-01-transit-hub': 'Street-Food Promenade',
  'skyline-02-archive-highrise': 'Boutique Shop Street',
  'skyline-03-debug-lab': 'Mall Atrium',
  'skyline-04-simulation-deck': 'Street-Food Market',
  'skyline-05-multi-level-campus': 'Open-Air Mall',
  'skyline-06-automation-district': 'Convenience Store Avenue',
  'skyline-07-security-center': 'Covered Shopping Arcade',
  'skyline-08-maintenance-core': 'Fashion District Crosswalk',
  'skyline-09-network-operations-center': 'Mall Food Court',
  'skyline-10-migration-transit-ring': 'Electronics Shop Alley',
  'skyline-09-data-center-roof': 'Rooftop Retail Terrace',
  'skyline-12-command-research-roof': 'Street-Shop Plaza',
}

function backgroundLabel(src: string): string {
  const base = src.split('/').pop()?.replace(/\.png$/, '') ?? ''
  if (BACKGROUND_LABEL_OVERRIDES[base]) return BACKGROUND_LABEL_OVERRIDES[base]

  return titleCase(base.replace(/^chapter-\d+-/, '')) || 'Battle Ground'
}

export function storyPreview(slug: string): StoryPreview | undefined {
  const world = STORY_WORLDS[slug]
  if (!world) return undefined

  const fallback = STORY_WORLDS[DEFAULT_STORY_WORLD_SLUG]
  const parallaxBackgrounds = world.battle.parallax
    ? Object.values(world.battle.parallax).map((sprite) => sprite.src)
    : undefined

  const storyMap = world.map?.background.src ?? fallback.map?.background.src
  const battleBackgrounds = world.preview?.battleBackgrounds ?? parallaxBackgrounds ?? fallback.preview?.battleBackgrounds
  const monsterPoses = world.preview?.monsterPoses ?? fallback.preview?.monsterPoses

  if (!storyMap || !battleBackgrounds?.length || !monsterPoses?.length) return undefined

  return {
    storyMap,
    battleBackgrounds,
    monsterPoses,
  }
}

export function environmentSlides(bundle: StoryPreview): EnvSlide[] {
  const battle = [...new Set(bundle.battleBackgrounds)]
  return [
    { key: 'map', label: 'Story Map', kind: 'map', src: bundle.storyMap },
    ...battle.map((src) => ({ key: src, label: backgroundLabel(src), kind: 'battle' as const, src })),
  ]
}
