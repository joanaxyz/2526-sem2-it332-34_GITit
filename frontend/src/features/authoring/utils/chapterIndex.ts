import type { AuthoringChapter } from '@/features/authoring/types'

export function chapterIndexToSortOrder(chapterIndex: number): number | null {
  const normalized = Math.round(Number(chapterIndex))
  if (!Number.isFinite(normalized) || normalized < 1) return null
  return normalized - 1
}

export function findChapterForIndex(
  chapters: AuthoringChapter[],
  chapterIndex: number | null | undefined,
): AuthoringChapter | null {
  if (chapterIndex == null) return null
  const sortOrder = chapterIndexToSortOrder(chapterIndex)
  if (sortOrder == null) return null
  return chapters.find((chapter) => chapter.sort_order === sortOrder) ?? null
}
