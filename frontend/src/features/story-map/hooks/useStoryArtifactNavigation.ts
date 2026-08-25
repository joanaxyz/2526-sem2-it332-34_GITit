import { useNavigate } from 'react-router-dom'

import type {
  ChallengeActionIntent,
  ChallengeTrialAccess,
} from '@/features/challenges/types'
import type { AdventureLevelSummary } from '@/features/story-map/types'

/**
 * The story map routes from the selected interactable artifact into the owning
 * feature. It does not start or retry runs directly; challenges and adventures
 * own their own mutations and full-screen loading state.
 */
export function useStoryArtifactNavigation() {
  const navigate = useNavigate()

  function openChallengeArtifact(item: ChallengeTrialAccess, action: ChallengeActionIntent) {
    if (action === 'replay') {
      navigate(`/challenge-trials/${item.id}/replay`)
      return
    }
    if (action === 'retry' && item.latest_attempt?.id) {
      navigate(`/challenge-runs/${item.latest_attempt.id}/retry`)
      return
    }
    navigate(`/challenge-trials/${item.id}`)
  }

  function openAdventureLevel(level: AdventureLevelSummary) {
    navigate(`/adventure-levels/${level.id}`)
  }

  return { openChallengeArtifact, openAdventureLevel }
}
