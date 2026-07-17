import type { StoryBattleDef, StoryWorldDef } from '@/shared/story-worlds/types'

import battleData from './data/battle.json'
import monstersData from './data/monsters.json'

const battleBackgrounds = Array.from(
  { length: 8 },
  (_, index) => {
    const chapter = String(index + 1).padStart(2, '0')
    return `/cosmetics/story-worlds/arcane-spire/backgrounds/battle/chapter-${chapter}.png`
  },
)

const monsterPoses = [
  '/cosmetics/story-worlds/arcane-spire/monsters/monster-11/pose/idle.png',
  '/cosmetics/story-worlds/arcane-spire/monsters/monster-05/pose/idle.png',
  '/cosmetics/story-worlds/arcane-spire/monsters/monster-06/pose/idle.png',
  '/cosmetics/story-worlds/arcane-spire/monsters/monster-10/pose/idle.png',
  '/cosmetics/story-worlds/arcane-spire/monsters/monster-08/pose/idle.png',
]

/** Arcane Spire: the default story world and fallback renderer. */
export const arcaneSpireWorld: StoryWorldDef = {
  slug: 'arcane-spire',
  label: 'Arcane Spire',
  tone: 'blue',
  sky: {
    base: '#05081d',
    // Pure CSS aurora glows over a vertical night gradient. No raster images.
    background: [
      'radial-gradient(120% 70% at 50% -10%, rgba(var(--theme-primary-rgb), 0.10), transparent 60%)',
      'radial-gradient(90% 60% at 15% 30%, rgba(var(--theme-challenge-rgb), 0.10), transparent 55%)',
      'radial-gradient(90% 60% at 85% 50%, rgba(var(--theme-rail-rgb), 0.08), transparent 55%)',
      'linear-gradient(180deg, #070b22 0%, #05081d 45%, #04060f 100%)',
    ].join(', '),
    starfield: true,
  },
  tokens: {
    primaryRgb: '0, 163, 255',
    secondaryRgb: '176, 74, 255',
    accentRgb: '0, 180, 216',
    surfaceRgb: '5, 8, 29',
    glowRgb: '53, 143, 255',
    sparkRgb: '98, 230, 255',
  },
  // Battle visuals (backdrop + crystal + monster roster) are generated from
  // source PNGs; gameplay HP stays in the encounter state.
  battle: {
    backdrop: battleData.backdrop,
    parallax: {
      'chapter-01-foundation-hall': battleData.backdrop,
      'chapter-02-scriptorium-library': {
        ...battleData.backdrop,
        src: battleBackgrounds[1],
      },
      'chapter-03-branching-gallery': {
        ...battleData.backdrop,
        src: battleBackgrounds[2],
      },
      'chapter-04-convergence-chamber': {
        ...battleData.backdrop,
        src: battleBackgrounds[3],
      },
      'chapter-05-recovery-vault': {
        ...battleData.backdrop,
        src: battleBackgrounds[4],
      },
      'chapter-06-stash-workshop': {
        ...battleData.backdrop,
        src: battleBackgrounds[5],
      },
      'chapter-07-remote-relay': {
        ...battleData.backdrop,
        src: battleBackgrounds[6],
      },
      'chapter-08-guild-signal-apex': {
        ...battleData.backdrop,
        src: battleBackgrounds[7],
      },
    },
    monsters: monstersData,
  } as unknown as StoryBattleDef,
  map: {
    background: {
      src: '/cosmetics/story-worlds/arcane-spire/backgrounds/level-map.png',
      fps: 1,
      loops: false,
      frameWidth: 1659,
      frameHeight: 948,
      columns: 1,
      rows: 1,
      frameCount: 1,
    },
  },
  preview: {
    battleBackgrounds,
    monsterPoses,
  },
}
