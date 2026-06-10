import { type CSSProperties } from 'react'

import { Button } from '@/shared/components/Button'
import { LoadingState } from '@/shared/components/LoadingState'
import {
  actionForChallengeLevel,
  actionLabel,
  adventureActionLabel,
  challengeLevelAccent,
} from '@/features/storeys/challengeUi'
import { useChallengeActions } from '@/features/storeys/hooks/useChallengeActions'
import { useTowerSelection } from '@/features/storeys/hooks/useTowerSelection'

const ADVENTURE_ACCENT = '0, 245, 212'

// The single floating action for whatever door is selected, pinned lower-left.
export function TowerActionButton() {
  const selected = useTowerSelection((state) => state.selected)
  const { runChallengeAction, runAdventureAction, actionPending } = useChallengeActions()

  if (!selected) return null

  const pendingOverlay = actionPending ? (
    <div className="tower-loading-overlay">
      <LoadingState
        description="Preparing the repository, terminal, and stage data."
        label={selected.kind === 'adventure' ? 'Loading adventure' : 'Loading challenge'}
        variant="screen"
      />
    </div>
  ) : null

  if (selected.kind === 'adventure') {
    const { adventure } = selected

    return (
      <>
        <div className="tower-action-dock" style={{ '--action-accent': ADVENTURE_ACCENT } as CSSProperties}>
          <Button
            type="button"
            className="tower-action-button"
            disabled={actionPending}
            onClick={() => runAdventureAction(adventure)}
          >
            {adventureActionLabel(adventure)}
          </Button>
        </div>
        {pendingOverlay}
      </>
    )
  }

  const { level, locked } = selected
  const action = actionForChallengeLevel(level)
  const accent = challengeLevelAccent(level)
  const disabled = actionPending || locked || !action

  return (
    <>
      <div className="tower-action-dock" style={{ '--action-accent': accent } as CSSProperties}>
        <Button
          type="button"
          className="tower-action-button"
          disabled={disabled}
          onClick={() => {
            if (action) runChallengeAction(level, action)
          }}
        >
          {actionLabel(action, level.status)}
        </Button>
      </div>
      {pendingOverlay}
    </>
  )
}