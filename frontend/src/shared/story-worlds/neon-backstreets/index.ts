import type { StoryBattleDef, StoryWorldDef } from '@/shared/story-worlds/types'

import battleData from './data/battle.json'
import monstersData from './data/monsters.json'

const chapterKeys = [
  'skyline-01-transit-hub',
  'skyline-02-archive-highrise',
  'skyline-03-debug-lab',
  'skyline-04-simulation-deck',
  'skyline-05-multi-level-campus',
  'skyline-06-automation-district',
  'skyline-07-security-center',
  'skyline-08-maintenance-core',
  'skyline-09-network-operations-center',
  'skyline-10-migration-transit-ring',
  'skyline-09-data-center-roof',
  'skyline-12-command-research-roof',
]
const chapterBackgrounds = chapterKeys.map(
  (_, index) => {
    const chapter = String(index + 1).padStart(2, '0')
    return `/cosmetics/story-worlds/neon-backstreets/backgrounds/battle/chapter-${chapter}.png`
  },
)

const monsterPoses = [
  '/cosmetics/story-worlds/neon-backstreets/monsters/monster-11/pose/idle.png',
  '/cosmetics/story-worlds/neon-backstreets/monsters/monster-05/pose/idle.png',
  '/cosmetics/story-worlds/neon-backstreets/monsters/monster-06/pose/idle.png',
  '/cosmetics/story-worlds/neon-backstreets/monsters/monster-10/pose/idle.png',
  '/cosmetics/story-worlds/neon-backstreets/monsters/monster-08/pose/idle.png',
]

export const neonBackstreetsWorld: StoryWorldDef = {
  slug: 'neon-backstreets',
  label: 'Neon Backstreets',
  tone: 'neon',
  sky: {
    base: '#030914',
    background: [
      'linear-gradient(116deg, transparent 0 43%, rgba(0, 217, 255, 0.08) 43% 44%, transparent 44% 100%)',
      'radial-gradient(85% 65% at 16% 20%, rgba(0, 220, 255, 0.15), transparent 60%)',
      'radial-gradient(80% 60% at 84% 35%, rgba(255, 71, 215, 0.13), transparent 62%)',
      'linear-gradient(180deg, #071426 0%, #030914 55%, #02050d 100%)',
    ].join(', '),
    starfield: false,
  },
  tokens: {
    primaryRgb: '0, 223, 255',
    secondaryRgb: '255, 72, 207',
    accentRgb: '127, 255, 189',
    surfaceRgb: '3, 9, 20',
    glowRgb: '0, 193, 255',
    sparkRgb: '180, 255, 234',
  },
  battle: {
    backdrop: battleData.backdrop,
    parallax: Object.fromEntries(
      chapterKeys.map((key, index) => [key, { ...battleData.backdrop, src: chapterBackgrounds[index] }]),
    ),
    monsters: monstersData,
  } as unknown as StoryBattleDef,
  map: {
    background: {
      src: '/cosmetics/story-worlds/neon-backstreets/backgrounds/level-map.png',
      fps: 1,
      loops: false,
      frameWidth: 1659,
      frameHeight: 948,
      columns: 1,
      rows: 1,
      frameCount: 1,
    },
  },
  preview: { battleBackgrounds: chapterBackgrounds, monsterPoses },
}
