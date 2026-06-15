import { useNavigate } from 'react-router-dom'

import type {
  ChallengeActionIntent,
  ChallengeLevelAccess,
  CommandAdventureSummary,
} from '@/features/challenges/types'

/**
 * The tower routes from the selected interactable artifact into the owning
 * feature. It does not start or retry runs directly; challenges and adventures
 * own their own mutations and full-screen loading state.
 */
export function useTowerArtifactNavigation() {
  const navigate = useNavigate()

  function openChallengeArtifact(item: ChallengeLevelAccess, action: ChallengeActionIntent) {
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

  function openAdventureArtifact(adventure: CommandAdventureSummary) {
    if (adventure.active_run_id) {
      navigate(`/adventure-runs/${adventure.active_run_id}`)
      return
    }
    navigate(`/command-adventures/${adventure.slug}`)
  }

  return { openChallengeArtifact, openAdventureArtifact }
}
