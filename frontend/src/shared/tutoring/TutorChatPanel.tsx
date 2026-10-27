import { ArrowDown, ArrowUp, ShieldCheck, SquarePen } from 'lucide-react'
import { useEffect, useId, useRef, useState } from 'react'

import { useAuthStore } from '@/shared/auth/useAuth'
import { TutorMarkdown } from './TutorMarkdown'
import type { TutorContext } from './tutorApi'
import { useTutorChat, type TutorMessage } from './useTutorChat'
import { findOfflineFaq, OFFLINE_FAQS } from './offlineFaqs'
import './tutor.css'

export function TutorChatPanel({ context }: { context: TutorContext }) {
  const generation = useAuthStore((state) => state.sessionGeneration)
  const scope = `${generation}:${context.surface}:${context.run_id ?? ''}:${context.teaching_key ?? ''}`
  return <Conversation key={scope} context={context} scope={scope} />
}

function Conversation({ context, scope }: { context: TutorContext; scope: string }) {
  const chat = useTutorChat(context, scope)
  const { draft, setDraft } = chat
  const [offline, setOffline] = useState(() => !navigator.onLine)
  const [view, setView] = useState<'chat' | 'faq'>(() => navigator.onLine ? 'chat' : 'faq')
  const [notice, setNotice] = useState('')
  const [selectedFaq, setSelectedFaq] = useState<string | null>(null)
  const [newMessages, setNewMessages] = useState(false)
  const composerId = useId()
  const transcript = useRef<HTMLDivElement>(null)
  const composer = useRef<HTMLTextAreaElement>(null)
  const faqButton = useRef<HTMLButtonElement>(null)
  const following = useRef(true)

  useEffect(() => {
    const element = transcript.current
    if (following.current) {
      if (element && view === 'chat') element.scrollTop = element.scrollHeight
    } else if (chat.messages.at(-1)?.role === 'assistant') setNewMessages(true)
  }, [chat.messages, chat.pending, view])

  useEffect(() => {
    const update = () => {
      setOffline(!navigator.onLine)
      if (!navigator.onLine) {
        setView('faq')
        setNotice('You are offline. These saved explanations are available without AI.')
      } else {
        setNotice('Your connection is back. Return to Chat to send your saved question.')
      }
    }
    window.addEventListener('online', update)
    window.addEventListener('offline', update)
    return () => {
      window.removeEventListener('online', update)
      window.removeEventListener('offline', update)
    }
  }, [])

  useEffect(() => {
    if (view === 'chat') composer.current?.focus()
    else faqButton.current?.focus()
  }, [view])

  useEffect(() => {
    const element = composer.current
    if (!element) return
    element.style.height = 'auto'
    element.style.height = `${Math.min(element.scrollHeight, 160)}px`
  }, [draft])

  async function submit() {
    if (!draft.trim() || chat.pending) return
    const question = draft.trim()
    if (!navigator.onLine) {
      setSelectedFaq(findOfflineFaq(question)?.id ?? null)
      setNotice('You are offline. Your question is saved; browse these explanations while you wait.')
      setView('faq')
      return
    }
    setNotice('')
    const result = await chat.send(question)
    if (result === 'sent') composer.current?.focus()
    if (result === 'unavailable') {
      setSelectedFaq(findOfflineFaq(question)?.id ?? null)
      setNotice('AI help is unavailable. Your question is saved; browse these explanations or return to Chat to retry.')
      setView('faq')
    }
  }

  return (
    <div className="tutor-chat">
      <div className="tutor-chat__actions">
        <button type="button" className="tutor-chat__reset" aria-pressed={view === 'chat'} onClick={() => setView('chat')}>Chat</button>
        <button ref={faqButton} type="button" className="tutor-chat__reset" aria-pressed={view === 'faq'} onClick={() => setView('faq')}>Offline FAQs</button>
        {chat.messages.length || draft || chat.pending ? (
          <button type="button" className="tutor-chat__reset" aria-label="Start a new conversation" onClick={() => {
            chat.clear(); following.current = true; setNewMessages(false); setNotice(''); setSelectedFaq(null)
            setView(navigator.onLine ? 'chat' : 'faq'); composer.current?.focus()
          }}>
            <SquarePen size={15} aria-hidden="true" />
            New chat
          </button>
        ) : null}
      </div>

      {offline || notice ? <p className="tutor-chat__notice" role="status" data-tutor-selectable>
        {notice || 'You are offline. These saved explanations are available without AI.'}
      </p> : null}

      <div
        ref={transcript}
        className="tutor-chat__transcript app-scrollbar"
        role="log"
        aria-label="Git-It conversation"
        aria-live="polite"
        aria-busy={chat.pending}
        hidden={view !== 'chat'}
        onScroll={() => {
          const element = transcript.current
          if (!element) return
          following.current = element.scrollHeight - element.scrollTop - element.clientHeight < 48
          if (following.current) setNewMessages(false)
        }}
      >
        {chat.messages.length
          ? chat.messages.map((entry, index) => <Message key={index} entry={entry} home={context.surface === 'home'} />)
          : (
            <div className="tutor-chat__empty" data-tutor-selectable>
              <h3>What would you like to understand?</h3>
              <p>Ask what a command means, why it works, or which idea feels unclear.</p>
              <p>Questions about GIT it! are welcome too.</p>
            </div>
          )}
        {chat.pending ? <p className="tutor-chat__pending" role="status" data-tutor-selectable><span aria-hidden="true" />Thinking…</p> : null}
      </div>

      {view === 'chat' && newMessages ? <button type="button" className="tutor-chat__new-messages" onClick={() => {
        following.current = true; setNewMessages(false)
        if (transcript.current) transcript.current.scrollTop = transcript.current.scrollHeight
      }}><ArrowDown size={14} aria-hidden="true" />New message</button> : null}

      <section className="tutor-chat__faqs app-scrollbar" aria-label="Saved Git explanations" hidden={view !== 'faq'} data-tutor-selectable>
        <p className="tutor-chat__notice">Saved explanations, available without AI. These teach general Git concepts and do not solve scenario tasks.</p>
        {OFFLINE_FAQS.map((faq) => <details key={faq.id} open={selectedFaq === faq.id} onToggle={(event) => {
          if (event.currentTarget.open) setSelectedFaq(faq.id)
          else setSelectedFaq((current) => current === faq.id ? null : current)
        }}>
          <summary>{faq.question}</summary>
          <TutorMarkdown text={faq.answer} />
        </details>)}
      </section>

      {chat.error ? <p className="tutor-chat__error" role="alert" data-tutor-selectable>{chat.error}</p> : null}

      <form
        className="tutor-chat__composer"
        hidden={view !== 'chat'}
        data-tutor-selectable
        onClick={(event) => { if (event.target === event.currentTarget) composer.current?.focus() }}
        onSubmit={(event) => { event.preventDefault(); void submit() }}
      >
        <label className="sr-only" htmlFor={composerId}>Ask Git-It a question</label>
        <textarea
          ref={composer}
          id={composerId}
          value={draft}
          maxLength={4000}
          rows={1}
          placeholder="Ask about Git or GIT it!…"
          disabled={chat.pending}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
              event.preventDefault()
              void submit()
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
