import {
  deriveBattleEventsFromCommandOutcome,
  skillForCommand,
} from '@/shared/battle/deriveBattleEvents'
import type { BattleMonster, CommandSubmissionOutcome } from '@/shared/battle/types'

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
