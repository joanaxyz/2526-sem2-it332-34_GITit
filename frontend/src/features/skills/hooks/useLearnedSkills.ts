import { useQuery } from '@tanstack/react-query'

import { learnedSkillsQueryOptions } from '@/features/skills/api/skillsApi'

/** The player's registry of learned commands, for the spellbook UI. */
export function useLearnedSkills() {
  return useQuery({
    ...learnedSkillsQueryOptions(),
    select: (data) => data.results,
  })
}
