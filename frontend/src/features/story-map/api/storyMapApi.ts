import { apiOperationRequest } from '@/shared/api/httpClient'
import type { ChapterContentOverview } from '@/features/story-map/types'
import type { ChapterBook } from '@/features/story-map/components/book/bookTypes'
import type { Story } from '@/features/story-map/types'
import type { LearningChapter } from '@/features/story-map/types'

export const storyMapApi = {
  listStories() {
    return apiOperationRequest<'stories_list', Story[]>('stories_list', '/stories/')
  },
  listChapters(storySlug?: string | null) {
    const query = storySlug ? `?story=${encodeURIComponent(storySlug)}` : ''
    return apiOperationRequest<'chapters_list', LearningChapter[]>('chapters_list', `/chapters/${query}`)
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
}
