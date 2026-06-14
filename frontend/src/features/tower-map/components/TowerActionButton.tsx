import { useState, type CSSProperties } from 'react'

import { Button } from '@/shared/components/Button'
import type { TomeSummary } from '@/features/challenges/types'
import { TomeReaderModal } from '@/features/storeys/book/TomeReaderModal'
import {
  actionForChallengeLevel,
  actionLabel,
  adventureActionLabel,
  challengeLevelAccent,
} from '@/features/storeys/challengeUi'
import { useTowerDoorNavigation } from '@/features/storeys/hooks/useTowerDoorNavigation'
import { useTowerSelection } from '@/features/storeys/hooks/useTowerSelection'

const ADVENTURE_ACCENT = '0, 245, 212'

// The single floating action for whatever door is selected, pinned lower-left.
export function TowerActionButton() {
  const selected = useTowerSelection((state) => state.selected)
  const { openChallengeDoor, openAdventureDoor } = useTowerDoorNavigation()
  // Tomes open in place (a reader modal), not via navigation like the doors.
  const [openTome, setOpenTome] = useState<TomeSummary | null>(null)

  if (!selected) return null

  if (selected.kind === 'tome') {
    const { tome } = selected
    return (
      <>
        <div className="tower-action-dock" style={{ '--action-accent': ADVENTURE_ACCENT } as CSSProperties}>
          <Button type="button" className="tower-action-button" onClick={() => setOpenTome(tome)}>
            Read
          </Button>
        </div>
        {openTome ? <TomeReaderModal tome={openTome} onClose={() => setOpenTome(null)} /> : null}
      </>
    )
  }

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

  const { level, locked } = selected
  const action = actionForChallengeLevel(level)
  const accent = challengeLevelAccent(level)
  const disabled = locked || !action

  return (
    <>
      <div className="tower-action-dock" style={{ '--action-accent': accent } as CSSProperties}>
        <Button
          type="button"
          className="tower-action-button"
          disabled={disabled}
          onClick={() => {
            if (action) openChallengeDoor(level, action)
          }}
        >
          {actionLabel(action, level.status)}
        </Button>
      </div>
    </>
  )
}