import type { DrillPlan } from '@/features/drills/types'

import plan from './drillPlan.json'

/**
 * A real seeded drill, frozen: Chapter 1's staging-and-committing level,
 * exported straight from `level_drill_payload` so the playground exercises
 * the shapes the API actually sends - six cards with different ladders, a
 * blank-bearing card, and the closing ordering question.
 *
 * Dev-only, like the page that uses it: `import.meta.env.DEV` compiles
 * both away in a production build.
 */
export const DRILL_PLAN_FIXTURE = plan as unknown as DrillPlan
