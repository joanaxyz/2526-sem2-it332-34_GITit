import type { ApiSchemas } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'

export type Leaderboard = ApiSchemas['LeaderboardResponse']
export type LeaderboardCategory = 'xp' | 'perfect_clears' | 'gates'

export const leaderboardApi = {
  get(category: LeaderboardCategory) {
    const query = `?category=${encodeURIComponent(category)}`
    return apiOperationRequest('progress_leaderboard_retrieve', `/progress/leaderboard/${query}`)
  },
}
