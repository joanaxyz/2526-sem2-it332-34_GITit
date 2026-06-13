import { apiRequest } from '@/shared/api/httpClient'
import type { LearnedSkill } from '@/features/skills/types'

export const skillsApi = {
  listLearned() {
    return apiRequest<{ results: LearnedSkill[] }>('/skills/learned/')
  },
}
