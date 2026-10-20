import { ArrowRight, Flag, Lightbulb, MapPin, Target } from 'lucide-react'
import { useEffect, useId, useRef } from 'react'

import { Modal } from '@/shared/components/Modal'
import { ScenarioInline } from '@/shared/level/components/ScenarioInline'

/**
 * An open briefing over the game world. Authored text stays intact; clicking
 * anywhere or pressing Enter, Space or Escape returns focus to the terminal.
 */
export function TierStoryModal({
  open,
  title,
  intro,
  startingPoint,
  task,
  realWorldContext,
  expectedResult,
  onClose,
}: {
  open: boolean
  title: string
  intro: string
  startingPoint?: string
  task: string
  /** Why the skill matters outside the game; hidden when absent. */
  realWorldContext?: string
  expectedResult?: string
  onClose: () => void
}) {
  const headingId = useId()
  const onCloseRef = useRef(onClose)
  useEffect(() => {
    onCloseRef.current = onClose
  }, [onClose])

  const start = () => {
    onCloseRef.current()
    requestAnimationFrame(() => document.querySelector<HTMLInputElement>('[data-command-input]')?.focus())
  }

  const context = realWorldContext?.trim()
  const startingPointText = startingPoint?.trim()
  const result = expectedResult?.trim()
  const paragraphs = intro.trim().split(/\n\s*\n/).filter(Boolean)
  const taskText = task.trim()
  const hasStory = Boolean(paragraphs.length || startingPointText || taskText || context || result)

  return (
    <Modal
      open={open}
      title={title}
      onClose={start}
      hideHeader
      dismissOnClick
      className="tier-story-modal"
      overlayClassName="tier-story-overlay"
      contentClassName="tier-story-modal__body"
    >
      <div className="tier-story-modal__reading" onClick={(event) => {
        // Selecting a path or passage should not dismiss the briefing.
        if (window.getSelection()?.toString().trim()) event.stopPropagation()
      }}>
        <header className="tier-story-modal__header">
          <p className="tier-story-modal__eyebrow">Mission briefing</p>
          <p className="tier-story-modal__title" aria-hidden="true">{title}</p>
        </header>

        {taskText ? (
          <section className="tier-story-modal__mission" aria-labelledby={`${headingId}-task`}>
            <h3 id={`${headingId}-task`} className="tier-story-modal__heading"><Target aria-hidden="true" />Your task</h3>
            <p><ScenarioInline text={taskText} /></p>
          </section>
        ) : null}

        <div className={`tier-story-modal__spread${paragraphs.length ? ' has-story' : ''}${startingPointText || result ? ' has-reference' : ''}`}>
          {paragraphs.length ? (
            <section className="tier-story-modal__story" aria-labelledby={`${headingId}-situation`}>
              <h3 id={`${headingId}-situation`} className="tier-story-modal__heading">The situation</h3>
              <div className="tier-story-modal__prose">
                {paragraphs.map((paragraph, index) => <p key={index}><ScenarioInline text={paragraph} /></p>)}
              </div>
            </section>
          ) : null}

          {startingPointText || result ? (
            <div className="tier-story-modal__reference">
              {startingPointText ? (
                <section aria-labelledby={`${headingId}-starting-point`}>
                  <h3 id={`${headingId}-starting-point`} className="tier-story-modal__heading"><MapPin aria-hidden="true" />Starting point</h3>
                  <p><ScenarioInline text={startingPointText} /></p>
                </section>
              ) : null}
              {result ? (
                <section aria-labelledby={`${headingId}-expected-result`}>
                  <h3 id={`${headingId}-expected-result`} className="tier-story-modal__heading"><Flag aria-hidden="true" />Expected result</h3>
                  <p><ScenarioInline text={result} /></p>
                </section>
              ) : null}
            </div>
          ) : null}
        </div>

        {context ? (
          <section className="tier-story-modal__context" aria-labelledby={`${headingId}-context`}>
            <h3 id={`${headingId}-context`} className="tier-story-modal__heading"><Lightbulb aria-hidden="true" />Why this matters</h3>
            <p><ScenarioInline text={context} /></p>
          </section>
        ) : null}
        {hasStory ? null : <p className="tier-story-modal__empty">No story is available for this level.</p>}
      </div>

      <footer className="tier-story-modal__footer">
        <p className="tier-story-modal__continue">
          Click anywhere to begin <ArrowRight aria-hidden="true" />
        </p>
        <span className="tier-story-modal__keyboard">or press <kbd>Enter</kbd></span>
      </footer>
    </Modal>
  )
}
