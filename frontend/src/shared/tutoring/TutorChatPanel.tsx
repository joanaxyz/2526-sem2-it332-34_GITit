import { ArrowUp, RotateCcw } from 'lucide-react'
import { useEffect, useId, useRef, useState } from 'react'

import { useAuthStore } from '@/shared/auth/useAuth'
import { MascotPortrait } from '@/shared/mascot/GuideCharacterPortrait'
import type { TutorContext } from './tutorApi'
import { useTutorChat, type TutorMessage } from './useTutorChat'
import './tutor.css'

const STARTER_TOPICS = [
  { id: 'repository', title: 'Repository' },
  { id: 'staging', title: 'Staging area' },
  { id: 'placeholders', title: 'Placeholders' },
]

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
  useEffect(() => {
    const element = transcript.current
    if (element) element.scrollTop = element.scrollHeight
  }, [chat.messages, chat.pending])

  function submit() {
    if (!draft.trim() || chat.pending) return
    void chat.send(draft)
    setDraft('')
  }

  const lastReply = chat.messages.findLast((entry) => entry.role === 'assistant')
  const topics = lastReply?.role === 'assistant' ? lastReply.reply.suggested_topics.slice(0, 4) : STARTER_TOPICS

  return (
    <div className="tutor-chat">
      <div className="tutor-chat__intro">
        <p>Understand Git, one question at a time.</p>
        <span>I explain concepts and placeholders. You choose the solution.</span>
        {chat.messages.length ? (
          <button type="button" className="tutor-chat__reset" aria-label="Start a new conversation" onClick={chat.clear}>
            <RotateCcw size={15} />
          </button>
        ) : null}
      </div>

      <div
        ref={transcript}
        className="tutor-chat__transcript app-scrollbar"
        role="log"
        aria-label="Git-It conversation"
        aria-live="polite"
        aria-busy={chat.pending}
      >
        {chat.messages.length
          ? chat.messages.map((entry, index) => <Message key={index} entry={entry} />)
          : <p className="tutor-chat__empty">Ask what a command means, why it works, or which idea feels unclear.</p>}
        {chat.pending ? <p className="tutor-chat__pending" role="status">Finding an explanation…</p> : null}
      </div>

      <div className="tutor-chat__topics" aria-label="Topics to explore">
        {topics.map((topic) => (
          <button key={topic.id} type="button" disabled={chat.pending} onClick={() => void chat.send(`Explain ${topic.title}`)}>
            {topic.title}
          </button>
        ))}
      </div>

      {chat.error ? <p className="tutor-chat__error" role="alert">{chat.error}</p> : null}

      <form className="tutor-chat__composer" onSubmit={(event) => { event.preventDefault(); submit() }}>
        <label className="sr-only" htmlFor={composerId}>Ask Git-It a question</label>
        <textarea
          id={composerId}
          value={draft}
          maxLength={4000}
          rows={2}
          placeholder="What would you like to understand?"
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
          <ArrowUp size={19} />
        </button>
      </form>
      <p className="tutor-chat__footnote">Enter to send · Shift + Enter for a new line</p>
    </div>
  )
}

function Message({ entry }: { entry: TutorMessage }) {
  const fromGitIt = entry.role === 'assistant'
  return (
    <div className={`tutor-chat__message tutor-chat__message--${entry.role}`}>
      {fromGitIt ? <MascotPortrait className="tutor-chat__avatar" alt="" width={30} height={38} /> : null}
      <div className="tutor-chat__bubble">
        <strong>{fromGitIt ? 'Git-It' : 'You'}</strong>
        <p>{entry.text}</p>
        {fromGitIt && entry.reply.sources.length ? (
          <details className="tutor-chat__sources">
            <summary>Teaching sources</summary>
            <ul>{entry.reply.sources.map((source) => <li key={source.id}>{source.title}</li>)}</ul>
          </details>
        ) : null}
      </div>
    </div>
  )
}
