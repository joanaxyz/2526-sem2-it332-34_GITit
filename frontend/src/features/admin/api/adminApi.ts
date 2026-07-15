import type { WalletSummary } from '@/shared/wallet/api/walletApi'
import { apiRequest } from '@/shared/api/httpClient'

export type AdminOverview = {
  users: { total: number; new_7d: number; new_30d: number }
  economy: { coins_in_circulation: number; coins_spent: number; signup_grant: number }
  recent_signups: AdminUserBrief[]
  recent_purchases: { user_id: number; amount: number; reason: string; created_at: string }[]
}

export type AdminUserBrief = {
  id: number
  username: string
  email: string
  is_staff: boolean
  is_active: boolean
  date_joined: string
}

export type AdminUserDetail = AdminUserBrief & {
  last_login: string | null
  wallet: WalletSummary
  entitlement_count: number
}

export type AdminTransaction = {
  id: number
  user_id: number
  username: string
  amount: number
  reason: string
  created_at: string
}

export type AdminStory = {
  id: number
  slug: string
  title: string
  summary: string
  sort_order: number
  is_published: boolean
  chapter_count: number
}

export type AdminChapter = {
  id: number
  story_id: number | null
  slug: string
  number: number
  title: string
  description: string
  is_published: boolean
  sort_order: number
}

export type AdminContent = {
  id: number
  kind: string
  slug: string
  title: string
  status: string
  visibility: string
  updated_at: string
}

export type AdminAnalytics = {
  runs: { by_status: Record<string, number>; total: number; passed: number }
  completions: { adventure: number; challenge: number; total: number }
  active_learners_30d: number
  per_story: { slug: string; title: string; runs: number; passed: number }[]
}

export type AdminModeration = {
  content: { id: number; kind: string; title: string; owner: string | null; updated_at: string }[]
}

export type AdminFeatureFlag = { key: string; label: string; description: string; enabled: boolean }
export type AdminSettings = { feature_flags: AdminFeatureFlag[] }

type UserActionPayload =
  | { action: 'grant_coins'; amount: number; reason?: string }
  | { action: 'set_staff'; value: boolean }
  | { action: 'set_active'; value: boolean }

function body(payload: unknown) {
  return { body: JSON.stringify(payload) }
}

export const adminApi = {
  overview() {
    return apiRequest<AdminOverview>('/admin/overview/')
  },
  users(query?: string) {
    const q = query ? `?q=${encodeURIComponent(query)}` : ''
    return apiRequest<{ results: AdminUserBrief[] }>(`/admin/users/${q}`)
  },
  user(id: number) {
    return apiRequest<AdminUserDetail>(`/admin/users/${id}/`)
  },
  userAction(id: number, payload: UserActionPayload) {
    return apiRequest<AdminUserDetail>(`/admin/users/${id}/actions/`, { method: 'POST', ...body(payload) })
  },
  transactions(userId?: number) {
    const q = userId ? `?user_id=${userId}` : ''
    return apiRequest<{ results: AdminTransaction[] }>(`/admin/economy/transactions/${q}`)
  },
  adjustCoins(payload: { user_id: number; amount: number; reason?: string }) {
    return apiRequest<{ wallet: WalletSummary }>('/admin/economy/adjust/', { method: 'POST', ...body(payload) })
  },
  stories() {
    return apiRequest<{ results: AdminStory[] }>('/admin/stories/')
  },
  createStory(payload: { slug: string; title: string; summary?: string }) {
    return apiRequest<AdminStory>('/admin/stories/', { method: 'POST', ...body(payload) })
  },
  updateStory(id: number, patch: Partial<Pick<AdminStory, 'title' | 'summary' | 'sort_order' | 'is_published'>>) {
    return apiRequest<AdminStory>(`/admin/stories/${id}/`, { method: 'PATCH', ...body(patch) })
  },
  chapters(storyId?: number) {
    const q = storyId ? `?story=${storyId}` : ''
    return apiRequest<{ results: AdminChapter[] }>(`/admin/chapters/${q}`)
  },
  updateChapter(id: number, patch: Partial<Pick<AdminChapter, 'title' | 'description' | 'is_published' | 'sort_order'>>) {
    return apiRequest<AdminChapter>(`/admin/chapters/${id}/`, { method: 'PATCH', ...body(patch) })
  },
  content(kind?: string) {
    const q = kind ? `?kind=${kind}` : ''
    return apiRequest<{ results: AdminContent[] }>(`/admin/content/${q}`)
  },
  analytics() {
    return apiRequest<AdminAnalytics>('/admin/analytics/')
  },
  moderation() {
    return apiRequest<AdminModeration>('/admin/moderation/')
  },
  unpublish(payload: { kind: 'content'; id: number }) {
    return apiRequest<{ ok: boolean }>('/admin/moderation/unpublish/', { method: 'POST', ...body(payload) })
  },
  settings() {
    return apiRequest<AdminSettings>('/admin/settings/')
  },
  saveFlag(payload: { key: string; label?: string; description?: string; enabled?: boolean }) {
    return apiRequest<AdminFeatureFlag>('/admin/settings/', { method: 'POST', ...body(payload) })
  },
}
