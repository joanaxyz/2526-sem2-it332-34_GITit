import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Castle, Check, Feather, PencilRuler, Plus } from 'lucide-react'

import { useTowerDesignEditor } from '@/features/tower-designs/hooks/useTowerDesignEditor'
import { cn } from '@/shared/utils/cn'

export type TowerView = 'official' | 'mine'

const OFFICIAL_LABEL = 'The Arcane Spire'

/**
 * The single in-tower navigation cluster, docked top-right near the SkyClock.
 * Icon-only chips with hover/focus label hints so it reads as instrumentation,
 * not a toolbar. Present on BOTH the official and private views.
 */
export function TowerControls({
  view,
  onViewChange,
}: {
  view: TowerView
  onViewChange: (view: TowerView) => void
}) {
  const navigate = useNavigate()
  const { design, hasDesign, canCreate, isCreating, isForking, raiseSpire, openOfficialFork } =
    useTowerDesignEditor()
  const [pickerOpen, setPickerOpen] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)
  const rootRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!pickerOpen) return
    function onPointerDown(event: PointerEvent) {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) setPickerOpen(false)
    }
    function onKey(event: KeyboardEvent) {
      if (event.key === 'Escape') setPickerOpen(false)
    }
    window.addEventListener('pointerdown', onPointerDown)
    window.addEventListener('keydown', onKey)
    return () => {
      window.removeEventListener('pointerdown', onPointerDown)
      window.removeEventListener('keydown', onKey)
    }
  }, [pickerOpen])

  // Show the tower's real name. Your tower carries its own editable title; the
  // official tower's name is the single OFFICIAL_LABEL constant.
  const mineLabel = design?.title?.trim() || 'Your Tower'
  const activeLabel = view === 'mine' ? mineLabel : OFFICIAL_LABEL

  async function handleRaiseSpire() {
    setActionError(null)
    try {
      const created = await raiseSpire()
      setPickerOpen(false)
      navigate(`/tower/editor/${created.id}`)
    } catch (error) {
      setActionError(actionErrorMessage(error, 'Could not raise your tower.'))
    }
  }

  function selectMine() {
    setPickerOpen(false)
    if (hasDesign) onViewChange('mine')
    else void handleRaiseSpire()
  }

  async function openEditor() {
    // Editing while viewing the official tower opens a private fork of it; your
    // tweaks there stay yours. Editing your own tower opens your design. The
    // editor is its own full-screen route (`/tower/editor/:designId`).
    setActionError(null)
    try {
      if (view === 'official') {
        const fork = await openOfficialFork()
        navigate(`/tower/editor/${fork.design.id}`)
        return
      }
      if (hasDesign && design) navigate(`/tower/editor/${design.id}`)
      else await handleRaiseSpire()
    } catch (error) {
      setActionError(actionErrorMessage(error, 'Could not open the editor.'))
    }
  }

  return (
    <div className="tower-controls" ref={rootRef}>
      {/* Compact tower picker */}
      <div className="tower-controls-picker">
        <button
          type="button"
          className="tower-control-chip tower-control-chip--picker"
          aria-haspopup="menu"
          aria-expanded={pickerOpen}
          onClick={() => setPickerOpen((open) => !open)}
        >
          <Castle className="size-4" aria-hidden="true" />
          <span className="tower-control-chip-label">{activeLabel}</span>
        </button>

        {pickerOpen ? (
          <div className="tower-control-popover" role="menu" aria-label="Choose a tower">
            <button
              type="button"
              role="menuitemradio"
              aria-checked={view === 'official'}
              className={cn('tower-control-option', view === 'official' && 'is-active')}
              onClick={() => {
                setPickerOpen(false)
                onViewChange('official')
              }}
            >
              <span>{OFFICIAL_LABEL}</span>
              {view === 'official' ? <Check className="size-3.5" aria-hidden="true" /> : null}
            </button>

            {hasDesign ? (
              <button
                type="button"
                role="menuitemradio"
                aria-checked={view === 'mine'}
                className={cn('tower-control-option', view === 'mine' && 'is-active')}
                onClick={selectMine}
              >
                <span>{mineLabel}</span>
                {view === 'mine' ? <Check className="size-3.5" aria-hidden="true" /> : null}
              </button>
            ) : (
              <button
                type="button"
                role="menuitem"
                className="tower-control-option tower-control-option--create"
                disabled={!canCreate}
                onClick={() => void handleRaiseSpire()}
              >
                <Plus className="size-3.5" aria-hidden="true" />
                <span>{isCreating ? 'Raising…' : 'Raise your Tower'}</span>
              </button>
            )}
          </div>
        ) : null}
      </div>

      {/* Icon actions */}
      <button
        type="button"
        className="tower-control-chip tower-control-chip--icon"
        data-hint={
          view === 'official'
            ? `Edit ${OFFICIAL_LABEL} (private to you)`
            : hasDesign
              ? `Edit ${mineLabel}`
              : 'Raise your Tower'
        }
        aria-label={
          view === 'official'
            ? `Edit ${OFFICIAL_LABEL} privately`
            : hasDesign
              ? `Edit ${mineLabel}`
              : 'Raise your Tower'
        }
        disabled={isCreating || isForking}
        onClick={() => void openEditor()}
      >
        <PencilRuler className="size-4" aria-hidden="true" />
      </button>

      {/* Authoring belongs to YOUR tower only: the button shows on your personal
          tower and opens its in-page editor (not the official tower or fork). */}
      {view === 'mine' && hasDesign && design?.origin === 'personal' ? (
        <button
          type="button"
          className="tower-control-chip tower-control-chip--icon"
          data-hint="Author content"
          aria-label="Author content — The Scriptorium"
          onClick={() => navigate(`/tower/editor/${design.id}`)}
        >
          <Feather className="size-4" aria-hidden="true" />
        </button>
      ) : null}

      {actionError ? (
        <p role="alert" className="tower-control-error">
          {actionError}
        </p>
      ) : null}
    </div>
  )
}

function actionErrorMessage(error: unknown, fallback: string) {
  if (error instanceof Error && error.message.trim()) {
    return `${fallback} ${error.message}`
  }
  return `${fallback} Please try again.`
}
