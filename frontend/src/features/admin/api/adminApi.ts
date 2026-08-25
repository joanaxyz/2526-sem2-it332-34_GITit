import { apiOperationRequest } from '@/shared/api/httpClient'
import type {
  ApiRequestBody,
  ApiSchemas,
} from '@/shared/api/generated/apiTypes'

export type AdminStory = ApiSchemas['AdminStory']
export type AdminChapter = ApiSchemas['AdminChapter']

export type AdminStoryCreatePayload = ApiRequestBody<'admin_stories_create'>
export type AdminChapterCreatePayload = ApiRequestBody<'admin_chapters_create'>

type UserActionPayload = ApiRequestBody<'admin_users_actions_create'>
type EconomyAdjustPayload = ApiRequestBody<'admin_economy_adjust_create'>
type StoryUpdatePayload = ApiRequestBody<'admin_stories_partial_update'>
type ChapterUpdatePayload = ApiRequestBody<'admin_chapters_partial_update'>
type ModerationUnpublishPayload = ApiRequestBody<'admin_moderation_unpublish_create'>
type FeatureFlagUpdatePayload = ApiRequestBody<'admin_settings_create'>

export const adminApi = {
  overview() {
    return apiOperationRequest('admin_overview_retrieve', '/admin/overview/')
  },
  users(query?: string) {
    const suffix = query ? `?q=${encodeURIComponent(query)}` : ''
    return apiOperationRequest('admin_users_retrieve', `/admin/users/${suffix}`)
  },
  user(id: number) {
    return apiOperationRequest('admin_users_retrieve_2', `/admin/users/${id}/`)
  },
  userAction(id: number, payload: UserActionPayload) {
    return apiOperationRequest('admin_users_actions_create', `/admin/users/${id}/actions/`, {
      body: payload,
    })
  },
  transactions(userId?: number) {
    const suffix = userId ? `?user_id=${userId}` : ''
    return apiOperationRequest(
      'admin_economy_transactions_retrieve',
      `/admin/economy/transactions/${suffix}`,
    )
  },
  adjustCoins(payload: EconomyAdjustPayload) {
    return apiOperationRequest('admin_economy_adjust_create', '/admin/economy/adjust/', {
      body: payload,
    })
  },
  stories() {
    return apiOperationRequest('admin_stories_retrieve', '/admin/stories/')
  },
  createStory(payload: AdminStoryCreatePayload) {
    return apiOperationRequest('admin_stories_create', '/admin/stories/', { body: payload })
  },
  updateStory(id: number, patch: StoryUpdatePayload) {
    return apiOperationRequest('admin_stories_partial_update', `/admin/stories/${id}/`, {
      body: patch,
    })
  },
  chapters(storyId?: number) {
    const suffix = storyId ? `?story=${storyId}` : ''
    return apiOperationRequest('admin_chapters_retrieve', `/admin/chapters/${suffix}`)
  },
  createChapter(payload: AdminChapterCreatePayload) {
    return apiOperationRequest('admin_chapters_create', '/admin/chapters/', { body: payload })
  },
  updateChapter(id: number, patch: ChapterUpdatePayload) {
    return apiOperationRequest('admin_chapters_partial_update', `/admin/chapters/${id}/`, {
      body: patch,
    })
  },
  content(kind?: ApiSchemas['AdminContentKindEnum']) {
    const suffix = kind ? `?kind=${kind}` : ''
    return apiOperationRequest('admin_content_retrieve', `/admin/content/${suffix}`)
  },
  analytics() {
    return apiOperationRequest('admin_analytics_retrieve', '/admin/analytics/')
  },
  moderation() {
    return apiOperationRequest('admin_moderation_retrieve', '/admin/moderation/')
  },
  unpublish(payload: ModerationUnpublishPayload) {
    return apiOperationRequest(
      'admin_moderation_unpublish_create',
      '/admin/moderation/unpublish/',
      { body: payload },
    )
  },
  settings() {
    return apiOperationRequest('admin_settings_retrieve', '/admin/settings/')
  },
  saveFlag(payload: FeatureFlagUpdatePayload) {
    return apiOperationRequest('admin_settings_create', '/admin/settings/', { body: payload })
  },
}
