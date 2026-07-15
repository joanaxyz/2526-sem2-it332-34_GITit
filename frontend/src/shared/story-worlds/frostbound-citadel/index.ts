import type { StoryBattleDef, StoryWorldDef } from '@/shared/story-worlds/types'

import battleData from './data/battle.json'
import monstersData from './data/monsters.json'

const chapterKeys = [
  'frost-01-forge-gate',
  'frost-02-frozen-bridge',
  'frost-03-blizzard-courtyard',
  'frost-04-icebound-vault',
  'frost-05-aurora-anvil',
  'frost-06-signal-bastion',
  'frost-07-summit-observatory',
  'frost-08-avalanche-debug-tunnel',
  'frost-09-aurora-release-platform',
]
const chapterBackgrounds = chapterKeys.map(
  (_, index) => {
    const chapter = String(index + 1).padStart(2, '0')
    return `/cosmetics/story-worlds/frostbound-citadel/backgrounds/battle/chapter-${chapter}.png`
  },
)

const monsterPoses = [
  '/cosmetics/story-worlds/frostbound-citadel/monsters/monster-11/pose/idle.png',
  '/cosmetics/story-worlds/frostbound-citadel/monsters/monster-05/pose/idle.png',
  '/cosmetics/story-worlds/frostbound-citadel/monsters/monster-06/pose/idle.png',
  '/cosmetics/story-worlds/frostbound-citadel/monsters/monster-10/pose/idle.png',
  '/cosmetics/story-worlds/frostbound-citadel/monsters/monster-08/pose/idle.png',
]

export const frostboundCitadelWorld: StoryWorldDef = {
  slug: 'frostbound-citadel',
  label: 'Frostbound Citadel',
  tone: 'ice',
  sky: {
    base: '#071523',
    background: [
      'radial-gradient(110% 70% at 50% -8%, rgba(181, 245, 255, 0.2), transparent 58%)',
      'radial-gradient(80% 48% at 18% 28%, rgba(100, 210, 255, 0.18), transparent 62%)',
      'radial-gradient(84% 50% at 82% 34%, rgba(156, 124, 255, 0.12), transparent 62%)',
      'linear-gradient(180deg, #0d2a3f 0%, #071523 52%, #03101c 100%)',
    ].join(', '),
    starfield: true,
  },
  tokens: {
    primaryRgb: '115, 221, 255',
    secondaryRgb: '148, 170, 255',
    accentRgb: '204, 250, 255',
    surfaceRgb: '4, 20, 34',
    glowRgb: '93, 207, 255',
    sparkRgb: '223, 253, 255',
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
      src: '/cosmetics/story-worlds/frostbound-citadel/backgrounds/level-map.png',
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
