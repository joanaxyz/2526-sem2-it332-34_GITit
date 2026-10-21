import type { LearnedSkill } from '@/features/skills/types'
import type { AdventureKnowledgeItem } from '@/features/story-map/types'
import { COMMAND_ANATOMY_TIP, type MascotKnowledgeTip } from '@/shared/mascot/mascotKnowledge'

export type MascotChapterContext = { id: number; number: number }

type MascotMapLevel = {
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

function authoredTips(
  entries: readonly AdventureKnowledgeItem[],
  source: string,
  prefix: string,
  seenItems: Set<string>,
  seenCommandSummaries: Set<string>,
): MascotKnowledgeTip[] {
  const tips: MascotKnowledgeTip[] = []
  for (const entry of entries) {
    const id = entry.id.trim()
    const command = entry.command.trim()
    const text = entry.text.trim()
    if (!id || !text || seenItems.has(id)) continue
    // A summary repeats across forms; each option/argument form remains useful.
    const commandKey = command.toLowerCase()
    if (entry.kind === 'command' && seenCommandSummaries.has(commandKey)) continue
    seenItems.add(id)
    if (entry.kind === 'command') seenCommandSummaries.add(commandKey)
    tips.push({
      id: `${prefix}:${id}`,
      kind: entry.kind,
      title: entry.title,
      token: entry.token,
      syntax: entry.syntax,
      whenToUse: entry.when_to_use,
      command,
      text,
      source,
    })
  }
  return tips
}

function levelTips(
  context: MascotMapContext | undefined,
  seenItems: Set<string>,
  seenCommandSummaries: Set<string>,
): MascotKnowledgeTip[] {
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
  return orderedLevels.flatMap((level) => authoredTips(
    level.knowledge ?? [], level.title, `level:${level.id}`, seenItems, seenCommandSummaries,
  ))
}

/** Current level guidance leads; the earned spellbook keeps mastered history available. */
export function knowledgeForMascot(
  skills: readonly LearnedSkill[],
  chapter?: MascotChapterContext,
  mapContext?: MascotMapContext,
): MascotKnowledgeTip[] {
  const seenItems = new Set<string>()
  const seenCommandSummaries = new Set<string>()
  const contextual = levelTips(mapContext, seenItems, seenCommandSummaries)
  const earned = skills
    .filter((skill) => !chapter || skill.chapter_number <= chapter.number)
    .sort((a, b) => {
      const aLearnedAt = Date.parse(a.learned_at ?? '') || 0
      const bLearnedAt = Date.parse(b.learned_at ?? '') || 0
      if (aLearnedAt !== bLearnedAt) return bLearnedAt - aLearnedAt
      const aCurrent = a.chapter_id === chapter?.id ? 1 : 0
      const bCurrent = b.chapter_id === chapter?.id ? 1 : 0
      return bCurrent - aCurrent || b.chapter_number - a.chapter_number || a.id - b.id
    })
    .flatMap((skill) => {
      const source = skill.chapter_title || 'Your spellbook'
      const commandKey = skill.base_command.trim().toLowerCase()
      const tips: MascotKnowledgeTip[] = []
      if (skill.summary.trim() && !seenCommandSummaries.has(commandKey)) {
        seenCommandSummaries.add(commandKey)
        tips.push({ id: `skill:${skill.id}`, command: skill.base_command, text: skill.summary, source })
      }
      return [...tips, ...authoredTips(
        skill.knowledge ?? [], source, `skill:${skill.id}`, seenItems, seenCommandSummaries,
      )]
    })

  return [...contextual, ...earned, ...(contextual.length || earned.length ? [COMMAND_ANATOMY_TIP] : [])]
}
