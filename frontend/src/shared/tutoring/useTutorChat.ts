import { useEffect, useRef, useState } from 'react'

import { useAuthStore } from '@/shared/auth/useAuth'
import { ApiError } from '@/shared/api/apiError'
import { tutorApi, type TutorContext, type TutorReply } from './tutorApi'

export type TutorMessage = { role: 'user'; text: string } | { role: 'assistant'; text: string; reply: TutorReply }
const conversations = new Map<string, TutorMessage[]>()
const drafts = new Map<string, string>()

// A conversation belongs to one sign-in lifetime, including across mounted views.
useAuthStore.subscribe((current, previous) => {
  if (current.sessionGeneration !== previous.sessionGeneration) {
    conversations.clear()
    drafts.clear()
  }
})

export function useTutorChat(context: TutorContext, scope: string) {
  const [messages, setMessages] = useState<TutorMessage[]>(() => conversations.get(scope) ?? [])
  const [pending, setPending] = useState(false)
  const [error, setError] = useState('')
  const [draft, updateDraft] = useState(() => drafts.get(scope) ?? '')
  const controller = useRef<AbortController | null>(null)
  const messagesRef = useRef(messages)
  const scopeRef = useRef(scope)
  messagesRef.current = messages
  scopeRef.current = scope
  useEffect(() => () => { controller.current?.abort() }, [])
  useEffect(() => useAuthStore.subscribe((current, previous) => {
    if (current.sessionGeneration !== previous.sessionGeneration) controller.current?.abort()
  }), [])

  function remember(next: TutorMessage[]) {
    const bounded = next.slice(-20)
    conversations.set(scope, bounded)
    // Keep session memory bounded even after browsing many guides.
    if (conversations.size > 24) conversations.delete(conversations.keys().next().value!)
    messagesRef.current = bounded
    setMessages(bounded)
  }

  function setDraft(value: string) {
    if (value) drafts.set(scope, value)
    else drafts.delete(scope)
    if (drafts.size > 24) drafts.delete(drafts.keys().next().value!)
    updateDraft(value)
  }

  async function send(text: string): Promise<'sent' | 'unavailable' | 'failed' | 'cancelled'> {
    const message = text.trim()
    if (!message || message.length > 4000 || controller.current) return 'cancelled'
    const request = new AbortController()
    controller.current = request
    const generation = useAuthStore.getState().sessionGeneration
    const before = messagesRef.current
    const isCurrent = () => !request.signal.aborted
      && generation === useAuthStore.getState().sessionGeneration && scopeRef.current === scope
    // Both sides travel, so "what do you mean?" can refer to Git-It's last answer.
    const history = before.slice(-20).map((entry) => ({ role: entry.role, text: entry.text.slice(0, 6000) }))
    while (history.reduce((total, turn) => total + turn.text.length, 0) > 32000) history.shift()
    // Only completed exchanges enter session memory or the next provider request.
    setMessages([...before, { role: 'user', text: message }])
    setPending(true)
    setError('')
    try {
      const reply = await tutorApi.chat({ message, context, history }, request.signal)
      if (!isCurrent()) return 'cancelled'
      if (reply.response_kind === 'unavailable') {
        remember(before)
        setError(reply.reply)
        return 'unavailable'
      }
      remember([...before, { role: 'user', text: message }, { role: 'assistant', text: reply.reply, reply }])
      setDraft('')
      return 'sent'
    } catch (failure) {
      if (!isCurrent()) return 'cancelled'
      remember(before)
      const unavailable = !(failure instanceof ApiError) || failure.status === 429 || failure.status >= 500
      setError(failure instanceof ApiError && failure.status === 429
        ? 'Git-It is busy. Your question is saved; try again shortly.'
        : unavailable ? 'Help could not be reached. Your question is saved.'
          : 'Your question could not be sent. Reopen the guide or check your session and try again.')
      return unavailable ? 'unavailable' : 'failed'
    } finally {
      if (!request.signal.aborted) setPending(false)
      if (controller.current === request) controller.current = null
    }
  }

  function clear() {
    controller.current?.abort()
    controller.current = null
    remember([])
    setPending(false)
    setError('')
    setDraft('')
  }

  return { messages, pending, error, draft, setDraft, send, clear }
}
