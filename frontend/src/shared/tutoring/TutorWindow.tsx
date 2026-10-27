import { X } from 'lucide-react'
import { useEffect, useId, useRef } from 'react'
import { createPortal } from 'react-dom'

import { MascotPortrait } from '@/shared/mascot/GuideCharacterPortrait'
import { TutorChatPanel } from './TutorChatPanel'
import type { TutorContext } from './tutorApi'
import './tutor.css'

export type TutorWindowDismissal = 'escape' | 'outside' | 'close'

/** Fixed chat panel shared by general help and the open command guide. */
export function TutorWindow({ context, workspace = false, onDismiss }: {
  context: TutorContext
  /** Over the gameplay workspace, as the open command guide's companion. */
  workspace?: boolean
  /** When given, the close button, Escape or a click outside the window puts it away. */
  onDismiss?: (how: TutorWindowDismissal) => void
}) {
  const titleId = useId()
  const frame = useRef<HTMLDivElement>(null)

  useEffect(() => {
    frame.current?.querySelector('textarea')?.focus()
  }, [])

  useEffect(() => {
    if (!onDismiss) return
    const dismissOnEscape = (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return
      event.preventDefault()
      // Only the chat closes, not a tour that is open behind it.
      event.stopPropagation()
      onDismiss('escape')
    }
    const dismissOnOutsidePointer = (event: PointerEvent) => {
      if (!frame.current?.contains(event.target as Node)) onDismiss('outside')
    }
    document.addEventListener('keydown', dismissOnEscape)
    document.addEventListener('pointerdown', dismissOnOutsidePointer)
    return () => {
      document.removeEventListener('keydown', dismissOnEscape)
      document.removeEventListener('pointerdown', dismissOnOutsidePointer)
    }
  }, [onDismiss])

  return createPortal(
    <div
      ref={frame}
      className={`tutor-window${workspace ? ' tutor-window--workspace' : ''}`}
    >
      <section className="tutor-window__panel" role="dialog" aria-labelledby={titleId}>
        <header className="tutor-window__header">
          <span className="tutor-window__portrait" aria-hidden="true">
            <MascotPortrait alt="" width={40} height={40} />
          </span>
          <div className="tutor-window__heading">
            <h2 id={titleId}>Ask Blue</h2>
            <p className="tutor-window__subtitle">Conceptual Git help <span aria-hidden="true">·</span> {workspace ? 'Command guide' : 'GIT it!'}</p>
          </div>
          {onDismiss ? (
            <button
              type="button"
              className="tutor-window__close"
              aria-label="Close Ask Blue"
              title="Close"
              onClick={() => onDismiss('close')}
            >
              <X aria-hidden="true" />
            </button>
          ) : null}
        </header>
        <TutorChatPanel context={context} />
      </section>
    </div>,
    document.body,
  )
}
