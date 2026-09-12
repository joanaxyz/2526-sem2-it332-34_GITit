import type { AdventureLevelSummary } from '@/features/story-map/types'
import type { LearningChapter } from '@/features/story-map/types'

function isFoundationsChapter(chapter: LearningChapter) {
  return chapter.slug === 'creating-inspecting-repositories'
}

export function chapterTitle(chapter: LearningChapter) {
  return isFoundationsChapter(chapter) ? 'Foundations' : chapter.title
}

export function firstOpenChapter(chapters: LearningChapter[], skipOrientation = false) {
  const availableChapters = skipOrientation
    ? chapters.filter((chapter) => !chapter.is_orientation)
    : chapters
  return (
    availableChapters.find((chapter) => !chapter.locked && (chapter.level_completion?.value ?? 0) < 100) ??
    availableChapters.find((chapter) => !chapter.locked) ??
    availableChapters[0] ??
    null
  )
}

export function nextPlayableLevelId(levels: AdventureLevelSummary[], chapterLocked: boolean) {
  return levels.find((level) => !chapterLocked && !level.locked && !level.is_passed)?.id ?? null
}

export function adventureLevelCleared(level: AdventureLevelSummary) {
  return level.is_passed
}
