import { ArrowUp, ShieldCheck, SquarePen } from 'lucide-react'
import { useEffect, useId, useRef, useState } from 'react'

import { useAuthStore } from '@/shared/auth/useAuth'
import { TutorMarkdown } from './TutorMarkdown'
import type { TutorContext } from './tutorApi'
import { useTutorChat, type TutorMessage } from './useTutorChat'
import './tutor.css'

export function TutorChatPanel({ context }: { context: TutorContext }) {
  const generation = useAuthStore((state) => state.sessionGeneration)
  const scope = `${generation}:${context.surface}:${context.run_id ?? ''}:${context.teaching_key ?? ''}`
  return <Conversation key={scope} context={context} scope={scope} />
}

function Conversation({ context, scope }: { context: TutorContext; scope: string }) {
  const chat = useTutorChat(context, scope)
  const [draft, setDraft] = useState('')
  const composerId = useId()
  const transcript = useRef<HTMLDivElement>(null)
  const composer = useRef<HTMLTextAreaElement>(null)
  useEffect(() => {
    const element = transcript.current
    if (element) element.scrollTop = element.scrollHeight
  }, [chat.messages, chat.pending])

  useEffect(() => {
    const element = composer.current
    if (!element) return
    element.style.height = 'auto'
    element.style.height = `${Math.min(element.scrollHeight, 160)}px`
  }, [draft])

  function submit() {
    if (!draft.trim() || chat.pending) return
    void chat.send(draft)
    setDraft('')
  }

  return (
    <div className="tutor-chat">
      {chat.messages.length ? (
        <div className="tutor-chat__actions">
          <button type="button" className="tutor-chat__reset" aria-label="Start a new conversation" onClick={() => { chat.clear(); composer.current?.focus() }}>
            <SquarePen size={15} aria-hidden="true" />
            New chat
          </button>
        </div>
      ) : null}

      <div
        ref={transcript}
        className="tutor-chat__transcript app-scrollbar"
        role="log"
        aria-label="Git-It conversation"
        aria-live="polite"
        aria-busy={chat.pending}
      >
        {chat.messages.length
          ? chat.messages.map((entry, index) => <Message key={index} entry={entry} home={context.surface === 'home'} />)
          : (
            <div className="tutor-chat__empty" data-tutor-selectable>
              <h3>What would you like to understand?</h3>
              <p>Ask what a command means, why it works, or which idea feels unclear.</p>
            </div>
          )}
        {chat.pending ? <p className="tutor-chat__pending" role="status" data-tutor-selectable><span aria-hidden="true" />Thinking…</p> : null}
      </div>

      {chat.error ? <p className="tutor-chat__error" role="alert" data-tutor-selectable>{chat.error}</p> : null}

      <form
        className="tutor-chat__composer"
        data-tutor-selectable
        onClick={(event) => { if (event.target === event.currentTarget) composer.current?.focus() }}
        onSubmit={(event) => { event.preventDefault(); submit() }}
      >
        <label className="sr-only" htmlFor={composerId}>Ask Git-It a question</label>
        <textarea
          ref={composer}
          id={composerId}
          value={draft}
          maxLength={4000}
          rows={1}
          placeholder="Ask anything about Git…"
          disabled={chat.pending}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
              event.preventDefault()
              submit()
            }
          }}
        />
        <button type="submit" aria-label="Send question" disabled={chat.pending || !draft.trim()}>
          <ArrowUp size={19} aria-hidden="true" />
        </button>
      </form>
    </div>
  )
}

function Message({ entry, home }: { entry: TutorMessage; home: boolean }) {
  const fromGitIt = entry.role === 'assistant'
  return (
    <article className={`tutor-chat__message tutor-chat__message--${entry.role}`} aria-label={fromGitIt ? 'Git-It' : 'You'}>
      <div className="tutor-chat__content" data-tutor-selectable>
        {/* Home declines a scenario that arrives from another tab; the workspace is always one. */}
        {fromGitIt && home && entry.reply.scenario_related ? (
          <p className="tutor-chat__guarded"><ShieldCheck size={13} aria-hidden="true" />Scenario spotted</p>
        ) : null}
        {fromGitIt
          ? <TutorMarkdown text={entry.text} />
          : entry.text.split(/\n{2,}/).map((paragraph, index) => <p key={index}>{paragraph}</p>)}
      </div>
    </article>
  )
}
