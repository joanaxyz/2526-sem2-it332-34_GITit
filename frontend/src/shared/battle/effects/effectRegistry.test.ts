import { readFileSync } from 'node:fs'

import { afterEach, describe, expect, it, vi } from 'vitest'

import {
  effectSheetForSkill,
  effectForSkill,
  effectPlaybackForSkill,
  effectPlacementForSkill,
  missedAttack,
  missedAttackForCompanion,
  monsterAttackEffect,
  spriteDisplayMetricsForSkill,
  spriteSourceForSkill,
  tintForSkill,
} from '@/shared/battle/effects/effectRegistry'
import { effectSpecForSkill } from '@/shared/battle/effects/skill-effects/catalog'
import skillIndex from '@/shared/cosmetics/companions/data/companion-skills.json'
import type { SpriteAnimation } from '@/shared/sprites/types'

const ROOT = '/cosmetics/companion/blue/effects/skill-flames-25'
const BLACK_ROOT = '/cosmetics/companion/black/effects/skill-lightning-25'
const WHITE_ROOT = '/cosmetics/companion/white/effects/skill-ice-25'
const README_ROOTS = {
  blue: 'blue/effects/skill-flames-25',
  white: 'white/effects/skill-ice-25',
  black: 'black/effects/skill-lightning-25',
} as const
const GIT_SKILLS = [
  'init',
  'clone',
  'status',
  'config',
  'log',
  'show',
  'diff',
  'add',
  'commit',
  'rm',
  'check-ignore',
  'restore',
  'branch',
  'switch',
  'checkout',
  'merge',
  'merge-base',
  'checkout-conflict',
  'diff-conflict',
  'ls-files',
  'mergetool',
  'reset',
  'revert',
  'reflog',
  'stash',
  'cherry-pick',
  'remote',
  'fetch',
  'pull',
  'push',
  'rebase',
  'tag',
  'rev-list',
  'default',
] as const

function installAnimationMocks() {
  const originalAnimate = HTMLElement.prototype.animate
  const animations: Keyframe[][] = []
  const animationElements: HTMLElement[] = []
  const parents: string[] = []
  Object.defineProperty(HTMLElement.prototype, 'animate', {
    configurable: true,
    value: vi.fn(function (this: HTMLElement, keyframes: Keyframe[] | PropertyIndexedKeyframes) {
      animations.push(keyframes as Keyframe[])
      animationElements.push(this)
      parents.push(this.parentElement?.dataset.testid ?? '')
      return { finished: Promise.resolve(), cancel: vi.fn() } as unknown as Animation
    }),
  })
  vi.spyOn(window, 'requestAnimationFrame').mockImplementation((callback) => {
    callback(performance.now() + 10_000)
    return 1
  })
  return {
    animations,
    animationElements,
    restore: () => {
      if (originalAnimate) {
        Object.defineProperty(HTMLElement.prototype, 'animate', {
          configurable: true,
          value: originalAnimate,
        })
      } else {
        delete (HTMLElement.prototype as Partial<HTMLElement>).animate
      }
      vi.restoreAllMocks()
    },
    parents,
  }
}

function setHostRect(el: HTMLElement, width: number, height: number) {
  Object.defineProperty(el, 'getBoundingClientRect', {
    configurable: true,
    value: () => ({
      width,
      height,
      top: 0,
      right: width,
      bottom: height,
      left: 0,
      x: 0,
      y: 0,
      toJSON: () => ({}),
    }),
  })
}

function translateOf(frame: Keyframe): { x: number; y: number } {
  const match = /translate\(([-\d.]+)px, ([-\d.]+)px\)/.exec(String(frame.transform))
  expect(match).not.toBeNull()
  return { x: Number(match![1]), y: Number(match![2]) }
}

function expectSpriteInsideHost(node: HTMLElement, frame: Keyframe, width: number, height: number) {
  const placed = translateOf(frame)
  const spriteWidth = Number.parseFloat(node.style.width)
  const spriteHeight = Number.parseFloat(node.style.height)
  expect(placed.x).toBeGreaterThanOrEqual(0)
  expect(placed.y).toBeGreaterThanOrEqual(0)
  expect(placed.x + spriteWidth).toBeLessThanOrEqual(width)
  expect(placed.y + spriteHeight).toBeLessThanOrEqual(height)
}

function expectVisibleSpriteInsideHost(
  node: HTMLElement,
  frame: Keyframe,
  bounds: { left: number; top: number; right: number; bottom: number },
  width: number,
  height: number,
) {
  const placed = translateOf(frame)
  const spriteWidth = Number.parseFloat(node.style.width)
  const spriteHeight = Number.parseFloat(node.style.height)
  expect(placed.x + spriteWidth * bounds.left).toBeGreaterThanOrEqual(0)
  expect(placed.y + spriteHeight * bounds.top).toBeGreaterThanOrEqual(0)
  expect(placed.x + spriteWidth * bounds.right).toBeLessThanOrEqual(width)
  expect(placed.y + spriteHeight * bounds.bottom).toBeLessThanOrEqual(height)
}

function scaleOf(frame: Keyframe): number {
  const match = /scale\(([-\d.]+)\)/.exec(String(frame.transform))
  expect(match).not.toBeNull()
  return Number(match![1])
}

function readmePlacement(desc: string): { playback: 'projectile' | 'target' | 'ground'; anchor: 'center' | 'feet' } | null {
  if (desc.includes('impact(ground)')) return { playback: 'projectile', anchor: 'feet' }
  if (desc.includes('impact(center)')) return { playback: 'projectile', anchor: 'center' }
  if (desc === 'target-ground') return { playback: 'target', anchor: 'feet' }
  if (desc === 'target-center') return { playback: 'target', anchor: 'center' }
  if (desc === 'ground-run') return { playback: 'ground', anchor: 'feet' }
  return null
}

function readmeSkillKey(skill: string): string {
  return skill.replace(/_(front|back)$/, '')
}

describe('effectRegistry', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('resolves concrete command forms to their own sheets', () => {
    expect(spriteSourceForSkill('checkout-conflict')).toBe(`${ROOT}/checkout-conflict.png`)
    expect(spriteSourceForSkill('diff-conflict')).toBe(`${ROOT}/diff-conflict.png`)
    expect(spriteSourceForSkill('merge-base')).toBe(`${ROOT}/merge-base.png`)
    expect(spriteSourceForSkill('ls-files')).toBe(`${ROOT}/ls-files.png`)
    expect(spriteSourceForSkill('tag')).toBe(`${ROOT}/tag.png`)
    expect(spriteSourceForSkill('rev-list')).toBe(`${ROOT}/rev-list.png`)
  })

  it('exposes a dedicated miss effect instead of the default projectile', () => {
    expect(spriteSourceForSkill('miss')).toBe(`${ROOT}/miss.png`)
    expect(effectPlaybackForSkill('miss')).toBe('miss')
    expect(tintForSkill('miss')).toBe('ash')
  })

  it('keeps unknown skills on the default sheet', () => {
    expect(spriteSourceForSkill('not-a-real-skill')).toBe(`${ROOT}/default.png`)
    expect(effectPlaybackForSkill('not-a-real-skill')).toBe('projectile')
  })

  it('wires companions without dedicated spell art to the Blue fallback', () => {
    expect(effectSheetForSkill('commit', 'unknown')).toMatchObject({
      name: 'unknown.skill.commit',
      src: `${ROOT}/commit.png`,
    })
    expect(effectPlaybackForSkill('commit', 'unknown')).toBe('target')
  })

  it('uses White ice art for every White skill sheet', () => {
    expect(effectSheetForSkill('init', 'white')).toMatchObject({
      name: 'white.skill.init',
      src: `${WHITE_ROOT}/init.png`,
    })
    expect(effectSheetForSkill('commit', 'white')).toMatchObject({
      name: 'white.skill.commit',
      src: `${WHITE_ROOT}/commit.png`,
    })
    expect(effectSheetForSkill('miss', 'white')).toMatchObject({
      name: 'white.skill.miss',
      src: `${WHITE_ROOT}/miss.png`,
    })
    expect(effectPlaybackForSkill('init', 'white')).toBe('projectile')
    expect(tintForSkill('init', 'white')).toBe('azure')
  })

  it('classifies every concrete git skill as a projectile, target, or ground effect', () => {
    for (const skill of GIT_SKILLS) {
      expect(['projectile', 'target', 'ground']).toContain(effectPlaybackForSkill(skill))
      expect(['projectile', 'target', 'ground']).toContain(effectPlaybackForSkill(skill, 'white'))
      expect(['projectile', 'target', 'ground']).toContain(effectPlaybackForSkill(skill, 'black'))
    }
  })

  it('routes push and switch as ground-travel effects', () => {
    expect(effectPlaybackForSkill('push')).toBe('ground')
    expect(effectPlaybackForSkill('switch')).toBe('ground')
    expect(effectPlacementForSkill('push')).toEqual({ playback: 'ground', anchor: 'feet' })
  })

  it('routes the designer-specified projectile-impact skills as projectiles', () => {
    for (const skill of ['add', 'branch', 'checkout', 'clone', 'default', 'init', 'merge', 'reflog', 'stash', 'diff']) {
      expect(effectPlaybackForSkill(skill)).toBe('projectile')
    }
  })

  it('anchors clone impact per companion art direction', () => {
    expect(effectPlacementForSkill('clone', 'blue')).toEqual({ playback: 'projectile', anchor: 'feet' })
    expect(effectPlacementForSkill('clone', 'white')).toEqual({ playback: 'projectile', anchor: 'center' })
    expect(effectPlacementForSkill('clone', 'black')).toEqual({ playback: 'projectile', anchor: 'center' })
  })

  it('anchors audited grounded projectile impacts on the ground line', () => {
    for (const slug of ['blue', 'white', 'black']) {
      expect(effectPlacementForSkill('init', slug)).toEqual({ playback: 'projectile', anchor: 'feet' })
    }
    // Blue's `add` impact is ground-baked, so it plants on the ground line; White
    // and Black baked theirs as a body-centred burst.
    expect(effectPlacementForSkill('add', 'blue')).toEqual({ playback: 'projectile', anchor: 'feet' })
    expect(effectPlacementForSkill('add', 'white')).toEqual({ playback: 'projectile', anchor: 'center' })
    expect(effectPlacementForSkill('add', 'black')).toEqual({ playback: 'projectile', anchor: 'center' })
    expect(effectPlacementForSkill('branch', 'blue')).toEqual({ playback: 'projectile', anchor: 'feet' })
    expect(effectPlacementForSkill('branch', 'white')).toEqual({ playback: 'projectile', anchor: 'center' })
    expect(effectPlacementForSkill('branch', 'black')).toEqual({ playback: 'projectile', anchor: 'center' })
    expect(effectPlacementForSkill('merge', 'white')).toEqual({ playback: 'projectile', anchor: 'feet' })
    expect(effectPlacementForSkill('stash', 'white')).toEqual({ playback: 'projectile', anchor: 'feet' })
    expect(effectSpecForSkill('add', 'blue')).toMatchObject({
      launchStartFrame: 3,
      impactStartFrame: 16,
    })
  })

  it('keeps runtime placement in sync with generated companion manifests', () => {
    for (const [companionSlug, skills] of Object.entries(skillIndex)) {
      for (const skill of skills) {
        expect(effectPlacementForSkill(skill.family, companionSlug)).toEqual({
          playback: skill.playback,
          anchor: skill.playback === 'ground' ? 'feet' : skill.anchor,
        })
      }
    }
  })

  it('carries the pixel-measured placeAnchor from the companion index onto the runtime spec', () => {
    let checked = 0
    for (const [companionSlug, skills] of Object.entries(skillIndex)) {
      for (const skill of skills) {
        const measured = (skill as { placeAnchor?: { x: number; y: number } }).placeAnchor
        if (!measured) continue
        // The runtime pins the measured pixel anchor, so it must reach the spec
        // verbatim (the fixed FEET/CENTER fraction is only a fallback).
        expect(effectSpecForSkill(skill.family, companionSlug).placeAnchor).toEqual(measured)
        checked += 1
      }
    }
    expect(checked).toBeGreaterThan(0)
  })

  it('keeps runtime placement in sync with companion README choreography notes', () => {
    for (const [companionSlug, root] of Object.entries(README_ROOTS)) {
      const text = readFileSync(
        `public/cosmetics/companion/${root}/README.md`,
        'utf8',
      )
      for (const line of text.split(/\r?\n/)) {
        const [rawSkill, desc] = line.split(' - ')
        if (!rawSkill || !desc) continue
        const expected = readmePlacement(desc.trim())
        if (!expected) continue
        expect(effectPlacementForSkill(readmeSkillKey(rawSkill.trim()), companionSlug), line).toEqual(expected)
      }
    }
  })

  it('plants ground-rooted risers on the ground line and body auras on the body', () => {
    // Risers that grow up from the floor sit on the enemy's ground point.
    for (const skill of [
      'show',
      'commit',
      'restore',
      'rebase',
      'reset',
      'remote',
      'pull',
      'merge-base',
      'cherry-pick',
      'diff-conflict',
      'check-ignore',
      'ls-files',
      'tag',
    ]) {
      expect(effectPlacementForSkill(skill)).toEqual({ playback: 'target', anchor: 'feet' })
    }
    expect(effectPlacementForSkill('ls-files', 'white')).toEqual({ playback: 'target', anchor: 'center' })
    expect(effectPlacementForSkill('ls-files', 'black')).toEqual({ playback: 'target', anchor: 'feet' })
    // Auras/bursts that play on the monster body are centered on it, not the floor.
    for (const skill of ['status', 'config', 'log', 'revert', 'mergetool', 'fetch', 'rev-list']) {
      expect(effectPlacementForSkill(skill)).toEqual({ playback: 'target', anchor: 'center' })
    }
    // Body-impact projectiles keep the centered impact anchor.
    expect(effectPlacementForSkill('default').anchor).toBe('center')
  })

  it('classifies rm as a projectile for every companion', () => {
    for (const slug of ['blue', 'white', 'black']) {
      expect(effectPlacementForSkill('rm', slug)).toEqual({ playback: 'projectile', anchor: 'center' })
    }
  })

  it('scales the effect up for a bigger monster via ctx.sizeScale', async () => {
    const runtime = installAnimationMocks()
    try {
      const layer = document.createElement('div')
      await effectForSkill('status')({ layer, from: { x: 80, y: 90 }, to: { x: 300, y: 200 }, sizeScale: 2 })
      const base = spriteDisplayMetricsForSkill('status')
      const node = runtime.animationElements[0]
      expect(Number.parseFloat(node.style.width)).toBeCloseTo(base.width * 2, 4)
      expect(Number.parseFloat(node.style.height)).toBeCloseTo(base.height * 2, 4)
    } finally {
      runtime.restore()
    }
  })

  it('plays layered companion spells behind and in front of the actors', async () => {
    const runtime = installAnimationMocks()
    try {
      const frontLayer = document.createElement('div')
      frontLayer.dataset.testid = 'front-layer'
      const backLayer = document.createElement('div')
      backLayer.dataset.testid = 'back-layer'
      await effectForSkill('remote', 'black')({
        layer: frontLayer,
        backLayer,
        from: { x: 80, y: 90 },
        to: { x: 300, y: 200 },
      })
      expect(runtime.parents).toContain('front-layer')
      expect(runtime.parents).toContain('back-layer')
    } finally {
      runtime.restore()
    }
  })

  it('uses the single Blue remote sheet and split Black remote sheets', () => {
    expect(spriteSourceForSkill('remote', 'blue')).toBe(`${ROOT}/remote.png`)
    expect(spriteSourceForSkill('remote', 'black')).toBe(`${BLACK_ROOT}/remote_front.png`)
  })

  it('uses Black lightning art for every Black skill sheet', () => {
    expect(effectSheetForSkill('init', 'black')).toMatchObject({
      name: 'black.skill.init',
      src: `${BLACK_ROOT}/init.png`,
    })
    expect(effectSheetForSkill('miss', 'black')).toMatchObject({
      name: 'black.skill.miss',
      src: `${BLACK_ROOT}/miss.png`,
    })
    expect(spriteSourceForSkill('push', 'black')).toBe(`${BLACK_ROOT}/push.png`)
    expect(effectPlaybackForSkill('init', 'black')).toBe('projectile')
    expect(tintForSkill('init', 'black')).toBe('violet')
  })

  it('keeps projectile fireballs compact enough to land on monster edges', () => {
    expect(spriteDisplayMetricsForSkill('default')).toMatchObject({
      width: 138.24,
      height: 138.24,
      playback: 'projectile',
    })
    expect(spriteDisplayMetricsForSkill('push').width).toBeLessThanOrEqual(140)
    expect(spriteDisplayMetricsForSkill('miss').width).toBeLessThanOrEqual(144)
  })

  it('lands projectile noses on the supplied target point instead of centering the sprite there', async () => {
    const runtime = installAnimationMocks()
    try {
      const layer = document.createElement('div')
      await effectForSkill('default')({ layer, from: { x: 80, y: 90 }, to: { x: 300, y: 140 } })

      // The flight is launch -> nose(@0.82) -> settle; its nose keyframe lands the
      // nose on the target (the impact/dissipate pop then plays there, pinned).
      const flight = runtime.animations.find((frames) => frames.length === 3 && frames[1].offset === 0.82)
      expect(flight).toBeDefined()
      const nose = translateOf(flight![1])
      const metrics = spriteDisplayMetricsForSkill('default')
      expect(nose.x + metrics.width * 0.78).toBeCloseTo(300, 4)
      expect(nose.y + metrics.height * 0.52).toBeCloseTo(140, 4)
    } finally {
      runtime.restore()
    }
  })

  it('lands a target effect planted on the enemy ground line', async () => {
    const runtime = installAnimationMocks()
    try {
      const layer = document.createElement('div')
      await effectForSkill('reset', 'blue')({ layer, from: { x: 80, y: 90 }, to: { x: 300, y: 200 } })

      expect(effectPlaybackForSkill('reset', 'blue')).toBe('target')
      const fade = runtime.animations.find((frames) => frames.length === 4 && frames[1].offset === 0.18)
      expect(fade).toBeDefined()
      const impact = translateOf(fade![1])
      const metrics = spriteDisplayMetricsForSkill('reset', 'blue')
      // Planted on the target via the pixel-measured placeAnchor (a ground-rooted
      // riser, so its measured base sits low in the cell).
      const pa = effectSpecForSkill('reset', 'blue').placeAnchor!
      expect(pa.y).toBeGreaterThan(0.6)
      expect(impact.x + metrics.width * pa.x).toBeCloseTo(300, 4)
      expect(impact.y + metrics.height * pa.y).toBeCloseTo(200, 4)
    } finally {
      runtime.restore()
    }
  })

  it('keeps the visible pixels of an edge-pinned Blue rebase effect inside the stage', async () => {
    const runtime = installAnimationMocks()
    try {
      const layer = document.createElement('div')
      setHostRect(layer, 360, 220)

      await effectForSkill('rebase', 'blue')({
        layer,
        from: { x: 80, y: 120 },
        to: { x: 430, y: 210 },
        sizeScale: 2,
      })

      const fade = runtime.animations.find((frames) => frames.length === 4 && frames[1].offset === 0.18)
      expect(fade).toBeDefined()
      const index = runtime.animations.indexOf(fade!)
      const bounds = effectSpecForSkill('rebase', 'blue').placeBounds!
      expect(bounds).toBeDefined()
      expectVisibleSpriteInsideHost(runtime.animationElements[index], fade![1], bounds, 360, 220)
    } finally {
      runtime.restore()
    }
  })

  it('plays init as gather, orb, projectile, impact, and dissipate phases', async () => {
    const runtime = installAnimationMocks()
    try {
      const layer = document.createElement('div')
      const bodyPoint = { x: 320, y: 150 }
      const feetPoint = { x: 320, y: 210 }
      await effectForSkill('init', 'white')({ layer, from: { x: 90, y: 100 }, to: bodyPoint, impactTo: feetPoint })

      const gather = runtime.animations.find((frames) => frames.length === 3 && frames[1].offset === 0.56)
      const travel = runtime.animations.find((frames) => frames.length === 3 && frames[1].offset === 0.82)
      const dissipate = runtime.animations.find((frames) => frames.length === 3 && frames[1].offset === 0.46)

      expect(gather).toBeDefined()
      expect(travel).toBeDefined()
      expect(dissipate).toBeDefined()

      const metrics = spriteDisplayMetricsForSkill('init', 'white')
      const gatherStart = translateOf(gather![0])
      const gatherEnd = translateOf(gather![2])
      // Charge gathers to the RIGHT of the hand (companion faces right): the orb
      // CENTRE sits one clearance (0.56 of its width) past the hand point (90).
      const chargeCenterX = 90 + metrics.width * 0.56
      expect(gatherStart.x + metrics.width * 0.5).toBeCloseTo(chargeCenterX, 4)
      expect(gatherStart.y + metrics.height * 0.5).toBeCloseTo(100, 4)
      expect(gatherEnd.x + metrics.width * 0.5).toBeCloseTo(chargeCenterX, 4)
      expect(gatherEnd.y + metrics.height * 0.5).toBeCloseTo(100, 4)

      // Travel lands the projectile nose on the body point; only the impact
      // phase pins its base to the ground line.
      const impact = translateOf(travel![1])
      expect(impact.x + metrics.width * 0.78).toBeCloseTo(bodyPoint.x, 4)
      expect(impact.y + metrics.height * 0.52).toBeCloseTo(bodyPoint.y, 4)

      // The impact/dissipate frames pin the pixel-measured placeAnchor onto the
      // ground point, not a fixed 0.86 fraction.
      const pa = effectSpecForSkill('init', 'white').placeAnchor!
      const settle = translateOf(dissipate![0])
      expect(settle.x + metrics.width * pa.x).toBeCloseTo(feetPoint.x, 4)
      expect(settle.y + metrics.height * pa.y).toBeCloseTo(feetPoint.y, 4)
    } finally {
      runtime.restore()
    }
  })

  it('plays clone as a projectile followed by a pinned impact animation', async () => {
    const runtime = installAnimationMocks()
    try {
      const layer = document.createElement('div')
      await effectForSkill('clone', 'black')({ layer, from: { x: 80, y: 96 }, to: { x: 300, y: 144 } })

      expect(effectPlaybackForSkill('clone', 'black')).toBe('projectile')

      const flight = runtime.animations.find((frames) => frames.length === 3 && frames[1].offset === 0.82)
      const impact = runtime.animations.find((frames) => frames.length === 3 && frames[1].offset === 0.42)

      expect(flight).toBeDefined()
      expect(impact).toBeDefined()

      const metrics = spriteDisplayMetricsForSkill('clone', 'black')
      const nose = translateOf(flight![1])
      expect(nose.x + metrics.width * 0.78).toBeCloseTo(300, 4)
      expect(nose.y + metrics.height * 0.52).toBeCloseTo(144, 4)

      const pa = effectSpecForSkill('clone', 'black').placeAnchor!
      const settle = translateOf(impact![0])
      expect(settle.x + metrics.width * pa.x).toBeCloseTo(300, 4)
      expect(settle.y + metrics.height * pa.y).toBeCloseTo(144, 4)
    } finally {
      runtime.restore()
    }
  })

  it('keeps Blue clone travel scale constant, then enlarges only its feet-planted impact', async () => {
    const runtime = installAnimationMocks()
    try {
      const layer = document.createElement('div')
      const bodyPoint = { x: 300, y: 144 }
      const feetPoint = { x: 300, y: 200 }
      await effectForSkill('clone', 'blue')({
        layer,
        from: { x: 80, y: 96 },
        to: bodyPoint,
        impactTo: feetPoint,
        sizeScale: 1.5,
      })

      const flight = runtime.animations.find((frames) => frames.length === 3 && frames[1].offset === 0.82)
      const impact = runtime.animations.find((frames) => frames.length === 3 && frames[1].offset === 0.42)

      expect(flight).toBeDefined()
      expect(impact).toBeDefined()

      const metrics = spriteDisplayMetricsForSkill('clone', 'blue')
      const node = runtime.animationElements[runtime.animations.indexOf(flight!)]
      expect(Number.parseFloat(node.style.width)).toBeCloseTo(metrics.width, 4)
      expect(Number.parseFloat(node.style.height)).toBeCloseTo(metrics.height, 4)
      const nose = translateOf(flight![1])
      expect(nose.x + metrics.width * 0.78).toBeCloseTo(bodyPoint.x, 4)
      expect(nose.y + metrics.height * 0.52).toBeCloseTo(bodyPoint.y, 4)

      const pa = effectSpecForSkill('clone', 'blue').placeAnchor!
      const settle = translateOf(impact![0])
      expect(settle.x + metrics.width * pa.x).toBeCloseTo(feetPoint.x, 4)
      expect(settle.y + metrics.height * pa.y).toBeCloseTo(feetPoint.y, 4)
      expect(scaleOf(impact![0])).toBeCloseTo(1.5, 4)
    } finally {
      runtime.restore()
    }
  })

  it('plays Black add as a gather, projectile, and centered impact motion', async () => {
    const runtime = installAnimationMocks()
    try {
      const layer = document.createElement('div')
      const bodyPoint = { x: 320, y: 150 }
      const impactPoint = { x: 320, y: 210 }
      await effectForSkill('add', 'black')({ layer, from: { x: 90, y: 100 }, to: bodyPoint, impactTo: impactPoint })

      expect(effectPlaybackForSkill('add', 'black')).toBe('projectile')

      const gather = runtime.animations.find((frames) => frames.length === 3 && frames[1].offset === 0.56)
      const travel = runtime.animations.find((frames) => frames.length === 3 && frames[1].offset === 0.82)
      const dissipate = runtime.animations.find((frames) => frames.length === 3 && frames[1].offset === 0.46)

      expect(gather).toBeDefined()
      expect(travel).toBeDefined()
      expect(dissipate).toBeDefined()

      const metrics = spriteDisplayMetricsForSkill('add', 'black')
      const gatherStart = translateOf(gather![0])
      // Charge gathers to the RIGHT of the hand (see the init test for the offset).
      expect(gatherStart.x + metrics.width * 0.5).toBeCloseTo(90 + metrics.width * 0.56, 4)
      expect(gatherStart.y + metrics.height * 0.5).toBeCloseTo(100, 4)

      const impact = translateOf(travel![1])
      expect(impact.x + metrics.width * 0.78).toBeCloseTo(bodyPoint.x, 4)
      expect(impact.y + metrics.height * 0.52).toBeCloseTo(bodyPoint.y, 4)

      // The dissipate frames pin the pixel-measured placeAnchor onto the impact
      // point (Black baked add as a body-centred burst).
      const pa = effectSpecForSkill('add', 'black').placeAnchor!
      const settle = translateOf(dissipate![0])
      expect(settle.x + metrics.width * pa.x).toBeCloseTo(impactPoint.x, 4)
      expect(settle.y + metrics.height * pa.y).toBeCloseTo(impactPoint.y, 4)
    } finally {
      runtime.restore()
    }
  })

  it('settles Blue add on its pixel-measured placeAnchor at the impact point', async () => {
    const runtime = installAnimationMocks()
    try {
      const layer = document.createElement('div')
      const bodyPoint = { x: 760, y: 168 }
      const impactPoint = { x: 760, y: 230 }

      await effectForSkill('add', 'blue')({ layer, from: { x: 90, y: 100 }, to: bodyPoint, impactTo: impactPoint })

      const travel = runtime.animations.find((frames) => frames.length === 3 && frames[1].offset === 0.82)
      const dissipate = runtime.animations.find((frames) => frames.length === 3 && frames[1].offset === 0.46)
      expect(travel).toBeDefined()
      expect(dissipate).toBeDefined()
      const travelNose = translateOf(travel![1])
      const settle = translateOf(dissipate![0])
      const metrics = spriteDisplayMetricsForSkill('add', 'blue')
      // Blue's add IS ground-baked, so its measured anchor sits low in the cell.
      const pa = effectSpecForSkill('add', 'blue').placeAnchor!
      expect(pa.y).toBeGreaterThan(0.5)
      expect(travelNose.x + metrics.width * 0.78).toBeCloseTo(bodyPoint.x, 4)
      expect(travelNose.y + metrics.height * 0.52).toBeCloseTo(bodyPoint.y, 4)
      expect(settle.x + metrics.width * pa.x).toBeCloseTo(impactPoint.x, 4)
      expect(settle.y + metrics.height * pa.y).toBeCloseTo(impactPoint.y, 4)
    } finally {
      runtime.restore()
    }
  })

  it('lands the missed attack splash anchor on the supplied ground point', async () => {
    const runtime = installAnimationMocks()
    try {
      const layer = document.createElement('div')
      await missedAttackForCompanion('white')({ layer, from: { x: 80, y: 90 }, to: { x: 280, y: 180 } })

      const travel = runtime.animations.find((frames) => frames.length === 5 && frames[3].offset === 0.88)
      expect(travel).toBeDefined()
      const impact = translateOf(travel![3])
      const metrics = spriteDisplayMetricsForSkill('miss')
      expect(impact.x + metrics.width * 0.47).toBeCloseTo(280, 4)
      expect(impact.y + metrics.height * 0.7).toBeCloseTo(180, 4)
    } finally {
      runtime.restore()
    }
  })

  it('keeps the legacy missedAttack export on the default companion', async () => {
    const runtime = installAnimationMocks()
    try {
      const layer = document.createElement('div')
      await missedAttack({ layer, from: { x: 80, y: 90 }, to: { x: 280, y: 180 } })

      expect(runtime.animations.some((frames) => frames.length === 5 && frames[3].offset === 0.88)).toBe(true)
    } finally {
      runtime.restore()
    }
  })

  it('mirrors leftward monster projectile sheets without vertical rotation', async () => {
    const runtime = installAnimationMocks()
    try {
      const layer = document.createElement('div')
      const sheet = monsterSheet('projectile')

      await monsterAttackEffect({
        playback: 'projectile',
        durationMs: 300,
        scale: 0.5,
        orientTo: 'travel',
        placement: 'target',
        anchor: 'center',
        layers: [
          { sheet, layer: 'front', scale: 0.5, opacity: 1, offsetX: 0, offsetY: 0, orientTo: 'travel' },
        ],
      })({ layer, from: { x: 300, y: 120 }, to: { x: 120, y: 120 }, targetFacing: 'right' })

      // Monster projectile sheets are authored facing right; leftward shots mirror
      // horizontally so the art stays upright instead of rotating upside down.
      const flight = runtime.animations.find((frames) => frames.length === 3 && frames[1].offset === 0.82)
      expect(flight).toBeDefined()
      expect(String(flight![0].transform)).toContain('scaleX(-1)')
      expect(String(flight![0].transform)).not.toContain('rotate(')
    } finally {
      runtime.restore()
    }
  })

  it('charges rightward monster projectiles toward Blue without mirroring', async () => {
    const runtime = installAnimationMocks()
    try {
      const layer = document.createElement('div')
      const sheet = monsterSheet('projectile')
      const from = { x: 120, y: 120 }

      await monsterAttackEffect({
        playback: 'projectile',
        durationMs: 600,
        scale: 0.6,
        orientTo: 'travel',
        placement: 'target',
        anchor: 'center',
        motion: 'charge',
        layers: [{ sheet, layer: 'front', scale: 0.6, opacity: 1, offsetX: 0, offsetY: 0, orientTo: 'travel' }],
      })({ layer, from, to: { x: 300, y: 120 }, targetFacing: 'right' })

      const gather = runtime.animations.find((frames) => frames.length === 3 && frames[1].offset === 0.56)
      expect(gather).toBeDefined()
      const width = sheet.frameWidth * 0.6
      // Battle monsters stand on the left and shoot toward Blue on the right, so
      // their charge gathers in the travel direction and keeps the right-facing art.
      const gatherCenterX = translateOf(gather![0]).x + width * 0.5
      expect(gatherCenterX).toBeCloseTo(from.x + width * 0.56, 4)
      expect(gatherCenterX).toBeGreaterThan(from.x)
      expect(String(gather![0].transform)).not.toContain('scaleX(-1)')
    } finally {
      runtime.restore()
    }
  })

  it('plays layered monster target sheets behind and in front of the target facing', async () => {
    const runtime = installAnimationMocks()
    try {
      const frontLayer = document.createElement('div')
      frontLayer.dataset.testid = 'front-layer'
      const backLayer = document.createElement('div')
      backLayer.dataset.testid = 'back-layer'

      await monsterAttackEffect({
        playback: 'target',
        durationMs: 300,
        scale: 0.5,
        orientTo: 'target-facing',
        placement: 'target',
        anchor: 'center',
        layers: [
          {
            sheet: monsterSheet('target.back'),
            layer: 'back',
            scale: 0.55,
            opacity: 0.8,
            offsetX: 0,
            offsetY: 10,
            orientTo: 'target-facing',
          },
          {
            sheet: monsterSheet('target.front'),
            layer: 'front',
            scale: 0.5,
            opacity: 1,
            offsetX: 0,
            offsetY: 0,
            orientTo: 'target-facing',
          },
        ],
      })({
        layer: frontLayer,
        backLayer,
        from: { x: 300, y: 120 },
        to: { x: 120, y: 120 },
        targetFacing: 'left',
      })

      expect(runtime.parents).toContain('front-layer')
      expect(runtime.parents).toContain('back-layer')
      expect(runtime.animations.some((frames) => String(frames[0]?.transform).includes('scaleX(-1)'))).toBe(true)
    } finally {
      runtime.restore()
    }
  })

  it('pins monster target effects with measured placeAnchor when available', async () => {
    const runtime = installAnimationMocks()
    try {
      const layer = document.createElement('div')
      const to = { x: 180, y: 150 }

      await monsterAttackEffect({
        playback: 'target',
        durationMs: 300,
        scale: 0.82,
        orientTo: 'target-facing',
        placement: 'target',
        anchor: 'feet',
        placeAnchor: { x: 0.46, y: 0.78 },
        layers: [
          {
            sheet: monsterSheet('measured.target'),
            layer: 'front',
            scale: 0.82,
            opacity: 1,
            offsetX: 0,
            offsetY: 0,
            orientTo: 'target-facing',
          },
        ],
      })({
        layer,
        from: { x: 260, y: 120 },
        to,
        targetFacing: 'right',
      })

      const fade = runtime.animations.find((frames) => frames.length === 4 && frames[1].offset === 0.18)
      expect(fade).toBeDefined()
      const impact = translateOf(fade![1])
      const width = 256 * 0.82
      const height = 256 * 0.82
      expect(impact.x + width * 0.46).toBeCloseTo(to.x, 4)
      expect(impact.y + height * 0.78).toBeCloseTo(to.y, 4)
    } finally {
      runtime.restore()
    }
  })

  it('keeps monster target attack effects inside the stage when the target is edge-pinned', async () => {
    const runtime = installAnimationMocks()
    try {
      const layer = document.createElement('div')
      setHostRect(layer, 300, 180)

      await monsterAttackEffect({
        playback: 'target',
        durationMs: 300,
        scale: 0.74,
        orientTo: 'target-facing',
        placement: 'target',
        anchor: 'center',
        layers: [
          {
            sheet: monsterSheet('two-headed-hound.target'),
            layer: 'front',
            scale: 0.9,
            opacity: 1,
            offsetX: 0,
            offsetY: 0,
            orientTo: 'target-facing',
          },
        ],
      })({
        layer,
        from: { x: 260, y: 120 },
        to: { x: -40, y: 8 },
        targetFacing: 'right',
      })

      const fade = runtime.animations.find((frames) => frames.length === 4 && frames[1].offset === 0.18)
      expect(fade).toBeDefined()
      const index = runtime.animations.indexOf(fade!)
      expectSpriteInsideHost(runtime.animationElements[index], fade![1], 300, 180)
    } finally {
      runtime.restore()
    }
  })
})

function monsterSheet(name: string): SpriteAnimation {
  return {
    name: `monster.${name}`,
    src: `/monster/${name}.png`,
    frameWidth: 256,
    frameHeight: 256,
    columns: 5,
    rows: 5,
    frameCount: 25,
    fps: 18,
    loop: false,
  }
}
