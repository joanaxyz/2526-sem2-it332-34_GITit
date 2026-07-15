// Build the companion skill-showcase index consumed by the Shop.
//
// The spell processor (process_companion_spell_sheets.py) emits one aligned
// sheet per git command that has raw art, plus a manifest listing them. Not
// every companion has every command yet, so the manifest can still name sheets
// that were never generated. This script is the source of truth for "which
// skill sheets actually exist on disk", pairing each real sheet with the
// manifest metadata the Shop needs to animate and label it.
//
// Output: frontend/src/shared/cosmetics/companions/data/companion-skills.json

import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const here = dirname(fileURLToPath(import.meta.url))
// here = scripts/assets → repo root is two levels up.
const ROOT = resolve(here, '..', '..')
const PUBLIC = resolve(ROOT, 'frontend', 'public')
const OUT = resolve(
  ROOT,
  'frontend',
  'src',
  'shared',
  'cosmetics',
  'companions',
  'data',
  'companion-skills.json',
)

const EFFECT_ROOTS = {
  blue: '/cosmetics/companion/blue/effects/skill-flames-25',
  white: '/cosmetics/companion/white/effects/skill-ice-25',
  black: '/cosmetics/companion/black/effects/skill-lightning-25',
}

// Not player-facing skills: keep them out of the showcase.
const EXCLUDE = new Set(['default', 'miss'])

// Rough git-workflow order so the showcase reads as a progression rather than
// manifest insertion order. Unknown families sort after these, alphabetically.
const ORDER = [
  'init', 'clone', 'config', 'status', 'log', 'show', 'diff', 'add', 'commit',
  'rm', 'restore', 'reset', 'revert', 'stash', 'branch', 'switch', 'checkout',
  'merge', 'merge-base', 'rebase', 'cherry-pick', 'reflog', 'check-ignore',
  'ls-files', 'checkout-conflict', 'diff-conflict', 'mergetool',
  'remote', 'fetch', 'pull', 'push',
]

function orderIndex(name) {
  const i = ORDER.indexOf(name)
  return i === -1 ? ORDER.length : i
}

const index = {}
for (const [slug, effectRoot] of Object.entries(EFFECT_ROOTS)) {
  const manifestPath = resolve(PUBLIC, `.${effectRoot}`, 'manifest.json')
  if (!existsSync(manifestPath)) continue
  const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'))
  const sprites = manifest.sprites ?? {}
  const entries = []
  for (const [name, entry] of Object.entries(sprites)) {
    if (EXCLUDE.has(name)) continue
    // Layered effects have no `<name>.png`; their still points at `<name>_front.png`.
    // Verify the representative sheet named in the manifest actually exists.
    const sheetPath = resolve(PUBLIC, `.${String(entry.src)}`)
    if (!existsSync(sheetPath)) continue
    const record = {
      family: name,
      command: String(entry.baseCommand ?? `git ${name}`),
      tint: String(entry.tint ?? 'cyan'),
      playback: String(entry.playback ?? 'target'),
      anchor: String(entry.anchor ?? 'center'),
      sheet: {
        src: String(entry.src),
        frameWidth: Number(entry.frameWidth),
        frameHeight: Number(entry.frameHeight),
        columns: Number(entry.columns),
        rows: Number(entry.rows),
        frameCount: Number(entry.frameCount),
        fps: Number(entry.fps),
      },
    }
    if (entry.motion) record.motion = String(entry.motion)
    if (entry.launchStartFrame != null) record.launchStartFrame = Number(entry.launchStartFrame)
    if (entry.impactStartFrame != null) record.impactStartFrame = Number(entry.impactStartFrame)
    if (Array.isArray(entry.layers)) {
      record.layers = entry.layers.map((l) => ({ layer: String(l.layer), src: String(l.src) }))
    }
    entries.push(record)
  }
  entries.sort((a, b) => orderIndex(a.family) - orderIndex(b.family) || a.family.localeCompare(b.family))
  index[slug] = entries
}

writeFileSync(OUT, `${JSON.stringify(index, null, 2)}\n`, 'utf8')
const summary = Object.entries(index)
  .map(([slug, list]) => `${slug}: ${list.length}`)
  .join(', ')
console.log(`Wrote ${OUT}\n  ${summary}`)
