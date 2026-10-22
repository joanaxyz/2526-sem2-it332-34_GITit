import { normalizeLevelContext } from '@/shared/level/utils/levelContext'
import type { WorkspaceRun } from '@/shared/level/workspace/types'

type WorkspaceStoryContent = {
  title: string
  intro: string
  startingPoint: string
  realWorldContext: string
  task: string
  expectedResult: string
  /** Exact literals the learner must type (clone URL, commit message...). */
  requiredValues: { label: string; value: string }[]
}

/**
 * Split a run's scenario context into what the workspace shows.
 *
 * Legacy content puts the case-specific narrative in the first unlabeled
 * detail; the generic story is the fallback. Every other detail is an exact,
 * copyable value. `fallbackTitle` names the level when the variant has no label.
 */
export function workspaceStoryContent(
  run: Pick<WorkspaceRun, 'scenario_context' | 'variant'>,
  fallbackTitle: string,
): WorkspaceStoryContent {
  const context = normalizeLevelContext(run.scenario_context)
  const narrativeIndex = context.details.findIndex((detail) => !detail.label)
  let intro = narrativeIndex >= 0 ? context.details[narrativeIndex].value : context.story
  let task = context.task
  let startingPoint = context.startingPoint

  // Older saved payloads embedded the starting point at the end of either the
  // narrative or task. Promote it into the explicit field without duplicating
  // it when the variant has already been reseeded with the revised contract.
  const marker = '\n\nStarting point:'
  const introMarker = intro.lastIndexOf(marker)
  if (introMarker >= 0) {
    startingPoint ||= intro.slice(introMarker + marker.length).trim()
    intro = intro.slice(0, introMarker).trimEnd()
  }
  const taskMarker = task.lastIndexOf(marker)
  if (taskMarker >= 0) {
    startingPoint ||= task.slice(taskMarker + marker.length).trim()
    task = task.slice(0, taskMarker).trimEnd()
  }

  return {
    title: run.variant?.label?.trim() || fallbackTitle,
    intro,
    startingPoint,
    realWorldContext: context.realWorldContext,
    task,
    expectedResult: context.expectedResult,
    requiredValues: context.details.filter((_, index) => index !== narrativeIndex),
  }
}
