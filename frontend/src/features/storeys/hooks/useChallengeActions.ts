import { useNavigate } from 'react-router-dom'

import type {
  ChallengeActionIntent,
  ChallengeLevelAccess,
  CommandAdventureSummary,
} from '@/features/challenges/types'

/**
 * Opens the selected tower door. Challenge start/review/retry work is routed to
 * dedicated practice pages so the full-screen loader belongs to the destination
 * flow instead of being rendered inside the tower dock.
 */
export function useChallengeActions() {
  const navigate = useNavigate()

  function runChallengeAction(item: ChallengeLevelAccess, action: ChallengeActionIntent) {
    if (action === 'resume' && item.active_run_id) {
      navigate(`/challenge-runs/${item.active_run_id}`)
      return
    }
    if (action === 'review') {
      navigate(`/challenge-levels/${item.id}/review`)
      return
    }
    if (action === 'retry' && item.latest_attempt?.id) {
      navigate(`/challenge-runs/${item.latest_attempt.id}/retry`)
      return
    }
    navigate(`/challenge-levels/${item.id}`)
  }

  function runAdventureAction(adventure: CommandAdventureSummary) {
    if (adventure.active_run_id) {
      navigate(`/adventure-runs/${adventure.active_run_id}`)
      return
    }
    navigate(`/command-adventures/${adventure.slug}`)
  }

  return { runChallengeAction, runAdventureAction }
}
