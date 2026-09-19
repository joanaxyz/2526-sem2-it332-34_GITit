import { effectSpecForSkill } from '@/shared/battle/effects/skill-effects/catalog'
import { definitionForMonster } from '@/shared/battle/monsterDescriptors'
import { stageParallaxUrl } from '@/shared/battle/stageBackdrop'
import type { BattleStage } from '@/shared/battle/types'
import { getCompanion } from '@/shared/cosmetics/companions/registry'
import { companionBattleFromDef, companionFromDef } from '@/shared/cosmetics/companionRuntime'
import { isImageWarm, warmImages, warmSprite, withBudget } from '@/shared/sprites/preload'
import type { SpriteAnimation } from '@/shared/sprites/types'
import { monsterSkin } from '@/shared/story-worlds/registry'
import type { StoryWorldDef } from '@/shared/story-worlds/types'

/**
 * Every image one encounter can paint, split by what the stage needs from it.
 *
 * `anchored` sheets are measured as well as decoded: the actors that render them
 * align visible pixels instead of the transparent frame box, so a late
 * measurement moves them after they are already on screen.
 */
export type BattleAssetManifest = {
  anchored: SpriteAnimation[]
  images: string[]
}

/** The fallback family any unrecognized command casts, whatever the level teaches. */
const ALWAYS_WARM_SKILLS = ['default']

export type BattleAssetInput = {
  storyWorld: StoryWorldDef
  stage?: BattleStage | null
  companionSlug: string
  /** Catalog monster ids the encounter can stage. */
  species: string[]
  /** Command families the level teaches, as `git-commit` or `commit`. */
  skillSlugs?: string[]
}

/** Everything an encounter paints: backdrop, companion, foes, and spell art. */
export function battleAssetManifest(input: BattleAssetInput): BattleAssetManifest {
  const anchored: SpriteAnimation[] = []
  const images: string[] = []

  const backdrop = stageParallaxUrl(input.storyWorld, input.stage)
  if (backdrop) images.push(backdrop)

  const companion = getCompanion(input.companionSlug)
  const locomotion = companionFromDef(companion)
  if (locomotion) {
    // PlayerActor and the loading screen both pin these to measured pixels.
    anchored.push(locomotion.sprites.idle, locomotion.sprites.run)
    for (const fidget of locomotion.randoms) images.push(fidget.src)
  }
  const companionBattle = companionBattleFromDef(companion)
  if (companionBattle) {
    for (const sheet of Object.values(companionBattle)) images.push(sheet.src)
  }
  const companionPortrait = companion.sprites.portrait ?? companion.sprites.idle
  if (companionPortrait) images.push(companionPortrait.src)

  for (const sheet of skillSheets(input.skillSlugs ?? [], input.companionSlug)) {
    images.push(sheet.src)
  }

  for (const monster of input.species) {
    collectMonsterArt(input.storyWorld, monster, anchored, images)
  }

  return finalize(anchored, images)
}

/** The foes a wave is about to stage, without the rest of the encounter. */
export function monsterAssetManifest(
  storyWorld: StoryWorldDef,
  species: string[],
): BattleAssetManifest {
  const anchored: SpriteAnimation[] = []
  const images: string[] = []
  for (const monster of species) collectMonsterArt(storyWorld, monster, anchored, images)
  return finalize(anchored, images)
}

/** True once every image in the manifest has already been decoded this session. */
export function battleAssetsWarm(manifest: BattleAssetManifest): boolean {
  return (
    manifest.images.every((src) => isImageWarm(src)) &&
    manifest.anchored.every((sheet) => isImageWarm(sheet.src))
  )
}

/**
 * Decode a manifest, resolving when it is warm or the budget runs out. The
 * anchored sheets are measured first: they place the actors, so a surface that
 * gives up early still paints them where they belong.
 */
export function warmBattleAssets(
  manifest: BattleAssetManifest,
  options: { timeoutMs?: number } = {},
): Promise<void> {
  if (battleAssetsWarm(manifest)) return Promise.resolve()
  const work = Promise.all([
    ...manifest.anchored.map((sheet) => warmSprite(sheet, { measureAnchor: true })),
    warmImages(manifest.images),
  ]).then(() => undefined)
  return withBudget(work, options.timeoutMs)
}

function collectMonsterArt(
  storyWorld: StoryWorldDef,
  species: string,
  anchored: SpriteAnimation[],
  images: string[],
): void {
  const skin = monsterSkin(storyWorld, species)
  if (!skin) return
  // Built through the same descriptor MonsterActor renders, so the measured
  // pixel anchor lands under the exact cache key the actor will ask for.
  const definition = definitionForMonster(
    { id: 0, species, hp: 1, max_hp: 1, alive: true },
    skin,
  )
  anchored.push(definition.sprites.idle)
  for (const [action, sheet] of Object.entries(definition.sprites)) {
    if (action !== 'idle') images.push(sheet.src)
  }
  if (definition.portrait) images.push(definition.portrait)
  if (definition.attack.kind === 'projectile' && definition.attack.sheet) {
    images.push(definition.attack.sheet.src)
  }
  for (const layer of definition.attack.effect?.layers ?? []) images.push(layer.sheet.src)
}

function skillSheets(skillSlugs: string[], companionSlug: string): SpriteAnimation[] {
  const families = [...skillSlugs.map(effectFamily), ...ALWAYS_WARM_SKILLS]
  return families.flatMap((family) => {
    const spec = effectSpecForSkill(family, companionSlug)
    // Depth-split families ship as back/front pairs; `sheet` points at the front.
    return spec.layers ? [spec.layers.back, spec.layers.front] : [spec.sheet]
  })
}

/**
 * The effect-sheet family behind a curriculum skill slug: the backend names a
 * command skill `git-cherry-pick`, the spell sheets name it `cherry-pick`.
 */
function effectFamily(skillSlug: string): string {
  return skillSlug.trim().toLowerCase().replace(/^git[\s-]+/, '') || 'default'
}

/**
 * One entry per image. Sheets collected as fall-throughs (a monster with no
 * walk pose reuses its idle) and sheets shared between the two lists would
 * otherwise be claimed twice; an anchored sheet always wins, since it needs the
 * measurement as well as the decode.
 */
function finalize(anchored: SpriteAnimation[], images: string[]): BattleAssetManifest {
  const claimed = new Set<string>()
  const sheets = anchored.filter((sheet) => {
    if (!sheet.src || claimed.has(sheet.src)) return false
    claimed.add(sheet.src)
    return true
  })
  const sources = images.filter((src) => {
    if (!src || claimed.has(src)) return false
    claimed.add(src)
    return true
  })
  return { anchored: sheets, images: sources }
}
