import { useEffect, type ReactNode, type Ref } from 'react'
import { createPortal } from 'react-dom'

import { MascotPortrait } from './GuideCharacterPortrait'
import { FLOATING_LAUNCHER_SIZES, rememberShownPosition, useFloatingPosition, type FloatingHomeSlot } from './useFloatingPosition'
import './mascot-launcher.css'

/**
 * Git-It floating over the page. A click opens what it launches; a drag only
 * moves it. While that is open the launcher hides but keeps its place, so a
 * closing window can collapse back into it (`[data-mascot-launcher="<name>"]`).
 */
export function FloatingMascotLauncher({ name, label, caption, size = 'default', takeOverFrom, homeSlot, open = false, onOpen, onDragStart, buttonRef, portrait, children }: {
  /** Identifies the launcher: its saved position and its collapse selector. */
  name: string
  /** The button's accessible name, e.g. "Open command guide". */
  label: string
  /** The short tag under the portrait, e.g. "Guide". */
  caption: string
  /** `large` when Git-It itself is the main call to action, e.g. a finished run's next step. */
  size?: keyof typeof FLOATING_LAUNCHER_SIZES
  /** Launchers this one replaces: it first appears where the latest of them was last seen. */
  takeOverFrom?: readonly string[]
  /** Separated default spots for launchers that appear together; saved positions still win. */
  homeSlot?: FloatingHomeSlot
  open?: boolean
  onOpen: () => void
  onDragStart?: () => void
  buttonRef?: Ref<HTMLButtonElement>
  /** Optional character art for companion chat; other guides keep Git-It. */
  portrait?: ReactNode
  /** Controls pinned to the launcher, beside its button. */
  children?: ReactNode
}) {
  const box = FLOATING_LAUNCHER_SIZES[size]
  const storageKey = `mascot-launcher:${name}`
  const { position, dragging, handlers, clicked } = useFloatingPosition(
    storageKey,
    onDragStart,
    box,
    takeOverFrom?.map((other) => `mascot-launcher:${other}`),
    homeSlot,
  )

  useEffect(() => {
    if (!open) rememberShownPosition(storageKey, position, box)
  }, [box, open, position, storageKey])
  // Which half of the viewport it sits in, so pinned callouts open toward the middle.
  const side = position.x + box.width / 2 > window.innerWidth / 2 ? 'end' : 'start'

  return createPortal(
    <div
      className="mascot-launcher"
      style={{ left: position.x, top: position.y }}
      data-side={side}
      data-size={size === 'default' ? undefined : size}
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
        <span className="mascot-launcher__art">
          {portrait ?? <MascotPortrait className="mascot-launcher__portrait" alt="" width={72} height={90} />}
        </span>
        <span className="mascot-launcher__caption">{caption}</span>
      </button>
      {children}
    </div>,
    document.body,
  )
}
