import {
  deriveBattleEventsFromCommandOutcome,
} from '@/shared/battle/deriveBattleEvents'
import type { BattleMonster } from '@/shared/battle/types'
import type { CommandSubmissionOutcome } from '@/shared/level-runtime/commandOutcome'
import { skillForCommand } from '@/shared/level-runtime/commandSkill'

export function battleEventsForSubmittedCommand({
  command,
  outcome,
  monsters,
  fallbackCommandFamily,
  storyWorldSlug,
}: {
  command: string
  outcome: CommandSubmissionOutcome
  monsters: BattleMonster[]
  fallbackCommandFamily?: string | null
  storyWorldSlug?: string | null
}) {
  return deriveBattleEventsFromCommandOutcome({
    outcome,
    skill: skillForCommand(command, outcome.command_family ?? fallbackCommandFamily),
    monsters,
    storyWorldSlug,
  })
}
