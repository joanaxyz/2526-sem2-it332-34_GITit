// Mirrors backend/assets/tags.py ASSET_TAGS. Keep in sync when adding tags.
export const ASSET_TAGS = [
  'medieval',
  'arcane',
  'neon',
  'celestial',
  'infernal',
  'ancient',
  'stone',
  'metal',
  'bone',
  'crystal',
  'verdant',
  'shadow',
  'ominous',
  'regal',
  'whimsical',
  'arcane-spire',
] as const

export type AssetTag = (typeof ASSET_TAGS)[number]
