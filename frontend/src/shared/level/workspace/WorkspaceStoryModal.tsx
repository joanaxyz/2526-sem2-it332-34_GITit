import { useEffect, useId, useRef } from 'react'

import { Modal } from '@/shared/components/Modal'
import { ScenarioInline } from '@/shared/level/components/ScenarioInline'
import { GuideCharacterPortrait } from '@/shared/mascot/GuideCharacterPortrait'

function StoryParagraphs({ text }: { text: string }) {
  return text.trim().split(/\n\s*\n/).filter(Boolean).map((paragraph, index) => (
    <p key={index}><ScenarioInline text={paragraph} /></p>
  ))
}

/**
 * An open briefing over the game world. Authored text stays intact; clicking
 * anywhere or pressing Enter, Space or Escape returns focus to the terminal.
 */
export function WorkspaceStoryModal({
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
  const introText = intro.trim()
  const taskText = task.trim()
  const hasStory = Boolean(introText || startingPointText || taskText || context || result)

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
      <div className="tier-story-modal__topbar" aria-hidden="true">
        <span className="tier-story-modal__badge">Mission Briefing</span>
      </div>

      <div className="tier-story-modal__layout" onClick={(event) => {
        // Selecting a path or passage should not dismiss the briefing.
        if (window.getSelection()?.toString().trim()) event.stopPropagation()
      }}>

        {/* Left — Guide character */}
        <div className="tier-story-modal__character" aria-hidden="true">
          <GuideCharacterPortrait
            className="tier-story-modal__portrait"
            alt=""
            width={200}
            height={250}
          />
        </div>

        {/* Center — title + task + situation */}
        <div className="tier-story-modal__center">
          <header className="tier-story-modal__header">
            <p className="tier-story-modal__title" aria-hidden="true">{title}</p>
          </header>

          {taskText ? (
            <section className="tier-story-modal__panel tier-story-modal__mission" aria-labelledby={`${headingId}-task`}>
              <h3 id={`${headingId}-task`} className="tier-story-modal__heading">Your task</h3>
              <StoryParagraphs text={taskText} />
            </section>
          ) : null}

          {introText ? (
            <section className="tier-story-modal__panel tier-story-modal__story" aria-labelledby={`${headingId}-situation`}>
              <h3 id={`${headingId}-situation`} className="tier-story-modal__heading">The situation</h3>
              <div className="tier-story-modal__prose">
                <StoryParagraphs text={introText} />
              </div>
            </section>
          ) : null}

          {hasStory ? null : <p className="tier-story-modal__empty">No story is available for this level.</p>}
        </div>

        {/* Right — reference panels */}
        {(startingPointText || result || context) ? (
          <div className="tier-story-modal__right">
            {startingPointText ? (
              <section className="tier-story-modal__panel" aria-labelledby={`${headingId}-starting-point`}>
                <h3 id={`${headingId}-starting-point`} className="tier-story-modal__heading">Starting point</h3>
                <StoryParagraphs text={startingPointText} />
              </section>
            ) : null}
            {result ? (
              <section className="tier-story-modal__panel" aria-labelledby={`${headingId}-expected-result`}>
                <h3 id={`${headingId}-expected-result`} className="tier-story-modal__heading">Expected result</h3>
                <StoryParagraphs text={result} />
              </section>
            ) : null}
            {context ? (
              <section className="tier-story-modal__panel tier-story-modal__context" aria-labelledby={`${headingId}-context`}>
                <h3 id={`${headingId}-context`} className="tier-story-modal__heading">Why this matters</h3>
                <StoryParagraphs text={context} />
              </section>
            ) : null}
          </div>
        ) : null}
      </div>

      <footer className="tier-story-modal__footer">
        <p className="tier-story-modal__continue">Begin Mission</p>
      </footer>
    </Modal>
  )
}
