import type { AdventureLevelSummary } from '@/features/challenges/types'
import type { LearningChapter } from '@/features/story-map/types'

export function isFoundationsChapter(chapter: LearningChapter) {
  return chapter.number === 1 || chapter.slug === 'creating-inspecting-repositories'
}

export function chapterTitle(chapter: LearningChapter) {
  return isFoundationsChapter(chapter) ? 'Foundations' : chapter.title
}

export function firstOpenChapter(chapters: LearningChapter[]) {
  return (
    chapters.find((chapter) => !chapter.locked && (chapter.level_completion?.value ?? 0) < 100) ??
    chapters.find((chapter) => !chapter.locked) ??
    chapters[0] ??
    null
  )
}

export function nextPlayableLevelId(levels: AdventureLevelSummary[], chapterLocked: boolean) {
  return levels.find((level) => !chapterLocked && !level.locked && !level.is_passed && !level.completed)?.id ?? null
}

export function adventureLevelCleared(level: AdventureLevelSummary) {
  return level.is_passed || level.completed
}
