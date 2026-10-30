import { ArrowDown, Send, ShieldCheck, SquarePen } from 'lucide-react'
import { useEffect, useId, useRef, useState } from 'react'
import type { ReactNode } from 'react'

import { useAuthStore } from '@/shared/auth/useAuth'
import { getCompanion } from '@/shared/cosmetics/companions/registry'
import type { CompanionDef } from '@/shared/cosmetics/types'
import { TutorMarkdown } from './TutorMarkdown'
import type { TutorContext } from './tutorApi'
import { useTutorChat, type TutorMessage } from './useTutorChat'
import { findOfflineFaq, OFFLINE_FAQS } from './offlineFaqs'
import { TutorRecoveryPanel } from './TutorRecoveryPanel'
import './tutor.css'

type TutorChatPanelProps = {
  context: TutorContext
  companion?: CompanionDef
  onPendingChange?: (pending: boolean) => void
  /** The window's title and close button share the panel's top bar with its tabs. */
  heading?: ReactNode
  headerEnd?: ReactNode
}

export function TutorChatPanel({ companion = getCompanion('blue'), ...props }: TutorChatPanelProps) {
  const generation = useAuthStore((state) => state.sessionGeneration)
  const { context } = props
  const scope = `${generation}:${context.surface}:${context.run_id ?? ''}:${context.teaching_key ?? ''}`
  return <Conversation key={scope} {...props} scope={scope} companion={companion} />
}

function Conversation({ context, scope, companion, onPendingChange, heading, headerEnd }: TutorChatPanelProps & { scope: string; companion: CompanionDef }) {
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
    onPendingChange?.(chat.pending)
    return () => onPendingChange?.(false)
  }, [chat.pending, onPendingChange])

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
      {chat.pending ? <span className="sr-only" role="status">{companion.label} is thinking</span> : null}
      <header className="tutor-chat__bar">
        {heading}
        <div className="tutor-chat__tabs">
          <button type="button" aria-pressed={view === 'chat'} onClick={() => setView('chat')}>Chat</button>
          <button ref={faqButton} type="button" aria-pressed={view === 'faq'} onClick={() => setView('faq')}>FAQS</button>
        </div>
        <div className="tutor-chat__bar-end">
          {chat.messages.length || draft || chat.pending ? (
            <button type="button" className="tutor-chat__icon-button" aria-label="Start a new conversation" title="New chat" onClick={() => {
              chat.clear(); following.current = true; setNewMessages(false); setSelectedFaq(null)
              setView('chat'); composer.current?.focus()
            }}>
              <SquarePen size={16} aria-hidden="true" />
            </button>
          ) : null}
          {headerEnd}
        </div>
      </header>

      <div
        ref={transcript}
        className="tutor-chat__transcript app-scrollbar"
        role="log"
        aria-label={`${companion.label} conversation`}
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
          ? chat.messages.map((entry, index) => <Message key={index} entry={entry} home={context.surface === 'home'} companionName={companion.label} />)
          : (
            <div className="tutor-chat__welcome" data-tutor-selectable>
              <div className="tutor-chat__message tutor-chat__message--assistant">
                <div className="tutor-chat__content"><p>Hi, I’m {companion.label}. Ask me about Git concepts or how GIT it! works. I’ll help you reason through the ideas without giving scenario answers.</p></div>
              </div>
              <div className="tutor-chat__starters" aria-label="Suggested Git questions">
                <span className="tutor-chat__starters-title">Try asking</span>
                {['What is HEAD in Git?', 'How does staging work?', 'What happens during a merge conflict?'].map((question) => (
                  <button key={question} type="button" disabled={chat.pending || chat.cooldown.blocked || chat.offline} onClick={() => { setDraft(question); void chat.send(question) }}>{question}</button>
                ))}
              </div>
            </div>
          )}
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
        <label className="sr-only" htmlFor={composerId}>Ask {companion.label} a question</label>
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
    </div>
  )
}

function Message({ entry, home, companionName }: { entry: TutorMessage; home: boolean; companionName: string }) {
  const fromGitIt = entry.role === 'assistant'
  return (
    <article className={`tutor-chat__message tutor-chat__message--${entry.role}`} aria-label={fromGitIt ? companionName : 'You'}>
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
