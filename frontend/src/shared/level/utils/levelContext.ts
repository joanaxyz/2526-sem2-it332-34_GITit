import type { LevelScenarioContext } from '@/shared/level/types'

export type ObjectiveCheck = { label: string; satisfied: boolean }

export type NormalizedLevelContext = {
  story: string
  realWorldContext: string
  task: string
  details: { label: string; value: string }[]
}

/** Flatten a schema_version 3 scenario context into the fields the story card renders. */
export function normalizeLevelContext(
  context?: LevelScenarioContext | null,
): NormalizedLevelContext {
  return {
    story: cleanText(context?.story),
    realWorldContext: cleanText(context?.real_world_context),
    task: cleanText(context?.task),
    details: (context?.details ?? [])
      .map((item) => ({ label: cleanText(item.label), value: cleanText(item.value) }))
      .filter((item) => item.value),
  }
}

/** True when the normalized context carries any learner-facing detail. */
export function hasLevelContext(context: NormalizedLevelContext) {
  return Boolean(context.story || context.realWorldContext || context.task || context.details.length)
}

function cleanText(value?: string) {
  return (value ?? '').trim()
}
