import type { LevelScenarioContext } from '@/shared/level/types'

export type NormalizedLevelContext = {
  story: string
  startingPoint: string
  realWorldContext: string
  task: string
  objectiveChecks: string[]
  expectedResult: string
  details: { label: string; value: string }[]
}

/** Flatten a schema_version 3 scenario context into the fields the workspace renders. */
export function normalizeLevelContext(
  context?: LevelScenarioContext | null,
): NormalizedLevelContext {
  return {
    story: cleanText(context?.story),
    startingPoint: cleanText(context?.starting_point),
    realWorldContext: cleanText(context?.real_world_context),
    task: cleanText(context?.task),
    objectiveChecks: (context?.objective_checks ?? []).map(cleanText).filter(Boolean),
    expectedResult: cleanText(context?.expected_result),
    details: (context?.details ?? [])
      .map((item) => ({ label: cleanText(item.label), value: cleanText(item.value) }))
      .filter((item) => item.value),
  }
}

function cleanText(value?: string) {
  return (value ?? '').trim()
}
