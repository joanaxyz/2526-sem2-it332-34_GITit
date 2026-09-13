import { apiOperationRequest } from '@/shared/api/httpClient'

import type { ActivityWindow } from '@/features/stats/types'

export const statsApi = {
  /**
   * `window` scopes the activity trend only (week = 7 days, month = 30 days,
   * year = 12 monthly buckets). Every headline number in the response is
   * all-time, so the rest of the screen does not move when it changes.
   */
  summary(window?: ActivityWindow) {
    const query = window ? `?window=${encodeURIComponent(window)}` : ''
    return apiOperationRequest('progress_stats_retrieve', `/progress/stats/${query}`)
  },
}
