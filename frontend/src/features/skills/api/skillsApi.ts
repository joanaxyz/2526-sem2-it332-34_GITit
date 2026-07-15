import type { ApiSchemas } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'
import type { LearnedSkill } from '@/features/skills/types'

export type LearnedSkillsResult = Omit<ApiSchemas['LearnedSkillsResponse'], 'results'> & {
  results: LearnedSkill[]
}

export const skillsApi = {
  listLearned() {
    return apiOperationRequest<'skills_learned_retrieve', LearnedSkillsResult>('skills_learned_retrieve', '/skills/learned/')
  },
}
