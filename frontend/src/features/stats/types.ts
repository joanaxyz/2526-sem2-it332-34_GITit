import type { ApiSchemas } from '@/shared/api/generated/apiTypes'

export type StatsSummary = ApiSchemas['StatsSummaryResponse']
export type SkillAxis = StatsSummary['skill_profile'][number]
export type TrendPoint = StatsSummary['activity_trend'][number]
