import type { SpriteAnimation } from '@/shared/sprites/types'
import { DEFAULT_SKILL_COMPANION, SKILL_EFFECT_ROOTS } from '@/shared/cosmetics/skillPortrait'
import { companionPlacementGeometry } from '@/shared/cosmetics/companions/companionSkills'
import { skillElementForCompanion } from '@/shared/audio/battleAudio'

import type { SkillSpriteSpec } from './types'

const FRAME = 256
const COLUMNS = 5
const ROWS = 5
const FRAME_COUNT = 25
const FPS = 18
const DEFAULT_EFFECT_COMPANION = DEFAULT_SKILL_COMPANION
const EFFECT_ROOTS = SKILL_EFFECT_ROOTS
/** Families the processor split into back/front depth sheets, per companion. */
const LAYERED_FAMILIES: Record<string, ReadonlySet<string>> = {
  blue: new Set<string>(),
  white: new Set<string>(),
  black: new Set(['cherry-pick', 'merge-base', 'remote']),
}

function layeredSheets(name: string, companionSlug: string): { back: SpriteAnimation; front: SpriteAnimation } {
  return { back: sheet(`${name}_back`, companionSlug), front: sheet(`${name}_front`, companionSlug) }
}

function companionEffectSlug(companionSlug?: string | null): string {
  return companionSlug?.trim().toLowerCase() || DEFAULT_EFFECT_COMPANION
}

function effectRootForCompanion(companionSlug: string): string {
  return EFFECT_ROOTS[companionSlug] ?? EFFECT_ROOTS[DEFAULT_EFFECT_COMPANION]
}

function sheet(name: string, companionSlug = DEFAULT_EFFECT_COMPANION, rootOverride?: string): SpriteAnimation {
  const owner = companionEffectSlug(companionSlug)
  return {
    name: `${owner}.skill.${name}`,
    src: `${rootOverride ?? effectRootForCompanion(owner)}/${name}.png`,
    frameWidth: FRAME,
    frameHeight: FRAME,
    columns: COLUMNS,
    rows: ROWS,
    frameCount: FRAME_COUNT,
    fps: FPS,
    loop: false,
  }
}

const PROJECTILE_SCALE = 0.54
const TARGET_SCALE = 0.66

// Authoritative playback buckets from the visual sheet audit READMEs:
//   projectile: add, branch, checkout, clone, default, init, merge, reflog,
//       stash, diff  - launch from the hand, fly out, impact the monster, then
//       play the impact/dissipate frames pinned at the hit point.
//   ground: push, switch - planted on the floor, run along it to the monster.
//   target: everything else - plays on the monster. `anchor` splits these into
//       'center' (an aura/burst baked to cell centre, planted on the body) and
//       'feet' (a ground-rooted riser, planted on the monster's ground line).
//       Keep each `anchor` in sync with process_companion_spell_sheets.py.
//       The `launchStartFrame`/`impactStartFrame` values are zero-based sheet
//       phase boundaries derived from frame-numbered audits of the generated art.
function buildEffects(companionSlug = DEFAULT_EFFECT_COMPANION): Record<string, SkillSpriteSpec> {
  const slug = companionEffectSlug(companionSlug)
  const element = skillElementForCompanion(slug)
  const effects: Record<string, SkillSpriteSpec> = {
    init: {
      sheet: sheet('init', companionSlug),
      playback: 'projectile',
      tint: 'cyan',
      scale: PROJECTILE_SCALE,
      durationMs: 760,
      motion: 'gather-orb-projectile-impact-dissipate',
      anchor: 'feet',
      launchStartFrame: 10,
      impactStartFrame: 15,
    },
    clone: {
      sheet: sheet('clone', companionSlug),
      playback: 'projectile',
      anchor: 'feet',
      tint: 'azure',
      scale: 0.62,
      durationMs: 820,
      impactStartFrame: 15,
    },
    status: { sheet: sheet('status', companionSlug), playback: 'target', anchor: 'center', tint: 'steel', scale: 0.62, durationMs: 860 },
    config: { sheet: sheet('config', companionSlug), playback: 'target', anchor: 'center', tint: 'indigo', scale: TARGET_SCALE, durationMs: 900 },
    log: { sheet: sheet('log', companionSlug), playback: 'target', anchor: 'center', tint: 'steel', scale: 0.62, durationMs: 900 },
    show: { sheet: sheet('show', companionSlug), playback: 'target', anchor: 'feet', tint: 'azure', scale: TARGET_SCALE, durationMs: 900 },
    diff: { sheet: sheet('diff', companionSlug), playback: 'projectile', tint: 'cyan', scale: 0.56, durationMs: 780, impactStartFrame: 15 },
    add: {
      sheet: sheet('add', companionSlug),
      playback: 'projectile',
      tint: 'cyan',
      scale: PROJECTILE_SCALE,
      durationMs: 760,
      motion: 'gather-orb-projectile-impact-dissipate',
      anchor: 'feet',
      launchStartFrame: 3,
      impactStartFrame: 16,
    },
    commit: { sheet: sheet('commit', companionSlug), playback: 'target', anchor: 'feet', tint: 'azure', scale: TARGET_SCALE, durationMs: 980 },
    rm: { sheet: sheet('rm', companionSlug), playback: 'projectile', tint: 'steel', scale: PROJECTILE_SCALE, durationMs: 760, impactStartFrame: 16 },
    'check-ignore': { sheet: sheet('check-ignore', companionSlug), playback: 'target', anchor: 'feet', tint: 'ash', scale: 0.62, durationMs: 860 },
    restore: { sheet: sheet('restore', companionSlug), playback: 'target', anchor: 'feet', tint: 'cyan', scale: TARGET_SCALE, durationMs: 900 },
    branch: { sheet: sheet('branch', companionSlug), playback: 'projectile', anchor: 'feet', tint: 'cyan', scale: PROJECTILE_SCALE, durationMs: 780, impactStartFrame: 19 },
    switch: { sheet: sheet('switch', companionSlug), playback: 'ground', tint: 'cyan', scale: 0.62, durationMs: 820 },
    checkout: { sheet: sheet('checkout', companionSlug), playback: 'projectile', tint: 'steel', scale: 0.52, durationMs: 680, impactStartFrame: 16 },
    merge: { sheet: sheet('merge', companionSlug), playback: 'projectile', tint: 'cyan', scale: 0.6, durationMs: 860, impactStartFrame: 20 },
    'merge-base': { sheet: sheet('merge-base', companionSlug), playback: 'target', anchor: 'feet', tint: 'indigo', scale: TARGET_SCALE, durationMs: 900 },
    'checkout-conflict': {
      sheet: sheet('checkout-conflict', companionSlug),
      playback: 'target',
      anchor: 'center',
      tint: 'steel',
      scale: TARGET_SCALE,
      durationMs: 960,
    },
    'diff-conflict': { sheet: sheet('diff-conflict', companionSlug), playback: 'target', anchor: 'feet', tint: 'cyan', scale: TARGET_SCALE, durationMs: 920 },
    'ls-files': { sheet: sheet('ls-files', companionSlug), playback: 'target', anchor: 'feet', tint: 'steel', scale: TARGET_SCALE, durationMs: 900 },
    mergetool: { sheet: sheet('mergetool', companionSlug), playback: 'target', anchor: 'center', tint: 'azure', scale: 0.62, durationMs: 920 },
    reset: { sheet: sheet('reset', companionSlug), playback: 'target', anchor: 'feet', tint: 'steel', scale: TARGET_SCALE, durationMs: 900 },
    revert: { sheet: sheet('revert', companionSlug), playback: 'target', anchor: 'center', tint: 'indigo', scale: TARGET_SCALE, durationMs: 940 },
    reflog: { sheet: sheet('reflog', companionSlug), playback: 'projectile', tint: 'violet', scale: PROJECTILE_SCALE, durationMs: 820, impactStartFrame: 16 },
    stash: { sheet: sheet('stash', companionSlug), playback: 'projectile', tint: 'violet', scale: PROJECTILE_SCALE, durationMs: 780, impactStartFrame: 15 },
    'cherry-pick': { sheet: sheet('cherry-pick', companionSlug), playback: 'target', anchor: 'feet', tint: 'azure', scale: TARGET_SCALE, durationMs: 980 },
    remote: { sheet: sheet('remote', companionSlug), playback: 'target', anchor: 'feet', tint: 'steel', scale: TARGET_SCALE, durationMs: 900 },
    fetch: { sheet: sheet('fetch', companionSlug), playback: 'target', anchor: 'center', tint: 'steel', scale: TARGET_SCALE, durationMs: 920 },
    pull: { sheet: sheet('pull', companionSlug), playback: 'target', anchor: 'feet', tint: 'azure', scale: TARGET_SCALE, durationMs: 900 },
    push: { sheet: sheet('push', companionSlug), playback: 'ground', tint: 'steel', scale: 0.54, durationMs: 840 },
    rebase: { sheet: sheet('rebase', companionSlug), playback: 'target', anchor: 'feet', tint: 'indigo', scale: 0.64, durationMs: 940 },
    tag: { sheet: sheet('tag', companionSlug), playback: 'target', anchor: 'feet', tint: 'indigo', scale: TARGET_SCALE, durationMs: 900 },
    'rev-list': { sheet: sheet('rev-list', companionSlug), playback: 'target', anchor: 'center', tint: 'violet', scale: 0.62, durationMs: 900 },
    default: { sheet: sheet('default', companionSlug), playback: 'projectile', tint: 'cyan', scale: PROJECTILE_SCALE, durationMs: 740, impactStartFrame: 15 },
    miss: { sheet: sheet('miss', companionSlug), playback: 'miss', tint: 'ash', scale: 0.56, durationMs: 760 },
  }

  if (slug === 'black') {
    effects.init = { ...effects.init, tint: 'violet', durationMs: 820 }
    effects.clone = { ...effects.clone, anchor: 'center' }
    effects.init = { ...effects.init, launchStartFrame: 8, impactStartFrame: 14 }
    effects.diff = { ...effects.diff, impactStartFrame: 14 }
    effects.add = { ...effects.add, anchor: 'center', launchStartFrame: 3, impactStartFrame: 18 }
    effects.rm = { ...effects.rm, impactStartFrame: 17 }
    effects.branch = { ...effects.branch, anchor: 'center', impactStartFrame: 19 }
    effects.checkout = { ...effects.checkout, impactStartFrame: 17 }
  } else if (slug === 'white') {
    effects.init = { ...effects.init, tint: 'azure', durationMs: 820 }
    effects.clone = { ...effects.clone, anchor: 'center' }
    effects.diff = { ...effects.diff, impactStartFrame: 20 }
    effects.add = { ...effects.add, anchor: 'center', launchStartFrame: 10, impactStartFrame: 15 }
    effects.branch = { ...effects.branch, anchor: 'center', impactStartFrame: 17 }
    effects.checkout = { ...effects.checkout, impactStartFrame: 20 }
    effects.merge = { ...effects.merge, anchor: 'feet', impactStartFrame: 18 }
    effects['ls-files'] = { ...effects['ls-files'], anchor: 'center' }
    effects.stash = { ...effects.stash, anchor: 'feet', impactStartFrame: 13 }
  } else if (slug === 'blue') {
    effects.add = { ...effects.add, launchStartFrame: 3, impactStartFrame: 16 }
  }

  // Inject the depth-split sheets for the effects this companion authored as
  // back/front. The single-sheet still (used for previews) points at the front.
  for (const family of LAYERED_FAMILIES[slug] ?? []) {
    const spec = effects[family]
    if (!spec) continue
    const layers = layeredSheets(family, slug)
    effects[family] = { ...spec, layers, sheet: layers.front }
  }

  // Attach the pixel-measured placement anchors emitted by the spell processor.
  // The runtime pins these on the target instead of the fixed FEET/CENTER
  // fraction, so placement follows the actual baked pixels and survives a
  // reprocess that shifts art within its transparent cell. Families the index
  // omits (default/miss) keep the constant-anchor fallback.
  const placementGeometry = companionPlacementGeometry(slug)
  for (const key of Object.keys(effects)) {
    const measured = placementGeometry[key]
    effects[key] = {
      ...effects[key],
      element,
      ...(measured?.anchor ? { placeAnchor: measured.anchor } : {}),
      ...(measured?.bounds ? { placeBounds: measured.bounds } : {}),
    }
  }

  return effects
}

const EFFECTS_CACHE = new Map<string, Record<string, SkillSpriteSpec>>()

export function effectsForCompanion(companionSlug?: string | null): Record<string, SkillSpriteSpec> {
  const owner = companionEffectSlug(companionSlug)
  const cached = EFFECTS_CACHE.get(owner)
  if (cached) return cached
  const effects = buildEffects(owner)
  EFFECTS_CACHE.set(owner, effects)
  return effects
}

export function effectSpecForSkill(skill: string, companionSlug?: string | null): SkillSpriteSpec {
  const effects = effectsForCompanion(companionSlug)
  return effects[skill.toLowerCase()] ?? effects.default
}
