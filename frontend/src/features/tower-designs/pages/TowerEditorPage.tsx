import { useNavigate, useParams } from 'react-router-dom'

import { InTowerEditor } from '@/features/tower-map/editor/InTowerEditor'
import { useTowerDesignEditor } from '@/features/tower-designs/hooks/useTowerDesignEditor'
import { Button } from '@/shared/components/Button'
import { LoadingState } from '@/shared/components/LoadingState'

/**
 * The tower editor as its own full-screen surface (`/tower/editor/:designId`).
 * It used to live inside the tower page via `?mode=edit`; it now stands alone so
 * the authoring tool is a focused workspace rather than an overlay on the spire.
 * Without an id (`/tower/editor`) it opens the user's personal design.
 */
export function TowerEditorPage() {
  const { designId } = useParams()
  const navigate = useNavigate()
  const { design, fork, isLoading } = useTowerDesignEditor()

  const routeId = designId ? Number(designId) : null
  const id = routeId ?? design?.id ?? null
  // Return to the tower the editor was opened from: the official view when
  // editing the private fork of the Arcane Spire, your own tower otherwise.
  // (Hardcoding ?view=mine dropped fork editors onto the wrong tower.)
  const editingFork = fork?.id != null && id === fork.id
  const exit = () => navigate(editingFork ? '/tower' : '/tower?view=mine')

  // Only the no-id entry has to wait on the personal design to resolve; a routed
  // id opens straight away.
  if (routeId === null && isLoading) {
    return <LoadingState label="Opening the editor" variant="screen" />
  }

  if (id === null || Number.isNaN(id)) {
    return (
      <div className="ite-shell ite-shell--message">
        <div className="ite-shell-message">
          <h1>No tower to edit</h1>
          <p>Raise your tower first, then come back to design it.</p>
          <Button onClick={() => navigate('/tower?view=mine')}>Back to your tower</Button>
        </div>
      </div>
    )
  }

  return <InTowerEditor designId={id} onExit={exit} />
}

export default TowerEditorPage
