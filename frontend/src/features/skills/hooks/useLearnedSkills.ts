import { useQuery } from '@tanstack/react-query'

import { skillsApi } from '@/features/skills/api/skillsApi'
import { queryKeys } from '@/shared/api/queryKeys'

/** The player's registry of learned commands, for the spellbook UI. */
export function useLearnedSkills() {
  return useQuery({
    queryKey: queryKeys.learnedSkills,
    queryFn: skillsApi.listLearned,
    select: (data) => data.results,
    staleTime: 2 * 60 * 1000,
  })
}
