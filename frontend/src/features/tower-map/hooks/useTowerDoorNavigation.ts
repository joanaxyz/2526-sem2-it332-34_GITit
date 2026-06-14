import { useNavigate } from 'react-router-dom'

import type {
  ChallengeActionIntent,
  ChallengeLevelAccess,
  CommandAdventureSummary,
} from '@/features/challenges/types'

/**
 * The tower should not start or retry runs directly. It only routes the learner
 * to the selected door's entry or active run page; each level feature owns
 * its own mutations and full-screen loading state.
 */
export function useTowerDoorNavigation() {
  const navigate = useNavigate()

  function openChallengeDoor(item: ChallengeLevelAccess, action: ChallengeActionIntent) {
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

  function openAdventureDoor(adventure: CommandAdventureSummary) {
    if (adventure.active_run_id) {
      navigate(`/adventure-runs/${adventure.active_run_id}`)
      return
    }
    navigate(`/command-adventures/${adventure.slug}`)
  }

  return { openChallengeDoor, openAdventureDoor }
}
