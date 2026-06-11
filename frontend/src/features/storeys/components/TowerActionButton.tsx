import { type CSSProperties } from 'react'

import { Button } from '@/shared/components/Button'
import {
  actionForChallengeQuest,
  actionLabel,
  adventureActionLabel,
  challengeQuestAccent,
} from '@/features/storeys/challengeUi'
import { useTowerDoorNavigation } from '@/features/storeys/hooks/useTowerDoorNavigation'
import { useTowerSelection } from '@/features/storeys/hooks/useTowerSelection'

const ADVENTURE_ACCENT = '0, 245, 212'

// The single floating action for whatever door is selected, pinned lower-left.
export function TowerActionButton() {
  const selected = useTowerSelection((state) => state.selected)
  const { openChallengeDoor, openAdventureDoor } = useTowerDoorNavigation()

  if (!selected) return null

  if (selected.kind === 'adventure') {
    const { adventure } = selected

    return (
      <>
        <div className="tower-action-dock" style={{ '--action-accent': ADVENTURE_ACCENT } as CSSProperties}>
          <Button
            type="button"
            className="tower-action-button"
            onClick={() => openAdventureDoor(adventure)}
          >
            {adventureActionLabel(adventure)}
          </Button>
        </div>
      </>
    )
  }

  const { quest, locked } = selected
  const action = actionForChallengeQuest(quest)
  const accent = challengeQuestAccent(quest)
  const disabled = locked || !action

  return (
    <>
      <div className="tower-action-dock" style={{ '--action-accent': accent } as CSSProperties}>
        <Button
          type="button"
          className="tower-action-button"
          disabled={disabled}
          onClick={() => {
            if (action) openChallengeDoor(quest, action)
          }}
        >
          {actionLabel(action, quest.status)}
        </Button>
      </div>
    </>
  )
}