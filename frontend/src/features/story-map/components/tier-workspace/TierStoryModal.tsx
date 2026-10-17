import { useEffect, useRef } from 'react'

import { Button } from '@/shared/components/Button'
import { Modal } from '@/shared/components/Modal'

/**
 * The level briefing. Every string comes from the run; each section is left
 * out when its text is missing. Escape and the close button come from Modal;
 * Ctrl/Cmd+Enter or the primary action start the level with the terminal
 * focused.
 */
export function TierStoryModal({
  open,
  title,
  intro,
  task,
  realWorldContext,
  onClose,
}: {
  open: boolean
  title: string
  intro: string
  task: string
  /** Why the skill matters outside the game; hidden when absent. */
  realWorldContext?: string
  onClose: () => void
}) {
  const onCloseRef = useRef(onClose)
  useEffect(() => {
    onCloseRef.current = onClose
  }, [onClose])

  const start = () => {
    onCloseRef.current()
    requestAnimationFrame(() => document.querySelector<HTMLInputElement>('[data-command-input]')?.focus())
  }

  useEffect(() => {
    if (!open) return
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key !== 'Enter' || !(event.ctrlKey || event.metaKey)) return
      event.preventDefault()
      onCloseRef.current()
      requestAnimationFrame(() => document.querySelector<HTMLInputElement>('[data-command-input]')?.focus())
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [open])

  const context = realWorldContext?.trim()
  const hasStory = Boolean(intro || task || context)

  return (
    <Modal
      open={open}
      title={title}
      onClose={onClose}
      className="tier-story-modal w-full max-w-2xl"
      contentClassName="tier-story-modal__body"
    >
      {intro ? <p className="tier-story-modal__intro">{intro}</p> : null}
      {context ? (
        <section className="tier-story-modal__section" aria-labelledby="tier-story-context">
          <h3 id="tier-story-context" className="tier-story-modal__heading">Real-world context</h3>
          <p>{context}</p>
        </section>
      ) : null}
      {task ? (
        <section className="tier-story-modal__section tier-story-modal__section--task" aria-labelledby="tier-story-task">
          <h3 id="tier-story-task" className="tier-story-modal__heading">Your task</h3>
          <p>{task}</p>
        </section>
      ) : null}
      {hasStory ? null : <p className="tier-story-modal__empty">No story is available for this level.</p>}

      <div className="tier-story-modal__actions">
        <Button type="button" onClick={start}>
          Start coding
          <kbd className="tier-story-modal__shortcut" aria-hidden="true">Ctrl+Enter</kbd>
        </Button>
      </div>
    </Modal>
  )
}
