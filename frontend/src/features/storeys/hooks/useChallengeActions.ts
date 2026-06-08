import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { challengesApi } from '@/features/challenges/api/challengesApi'
import { syncChallengeRunInCache } from '@/features/challenges/utils/challengeRunCache'
import type {
  ChallengeActionIntent,
  ChallengeLevelAccess,
  CommandAdventureSummary,
} from '@/features/challenges/types'

/**
 * Start / resume / retry / review a challenge level, or open a command
 * adventure. Extracted from StoreyPracticeHub so the page-level inspector can
 * own the actions while the doors stay presentational selectors.
 */
export function useChallengeActions() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const startMutation = useMutation({
    mutationFn: (levelId: number) => challengesApi.startChallengeRun(levelId),
    onSuccess: (run) => {
      syncChallengeRunInCache(queryClient, run)
      navigate(`/challenge-runs/${run.id}`)
    },
  })
  const reviewMutation = useMutation({
    mutationFn: (levelId: number) => challengesApi.startChallengeRun(levelId, { review: true }),
    onSuccess: (run) => {
      syncChallengeRunInCache(queryClient, run)
      navigate(`/challenge-runs/${run.id}`)
    },
  })
  const retryMutation = useMutation({
    mutationFn: (runId: number) => challengesApi.retryChallengeRun(runId),
    onSuccess: (run) => {
      syncChallengeRunInCache(queryClient, run)
      navigate(`/challenge-runs/${run.id}`)
    },
  })

  function runChallengeAction(item: ChallengeLevelAccess, action: ChallengeActionIntent) {
    if (action === 'resume' && item.active_run_id) {
      navigate(`/challenge-runs/${item.active_run_id}`)
      return
    }
    if (action === 'review') {
      reviewMutation.mutate(item.id)
      return
    }
    if (action === 'retry' && item.latest_attempt?.id) {
      retryMutation.mutate(item.latest_attempt.id)
      return
    }
    startMutation.mutate(item.id)
  }

  function runAdventureAction(adventure: CommandAdventureSummary) {
    if (adventure.active_run_id) {
      navigate(`/adventure-runs/${adventure.active_run_id}`)
      return
    }
    navigate(`/command-adventures/${adventure.slug}`)
  }

  const actionPending = startMutation.isPending || reviewMutation.isPending || retryMutation.isPending

  return { runChallengeAction, runAdventureAction, actionPending }
}
