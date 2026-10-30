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

/** Knowledge follows the next playable level, or the most recently cleared level when none remains. */
export function mascotKnowledgeFocusLevelId(levels: AdventureLevelSummary[], chapterLocked: boolean) {
  const nextPlayable = nextPlayableLevelId(levels, chapterLocked)
  if (nextPlayable != null) return nextPlayable

  return [...levels]
    .filter((level) => level.is_passed)
    .sort((a, b) => {
      const aCompletedAt = Date.parse(a.completion?.completed_at ?? a.passed_at ?? '') || 0
      const bCompletedAt = Date.parse(b.completion?.completed_at ?? b.passed_at ?? '') || 0
      return bCompletedAt - aCompletedAt || b.id - a.id
    })[0]?.id ?? null
}

export function adventureLevelCleared(level: AdventureLevelSummary) {
  return level.is_passed
}
