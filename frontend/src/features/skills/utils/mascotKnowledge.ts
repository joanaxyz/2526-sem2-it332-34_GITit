import type { LearnedSkill } from '@/features/skills/types'
import type { MascotKnowledgeTip } from '@/shared/mascot/mascotKnowledge'

export type MascotChapterContext = { id: number; number: number }

/** The earned spellbook owns knowledge; browsing a later chapter never unlocks tips. */
export function knowledgeForMascot(skills: readonly LearnedSkill[], chapter?: MascotChapterContext): MascotKnowledgeTip[] {
  return skills
    .filter((skill) => skill.summary.trim() && (!chapter || skill.chapter_number <= chapter.number))
    .sort((a, b) => {
      const aCurrent = a.chapter_id === chapter?.id ? 1 : 0
      const bCurrent = b.chapter_id === chapter?.id ? 1 : 0
      return bCurrent - aCurrent || b.chapter_number - a.chapter_number || a.id - b.id
    })
    .map((skill) => ({
      id: `skill:${skill.id}`,
      command: skill.base_command,
      text: skill.summary,
      source: skill.chapter_title || 'Your spellbook',
    }))
}
