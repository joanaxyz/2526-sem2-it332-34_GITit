import { queryOptions } from '@tanstack/react-query'

import type { ApiSchemas } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'
import { queryKeys } from '@/shared/api/queryKeys'
import type { LearnedSkill } from '@/features/skills/types'

export type LearnedSkillsResult = Omit<ApiSchemas['LearnedSkillsResponse'], 'results'> & {
  results: LearnedSkill[]
}

export const skillsApi = {
  listLearned() {
    return apiOperationRequest<'skills_learned_retrieve', LearnedSkillsResult>('skills_learned_retrieve', '/skills/learned/')
  },
}

/** Shared by the spellbook hook and the loaders that prefetch it. */
export function learnedSkillsQueryOptions() {
  return queryOptions({
    queryKey: queryKeys.learnedSkills,
    queryFn: skillsApi.listLearned,
    staleTime: 2 * 60 * 1000,
  })
}
