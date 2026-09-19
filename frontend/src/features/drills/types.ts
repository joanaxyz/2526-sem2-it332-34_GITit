import type { ApiSchemas } from '@/shared/api/generated/apiTypes'

export type DrillChoice = ApiSchemas['DrillChoice']
export type DrillBlank = ApiSchemas['DrillBlank']
export type DrillCard = ApiSchemas['DrillCard']
export type DrillSequence = ApiSchemas['DrillSequence']
export type DrillProgress = ApiSchemas['DrillProgress']
export type DrillPlan = ApiSchemas['LevelDrillPlanResponse']
export type DrillResume = ApiSchemas['DrillResume']

/**
 * The rungs a card climbs, in ascending production demand. A learner who can
 * only pick the right command from a list has recognition; a learner who can
 * assemble it from loose tokens can write it. The drill exists to move them
 * from the first to the second, so the ladder is the feature.
 */
export type DrillRung = 'recognise' | 'read' | 'complete' | 'forge'

export type DrillAsk =
  | { kind: 'card'; cardKey: string; rung: DrillRung }
  | { kind: 'sequence' }

/** What the learner has committed to, before it is graded. */
export type DrillAnswer =
  | { kind: 'choice'; value: string }
  | { kind: 'tokens'; values: string[] }

export type DrillVerdict = {
  correct: boolean
  /** The authored line that explains what they actually picked, when wrong. */
  pickedGloss: string | null
  picked: string | null
}
