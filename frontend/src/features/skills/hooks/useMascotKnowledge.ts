import { useMemo } from 'react'
import { useLearnedSkills } from './useLearnedSkills'
import {
  knowledgeForMascot,
  type MascotChapterContext,
  type MascotMapContext,
} from '@/features/skills/utils/mascotKnowledge'

export function useMascotKnowledge(chapter?: MascotChapterContext, mapContext?: MascotMapContext) {
  const { data: skills } = useLearnedSkills()
  const chapterId = chapter?.id
  const chapterNumber = chapter?.number
  const currentLevelId = mapContext?.currentLevelId
  const levels = mapContext?.levels
  return useMemo(() => {
    const chapterContext = chapterId != null && chapterNumber != null
      ? { id: chapterId, number: chapterNumber }
      : undefined
    const map = levels ? { currentLevelId: currentLevelId ?? null, levels } : undefined
    return knowledgeForMascot(skills ?? [], chapterContext, map)
  }, [skills, chapterId, chapterNumber, currentLevelId, levels])
}
