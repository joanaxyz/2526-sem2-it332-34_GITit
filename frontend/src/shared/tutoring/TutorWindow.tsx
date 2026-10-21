import { GripHorizontal, MoveDiagonal2 } from 'lucide-react'
import { useEffect, useId, useRef } from 'react'
import { createPortal } from 'react-dom'

import { MascotPortrait } from '@/shared/mascot/GuideCharacterPortrait'
import { TutorChatPanel } from './TutorChatPanel'
import type { TutorContext } from './tutorApi'
import { useTutorWindowLayout } from './useTutorWindowLayout'
import './tutor.css'

export type TutorWindowDismissal = 'escape' | 'outside'

// Keep the side mascot outside the panel, hiding it when there is no room beside it.
const SPEAKER_ROOM = 84
// Shorter windows keep only the conversation and the composer.
const COMPACT_HEIGHT = 450

/**
 * The floating, nonmodal "Ask Git-It" chat. Its background and side mascot drag it; its edges
 * resize it. Keyboard users get move and resize controls that show on focus.
 */
export function TutorWindow({ context, workspace = false, onDismiss }: {
  context: TutorContext
  /** Over the gameplay workspace, as the open command guide's companion. */
  workspace?: boolean
  /** When given, Escape or a click outside the window puts it away. */
  onDismiss?: (how: TutorWindowDismissal) => void
}) {
  const titleId = useId()
  const frame = useRef<HTMLDivElement>(null)
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
      data-speaker-hidden={rect.x < SPEAKER_ROOM || undefined}
      data-compact={rect.height < COMPACT_HEIGHT || undefined}
      {...frameHandlers}
    >
      <MascotPortrait className="tutor-window__speaker" alt="" width={54} height={68} />
      <section className="tutor-window__panel" role="dialog" aria-labelledby={titleId}>
        <header className="tutor-window__header">
          <div className="tutor-window__heading">
            <h2 id={titleId}>Ask Git-It</h2>
          </div>
          <button
            type="button"
            className="tutor-window__key-control"
            aria-label="Move AI chat window"
            title="Arrow keys move · Shift for larger steps · Home resets"
            onKeyDown={moveWithKeyboard}
          >
            <GripHorizontal aria-hidden="true" />
          </button>
        </header>
        <TutorChatPanel context={context} />
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
