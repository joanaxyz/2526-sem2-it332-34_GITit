import { AdventureLevelsModal } from '@/features/story-map/components/AdventureLevelsModal'
import { ChallengeTrialsModal } from '@/features/story-map/components/ChallengeTrialsModal'
import { useStoryContentModal } from '@/features/story-map/hooks/useStoryContentModal'

// Single mount point for relic modals. Adventure and challenge relics list their
// playable content; lesson reading lives in the chapter book.
export function StoryContentModals() {
  const active = useStoryContentModal((state) => state.active)
  const close = useStoryContentModal((state) => state.close)

  if (!active) return null

  if (active.kind === 'adventure') {
    return (
      <AdventureLevelsModal
        adventures={active.adventures}
        locked={active.locked}
        lockReason={active.lockReason}
        onClose={close}
      />
    )
  }

  return (
    <ChallengeTrialsModal
      challenges={active.challenges}
      locked={active.locked}
      lockReason={active.lockReason}
      onClose={close}
    />
  )
}
