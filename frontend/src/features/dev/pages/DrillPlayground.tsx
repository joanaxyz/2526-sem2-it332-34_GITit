import { DrillSession } from '@/features/drills/components/DrillSession'
import { DRILL_PLAN_FIXTURE } from '@/features/dev/fixtures/drillPlan'

/**
 * Squire's Drill on fixture content, with no auth and no level gate.
 *
 * The real drill route needs an account that has actually unlocked the
 * level, which makes iterating on the screen slow and makes the states
 * that matter most - a miss, an exhausted card, the finished track -
 * hard to reach on purpose. This runs the real components against a real
 * seeded plan instead.
 *
 * The session's checkpoint and report calls will fail here (there is no
 * session cookie); that is deliberate and harmless - both are
 * fire-and-forget, and the failure surfaces the summary's
 * "could not be saved" notice, which is otherwise hard to see.
 */
export default function DrillPlayground() {
  return <DrillSession plan={DRILL_PLAN_FIXTURE} />
}

export const Component = DrillPlayground
