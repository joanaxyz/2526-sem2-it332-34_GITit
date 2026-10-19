import { useMemo } from 'react'
import { useLearnedSkills } from './useLearnedSkills'
import { knowledgeForMascot, type MascotChapterContext } from '@/features/skills/utils/mascotKnowledge'

export function useMascotKnowledge(chapter?: MascotChapterContext) {
  const { data: skills } = useLearnedSkills()
  const chapterId = chapter?.id
  const chapterNumber = chapter?.number
  return useMemo(() => knowledgeForMascot(skills ?? [], chapterId != null && chapterNumber != null
    ? { id: chapterId, number: chapterNumber } : undefined), [skills, chapterId, chapterNumber])
}
