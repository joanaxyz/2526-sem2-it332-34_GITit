import type { TierObjective, TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { normalizeLevelContext } from '@/shared/level/utils/levelContext'

/**
 * The one place a tier run becomes Objectives card rows.
 *
 * The scenario's authored checklist is learner-facing briefing content. Until
 * the evaluator reports per-row progress, rows complete together with the run.
 * Legacy scenarios without a checklist keep the task as their single row.
 */
export function tierObjectives(run: Pick<TierRun, 'status' | 'scenario_context'>): TierObjective[] {
  const context = normalizeLevelContext(run.scenario_context)
  const legacyTask = context.task.split('\n\nStarting point:')[0].trim()
  const status = run.status === 'completed' ? 'done' : 'pending'
  if (!context.objectiveChecks.length) {
    return legacyTask ? [{ id: 'task', text: legacyTask, status }] : []
  }
  return context.objectiveChecks.map((text, index) => ({
    id: `objective-${index + 1}`,
    text,
    status,
  }))
}
