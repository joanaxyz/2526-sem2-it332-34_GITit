import { queryOptions } from '@tanstack/react-query'

import { apiOperationRequest } from '@/shared/api/httpClient'
import { queryKeys } from '@/shared/api/queryKeys'
import type { ChapterContentOverview, LearningChapter } from '@/features/story-map/types'
import {
  readStoryMapSnapshot,
  storyMapSnapshotKeys,
  writeStoryMapSnapshot,
} from '@/features/story-map/utils/storyMapSnapshot'
import type { ChapterBook } from '@/features/story-map/components/book/bookTypes'
import type {
  ChapterOrientationLessonDetail,
  ChapterOrientationLessonSummary,
} from '@/features/story-map/components/orientation/types'

export const storyMapApi = {
  listStories() {
    return apiOperationRequest('stories_list', '/stories/')
  },
  listChapters(storySlug?: string | null) {
    const query = storySlug ? `?story=${encodeURIComponent(storySlug)}` : ''
    return apiOperationRequest('chapters_list', `/chapters/${query}`)
  },
  getChapterChests(chapterId: number) {
    return apiOperationRequest('chapters_chests_retrieve', `/chapters/${chapterId}/chests/`)
  },
  openChapterChest(chapterId: number, threshold: number) {
    return apiOperationRequest('chapters_chests_create', `/chapters/${chapterId}/chests/`, {
      body: { threshold },
    })
  },
  getChapterOverview(chapterId: number) {
    return apiOperationRequest<'chapters_overview_retrieve', ChapterContentOverview>(
      'chapters_overview_retrieve',
      `/chapters/${chapterId}/overview/`,
    )
  },
  getChapterBook(chapterId: number) {
    return apiOperationRequest<'chapters_book_retrieve', ChapterBook>(
      'chapters_book_retrieve',
      `/chapters/${chapterId}/book/`,
    )
  },
  listOrientationLessons(chapterId: number) {
    return apiOperationRequest<'chapters_orientation_list', ChapterOrientationLessonSummary[]>(
      'chapters_orientation_list',
      `/chapters/${chapterId}/orientation/`,
    )
  },
  getOrientationLesson(lessonId: number) {
    return apiOperationRequest<'orientation_lessons_retrieve', ChapterOrientationLessonDetail>(
      'orientation_lessons_retrieve',
      `/orientation-lessons/${lessonId}/`,
    )
  },
  completeOrientationLesson(lessonId: number, highestStepSeen: number) {
    return apiOperationRequest<'orientation_lessons_complete_create', ChapterOrientationLessonDetail>(
      'orientation_lessons_complete_create',
      `/orientation-lessons/${lessonId}/complete/`,
      { body: { highest_step_seen: highestStepSeen } },
    )
  },
}

// Both map queries seed from the player's last-known snapshot and mark it
// stale (updatedAt 0), so the path paints immediately and revalidates at once.
export function storyChaptersQueryOptions(storySlug: string) {
  const snapshotKey = storyMapSnapshotKeys.chapters(storySlug)
  return queryOptions({
    queryKey: queryKeys.storyChapters(storySlug),
    queryFn: async () => {
      const chapters = await storyMapApi.listChapters(storySlug)
      writeStoryMapSnapshot(snapshotKey, chapters)
      return chapters
    },
    initialData: () => readStoryMapSnapshot<LearningChapter[]>(snapshotKey),
    initialDataUpdatedAt: 0,
    staleTime: 5 * 60 * 1000,
  })
}

export function chapterOverviewQueryOptions(chapterId: number) {
  const snapshotKey = storyMapSnapshotKeys.chapterOverview(chapterId)
  return queryOptions({
    queryKey: queryKeys.chapterOverview(chapterId),
    queryFn: async () => {
      const overview = await storyMapApi.getChapterOverview(chapterId)
      writeStoryMapSnapshot(snapshotKey, overview)
      return overview
    },
    initialData: () => readStoryMapSnapshot<ChapterContentOverview>(snapshotKey),
    initialDataUpdatedAt: 0,
    staleTime: 2 * 60 * 1000,
  })
}
