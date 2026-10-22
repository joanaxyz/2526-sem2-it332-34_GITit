import { DrillSession } from '@/features/drills/components/DrillSession'
import { DRILL_PLAN_FIXTURE } from '@/features/dev/utils/drillPlan'
import type { DrillPlan } from '@/features/drills/types'

const CHECKPOINT_PLAN: DrillPlan = {
  ...DRILL_PLAN_FIXTURE,
  resume: null,
  sequence: null,
  cards: [{
    key: 'checkpoint-init', command: 'git init -b main', intent: 'Initialize a repository with main as its first branch.',
    base_command: 'git init', summary: '', tokens: ['git', 'init', '-b', 'main'],
    bank: ['main', 'git', '-b', 'init'], command_choices: [], intent_choices: [], blank: null,
  }],
}

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
  const plan = new URLSearchParams(window.location.search).has('checkpoint') ? CHECKPOINT_PLAN : DRILL_PLAN_FIXTURE
  return <DrillSession plan={plan} />
}

export const Component = DrillPlayground
