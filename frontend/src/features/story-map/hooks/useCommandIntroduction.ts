import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'

import { commandIntroductionsApi, type CommandIntroduction } from '@/features/story-map/api/commandIntroductionsApi'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { updateTierRunCache } from '@/features/story-map/utils/tierRunCache'
import { ApiError } from '@/shared/api/apiError'
import { queryKeys } from '@/shared/api/queryKeys'

/** Acknowledges server feedback. Commands use the ordinary terminal mutation. */
export function useCommandIntroduction(run: TierRun, tutor: CommandIntroduction) {
  const queryClient = useQueryClient()
  const [pending, setPending] = useState(false)
  const [error, setError] = useState('')
  const key = queryKeys.adventureTierRun(run.id)
  const isCurrent = () => queryClient.getQueryData<TierRun>(key)?.tutor?.context_id === tutor.context_id

  return {
    pending, error,
    async complete() {
      if (pending || !tutor.completion_token || !isCurrent()) return false
      setPending(true)
      setError('')
      try {
        const response = await commandIntroductionsApi.complete(run.id, tutor.completion_token)
        if (!isCurrent()) return false
        const current = queryClient.getQueryData<TierRun>(key)
        if (current) updateTierRunCache(queryClient, { ...current, tutor: response.tutor })
        return true
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : 'Could not save this introduction. Try again.')
        if (cause instanceof ApiError && [400, 409, 423].includes(cause.status)) {
          await queryClient.invalidateQueries({ queryKey: key })
        }
        return false
      } finally {
        setPending(false)
      }
    },
  }
}
