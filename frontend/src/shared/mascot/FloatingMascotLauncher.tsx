import type { ReactNode, Ref } from 'react'
import { createPortal } from 'react-dom'

import { MascotPortrait } from './GuideCharacterPortrait'
import { useFloatingPosition } from './useFloatingPosition'
import './mascot-launcher.css'

/**
 * Git-It floating over the page. A click opens what it launches; a drag only
 * moves it. While that is open the launcher hides but keeps its place, so a
 * closing window can collapse back into it (`[data-mascot-launcher="<name>"]`).
 */
export function FloatingMascotLauncher({ name, label, caption, open = false, onOpen, onDragStart, buttonRef, children }: {
  /** Identifies the launcher: its saved position and its collapse selector. */
  name: string
  /** The button's accessible name, e.g. "Open command guide". */
  label: string
  /** The short tag under the portrait, e.g. "Guide". */
  caption: string
  open?: boolean
  onOpen: () => void
  onDragStart?: () => void
  buttonRef?: Ref<HTMLButtonElement>
  /** Controls pinned to the launcher, beside its button. */
  children?: ReactNode
}) {
  const { position, dragging, handlers, clicked } = useFloatingPosition(`mascot-launcher:${name}`, onDragStart)

  return createPortal(
    <div
      className="mascot-launcher"
      style={{ left: position.x, top: position.y }}
      data-dragging={dragging || undefined}
      aria-hidden={open || undefined}
      inert={open || undefined}
    >
      <button
        ref={buttonRef}
        type="button"
        className="mascot-launcher__button"
        data-mascot-launcher={name}
        aria-label={label}
        aria-expanded={open}
        title={`${label} · Drag to move. Arrow keys move; Home resets.`}
        {...handlers}
        onClick={() => {
          if (clicked() && !open) onOpen()
        }}
      >
        <MascotPortrait className="mascot-launcher__portrait" alt="" width={72} height={90} />
        <span className="mascot-launcher__caption">{caption}</span>
      </button>
      {children}
    </div>,
    document.body,
  )
}
