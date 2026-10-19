import type { LearnedSkill } from '@/features/skills/types'
import type { AdventureKnowledgeItem } from '@/features/story-map/types'
import { COMMAND_ANATOMY_TIP, type MascotKnowledgeTip } from '@/shared/mascot/mascotKnowledge'

export type MascotChapterContext = { id: number; number: number }

export type MascotMapLevel = {
  id: number
  title: string
  is_passed: boolean
  completion?: { completed_at: string } | null
  passed_at?: string | null
  knowledge?: readonly AdventureKnowledgeItem[]
}

export type MascotMapContext = {
  currentLevelId: number | null
  levels: readonly MascotMapLevel[]
}

function levelTips(context: MascotMapContext | undefined): MascotKnowledgeTip[] {
  if (!context) return []
  const current = context.levels.find((level) => level.id === context.currentLevelId)
  const previous = [...context.levels]
    .filter((level) => level.is_passed && level.id !== current?.id)
    .sort((a, b) => {
      const aCompletedAt = Date.parse(a.completion?.completed_at ?? a.passed_at ?? '') || 0
      const bCompletedAt = Date.parse(b.completion?.completed_at ?? b.passed_at ?? '') || 0
      return bCompletedAt - aCompletedAt || b.id - a.id
    })
  const orderedLevels = current ? [current, ...previous] : previous
  const seenItems = new Set<string>()
  const seenCommandSummaries = new Set<string>()
  const tips: MascotKnowledgeTip[] = []

  for (const level of orderedLevels) {
    for (const entry of level.knowledge ?? []) {
      const id = entry.id.trim()
      const command = entry.command.trim()
      const text = entry.text.trim()
      if (!id || !text || seenItems.has(id)) continue
      // A command summary is repeated on every authored form and often on
      // several levels. Keep the first contextual copy; retain each distinct
      // option/argument form pair so those tips remain cycleable.
      const commandKey = command.toLocaleLowerCase()
      if (entry.kind === 'command' && seenCommandSummaries.has(commandKey)) continue
      seenItems.add(id)
      if (entry.kind === 'command') seenCommandSummaries.add(commandKey)
      tips.push({
        id: `level:${level.id}:${id}`,
        kind: entry.kind,
        title: entry.title,
        token: entry.token,
        syntax: entry.syntax,
        whenToUse: entry.when_to_use,
        command,
        text,
        source: level.title,
      })
    }
  }
  return tips
}

/** Current level guidance leads; the earned spellbook keeps mastered history available. */
export function knowledgeForMascot(
  skills: readonly LearnedSkill[],
  chapter?: MascotChapterContext,
  mapContext?: MascotMapContext,
): MascotKnowledgeTip[] {
  const contextual = levelTips(mapContext)
  const contextualCommands = new Set(contextual.map((tip) => (tip.command ?? '').trim().toLowerCase()))
  const earned = skills
    .filter((skill) => skill.summary.trim() && (!chapter || skill.chapter_number <= chapter.number))
    .sort((a, b) => {
      const aLearnedAt = Date.parse(a.learned_at ?? '') || 0
      const bLearnedAt = Date.parse(b.learned_at ?? '') || 0
      if (aLearnedAt !== bLearnedAt) return bLearnedAt - aLearnedAt
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
    .filter((tip) => !contextualCommands.has((tip.command ?? '').trim().toLowerCase()))

  return [...contextual, ...earned, ...(contextual.length || earned.length ? [COMMAND_ANATOMY_TIP] : [])]
}
