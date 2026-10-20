import { useNavigate } from 'react-router-dom'

import { tierStartUrl } from '@/features/story-map/components/tierWorkspaceLayout'

export function useStoryAdventureStarts({
  hasCompanion,
  onCompanionRequired,
}: {
  hasCompanion: boolean
  onCompanionRequired: () => void
}) {
  const navigate = useNavigate()

  function requireCompanion(action: () => void) {
    if (!hasCompanion) {
      onCompanionRequired()
      return
    }
    action()
  }

  return {
    startTier: (tierId: number, replay: boolean) =>
      requireCompanion(() => navigate(tierStartUrl(tierId, { replay }))),
  }
}
