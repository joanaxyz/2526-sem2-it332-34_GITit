import { ArrowDown, Send, ShieldCheck, SquarePen } from 'lucide-react'
import { useEffect, useId, useRef, useState } from 'react'

import { useAuthStore } from '@/shared/auth/useAuth'
import { TutorMarkdown } from './TutorMarkdown'
import type { TutorContext } from './tutorApi'
import { useTutorChat, type TutorMessage } from './useTutorChat'
import { findOfflineFaq, OFFLINE_FAQS } from './offlineFaqs'
import { TutorRecoveryPanel } from './TutorRecoveryPanel'
import './tutor.css'

export function TutorChatPanel({ context }: { context: TutorContext }) {
  const generation = useAuthStore((state) => state.sessionGeneration)
  const scope = `${generation}:${context.surface}:${context.run_id ?? ''}:${context.teaching_key ?? ''}`
  return <Conversation key={scope} context={context} scope={scope} />
}

function Conversation({ context, scope }: { context: TutorContext; scope: string }) {
  const chat = useTutorChat(context, scope)
  const { draft, setDraft } = chat
  const [view, setView] = useState<'chat' | 'faq'>('chat')
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
    if (view === 'chat') composer.current?.focus()
    else faqButton.current?.focus()
  }, [view])

  useEffect(() => {
    const element = composer.current
    if (!element) return
    element.style.height = 'auto'
    element.style.height = `${Math.min(element.scrollHeight, 96)}px`
  }, [draft])

  async function submit() {
    if (!draft.trim() || chat.pending || chat.cooldown.blocked) return
    const question = draft.trim()
    const result = await chat.send(question)
    if (result === 'sent') composer.current?.focus()
  }

  return (
    <div className="tutor-chat">
      <div className="tutor-chat__actions">
        <button type="button" className="tutor-chat__reset" aria-pressed={view === 'chat'} onClick={() => setView('chat')}>Chat</button>
        <button ref={faqButton} type="button" className="tutor-chat__reset" aria-pressed={view === 'faq'} onClick={() => setView('faq')}>FAQS</button>
        {chat.messages.length || draft || chat.pending ? (
          <button type="button" className="tutor-chat__reset" aria-label="Start a new conversation" onClick={() => {
            chat.clear(); following.current = true; setNewMessages(false); setSelectedFaq(null)
            setView('chat'); composer.current?.focus()
          }}>
            <SquarePen size={15} aria-hidden="true" />
            New chat
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
            <div className="tutor-chat__welcome" data-tutor-selectable>
              <div className="tutor-chat__message tutor-chat__message--assistant">
                <span className="tutor-chat__speaker">Blue</span>
                <div className="tutor-chat__content"><p>Hi, I’m Blue. Ask me about Git concepts or how GIT it! works. I’ll help you reason through the ideas without giving scenario answers.</p></div>
              </div>
              <div className="tutor-chat__starters" aria-label="Suggested Git questions">
                <span className="tutor-chat__starters-title">Try asking</span>
                {['What is HEAD in Git?', 'How does staging work?', 'What happens during a merge conflict?'].map((question) => (
                  <button key={question} type="button" disabled={chat.pending || chat.cooldown.blocked || chat.offline} onClick={() => { setDraft(question); void chat.send(question) }}>{question}</button>
                ))}
              </div>
            </div>
          )}
        {chat.pending ? <div className="tutor-chat__message tutor-chat__message--assistant" role="status">
          <span className="tutor-chat__speaker">Blue</span>
          <span className="sr-only">Thinking...</span>
          <div className="tutor-chat__typing" aria-hidden="true"><i /><i /><i /></div>
        </div> : null}
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

      {view === 'chat' ? <TutorRecoveryPanel recovery={chat.recovery} remaining={chat.cooldown.remaining}
        pending={chat.pending} draft={draft} history={chat.messages} onRetry={() => { void submit() }} onFaqs={() => {
          setSelectedFaq(findOfflineFaq(draft, chat.messages)?.id ?? null); setView('faq')
        }} /> : null}

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
        <button type="submit" aria-label="Send question" disabled={chat.pending || chat.cooldown.blocked || chat.offline || !draft.trim()}>
          <Send size={17} aria-hidden="true" />
        </button>
      </form>
      <p className="tutor-chat__footer">Concept guidance only <span aria-hidden="true">·</span> No scenario answers</p>
    </div>
  )
}

function Message({ entry, home }: { entry: TutorMessage; home: boolean }) {
  const fromGitIt = entry.role === 'assistant'
  return (
    <article className={`tutor-chat__message tutor-chat__message--${entry.role}`} aria-label={fromGitIt ? 'Git-It' : 'You'}>
      {fromGitIt ? <span className="tutor-chat__speaker">Blue</span> : null}
      <div className="tutor-chat__content" data-tutor-selectable>
        {/* Home declines a scenario that arrives from another tab; the workspace is always one. */}
        {fromGitIt && home && entry.reply.scenario_related ? (
          <p className="tutor-chat__guarded"><ShieldCheck size={13} aria-hidden="true" />Scenario guidance</p>
        ) : null}
        {fromGitIt
          ? <TutorMarkdown text={entry.text} />
          : entry.text.split(/\n{2,}/).map((paragraph, index) => <p key={index}>{paragraph}</p>)}
      </div>
    </article>
  )
}
