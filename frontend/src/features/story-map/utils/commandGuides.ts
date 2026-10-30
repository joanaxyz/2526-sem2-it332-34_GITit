import type { CommandIntroduction } from '@/features/story-map/api/commandIntroductionsApi'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'

type GuideSource = Pick<TierRun, 'tutor' | 'command_guides' | 'guide_elsewhere'>

/** Every guide the run can open: the scenario's finished guides, the guide of
 * a command taught in another scenario, and the guide open now, once each. */
export function readableGuides(run: GuideSource): CommandIntroduction[] {
  const guides = [...run.command_guides, run.guide_elsewhere?.guide, run.tutor]
  const byKey = new Map<string, CommandIntroduction>()
  for (const guide of guides) {
    if (guide && !byKey.has(guide.teaching_key)) byKey.set(guide.teaching_key, guide)
  }
  return [...byKey.values()]
}
