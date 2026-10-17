import type { TierObjective, TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { normalizeLevelContext } from '@/shared/level/utils/levelContext'

/**
 * The one place a tier run becomes Objectives card rows.
 *
 * Tier runs carry no evaluated objective checklist yet, so the level's task is
 * the single objective, done once the run completes (the signal the outcome
 * modal uses). When the run payload gains `objective_checks`, map those rows
 * here; the card only reads {id, text, status}.
 */
export function tierObjectives(run: Pick<TierRun, 'status' | 'scenario_context'>): TierObjective[] {
  const task = normalizeLevelContext(run.scenario_context).task.split('\n\nStarting point:')[0].trim()
  if (!task) return []
  return [{ id: 'task', text: task, status: run.status === 'completed' ? 'done' : 'pending' }]
}
