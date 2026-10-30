import { GripHorizontal, MoveDiagonal2, X } from 'lucide-react'
import { useEffect, useId, useRef, useState } from 'react'
import { createPortal } from 'react-dom'

import type { CompanionDef } from '@/shared/cosmetics/types'
import { TutorChatPanel } from './TutorChatPanel'
import { TutorCompanionPortrait } from './TutorCompanionPortrait'
import type { TutorContext } from './tutorApi'
import { useTutorWindowLayout } from './useTutorWindowLayout'
import './tutor.css'

export type TutorWindowDismissal = 'escape' | 'outside' | 'close'

// The companion sits outside the panel, to its left; it hides when there is no room there.
const AVATAR_ROOM = 144

/**
 * The floating, nonmodal chat shared by general help and the open command guide.
 * Its background and the companion beside it drag it; its edges resize it.
 * Keyboard users get move and resize controls that show on focus.
 */
export function TutorWindow({ companion, context, workspace = false, onDismiss }: {
  companion: CompanionDef
  context: TutorContext
  /** Over the gameplay workspace, as the open command guide's companion. */
  workspace?: boolean
  /** When given, the close button, Escape or a click outside the window puts it away. */
  onDismiss?: (how: TutorWindowDismissal) => void
}) {
  const titleId = useId()
  const frame = useRef<HTMLDivElement>(null)
  const [thinking, setThinking] = useState(false)
  const { rect, cursor, frameHandlers, moveWithKeyboard, resizeWithKeyboard } = useTutorWindowLayout(workspace)

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
      style={{ left: rect.x, top: rect.y, width: rect.width, height: rect.height, cursor: cursor ?? undefined }}
      data-cursor={cursor ? '' : undefined}
      data-avatar-hidden={rect.x < AVATAR_ROOM || undefined}
      {...frameHandlers}
    >
      <span className="tutor-window__avatar" aria-hidden="true">
        <TutorCompanionPortrait companion={companion} thinking={thinking} />
      </span>
      <span className="tutor-window__tail" aria-hidden="true" />
      <section className="tutor-window__panel" role="dialog" aria-labelledby={titleId}>
        <TutorChatPanel
          companion={companion}
          context={context}
          onPendingChange={setThinking}
          heading={<h2 id={titleId} className="tutor-window__title">Ask {companion.label}</h2>}
          headerEnd={(
            <>
              <button
                type="button"
                className="tutor-window__key-control"
                aria-label="Move AI chat window"
                title="Arrow keys move · Shift for larger steps · Home resets"
                onKeyDown={moveWithKeyboard}
              >
                <GripHorizontal aria-hidden="true" />
              </button>
              {onDismiss ? (
                <button
                  type="button"
                  className="tutor-chat__icon-button"
                  aria-label={`Close Ask ${companion.label}`}
                  title="Close"
                  onClick={() => onDismiss('close')}
                >
                  <X aria-hidden="true" />
                </button>
              ) : null}
            </>
          )}
        />
        <button
          type="button"
          className="tutor-window__key-control tutor-window__resize"
          aria-label="Resize AI chat window"
          title="Arrow keys resize · Shift for larger steps · Home resets"
          onKeyDown={resizeWithKeyboard}
        >
          <MoveDiagonal2 aria-hidden="true" />
        </button>
      </section>
    </div>,
    document.body,
  )
}
