import type { ApiSchemas } from '@/shared/api/generated/apiTypes'

export type StatsSummary = ApiSchemas['StatsSummaryResponse']
export type SkillAxis = StatsSummary['skill_profile'][number]
export type TrendPoint = StatsSummary['activity_trend'][number]
/** Which trailing span `activity_trend` covers; only that field answers to it. */
export type ActivityWindow = StatsSummary['activity_window']
