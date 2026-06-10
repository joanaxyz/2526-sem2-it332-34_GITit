import type { PracticeScenarioContext } from '@/shared/practice/types'

export type ObjectiveCheck = { label: string; satisfied: boolean }

export type NormalizedPracticeContext = {
  story: string
  task: string
  details: { label: string; value: string }[]
  constraints: string[]
}

/** Flatten a schema_version 3 scenario context into the fields the brief renders. */
export function normalizePracticeContext(
  context?: PracticeScenarioContext | null,
): NormalizedPracticeContext {
  return {
    story: cleanText(context?.story),
    task: cleanText(context?.task),
    details: (context?.details ?? [])
      .map((item) => ({ label: cleanText(item.label), value: cleanText(item.value) }))
      .filter((item) => item.label && item.value),
    constraints: cleanList(context?.constraints),
  }
}

/** True when the normalized context carries any learner-facing detail. */
export function hasPracticeContext(context: NormalizedPracticeContext) {
  return Boolean(
    context.story || context.task || context.details.length || context.constraints.length,
  )
}

function cleanList(values?: string[]) {
  return (values ?? []).map(cleanText).filter(Boolean)
}

function cleanText(value?: string) {
  return (value ?? '').trim()
}
