import type { AdventureRun } from '@/features/adventures/types'
import {
  adventureEncounterSpecies,
  adventureStoryWorld,
} from '@/features/adventures/utils/adventureEncounter'
import { battleAssetManifest } from '@/shared/battle/battleAssets'
import type { BattleAssetManifest } from '@/shared/battle/battleAssets'

/**
 * Every image the first frame of this level will paint: the chapter backdrop,
 * the equipped companion, the foe this wave stages, and the spell sheets for the
 * commands the level teaches. Null when the run has no attempt to play, so a
 * finished run's outcome modal is never held behind art it will not show.
 */
export function adventureLevelAssetManifest(
  run: AdventureRun,
  companionSlug: string,
): BattleAssetManifest | null {
  const attempt = run.current_attempt
  if (!attempt) return null

  const storyWorld = adventureStoryWorld(run)
  const species = adventureEncounterSpecies({
    runId: run.id,
    attemptId: attempt.id,
    wave: attempt.wave,
    totalWaves: run.total_waves,
    maxHp: attempt.command_budget.max_counted_commands,
    storyWorld,
  })

  return battleAssetManifest({
    storyWorld,
    stage: run.battle_stage,
    companionSlug,
    species,
    // Mastery lists one row per command form; several forms share a skill, and
    // the manifest de-duplicates the sheets they resolve to.
    skillSlugs: run.mastery.commands.map((command) => command.skill_slug),
  })
}
