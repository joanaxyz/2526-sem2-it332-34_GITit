import { useEffect, useRef, useState } from 'react'

import { useAuthStore } from '@/shared/auth/useAuth'
import { tutorApi, type TutorContext, type TutorReply } from './tutorApi'
import { errorRecovery, OFFLINE_RECOVERY, unavailableRecovery, type Recovery } from './tutorRecovery'
import { setTutorCooldown, useTutorCooldown } from './useTutorCooldown'

export type TutorMessage = { role: 'user'; text: string } | { role: 'assistant'; text: string; reply: TutorReply }
const conversations = new Map<string, TutorMessage[]>()
const drafts = new Map<string, string>()
const TUTOR_REQUEST_TIMEOUT_MS = 40000

useAuthStore.subscribe((current, previous) => {
  if (current.sessionGeneration !== previous.sessionGeneration) {
    conversations.clear()
    drafts.clear()
  }
})

export function useTutorChat(context: TutorContext, scope: string) {
  const [messages, setMessages] = useState<TutorMessage[]>(() => conversations.get(scope) ?? [])
  const [pending, setPending] = useState(false)
  const [recovery, setRecovery] = useState<Recovery | null>(null)
  const [offline, setOffline] = useState(() => !navigator.onLine)
  const [draft, updateDraft] = useState(() => drafts.get(scope) ?? '')
  const cooldown = useTutorCooldown()
  const controller = useRef<AbortController | null>(null)
  const messagesRef = useRef(messages)
  const scopeRef = useRef(scope)
  messagesRef.current = messages
  scopeRef.current = scope
  useEffect(() => () => { controller.current?.abort() }, [])
  useEffect(() => useAuthStore.subscribe((current, previous) => {
    if (current.sessionGeneration !== previous.sessionGeneration) controller.current?.abort()
  }), [])
  useEffect(() => {
    const update = () => {
      setOffline(!navigator.onLine)
      if (navigator.onLine) setRecovery((current) => current?.reason === 'offline' ? null : current)
    }
    window.addEventListener('online', update)
    window.addEventListener('offline', update)
    return () => {
      window.removeEventListener('online', update)
      window.removeEventListener('offline', update)
    }
  }, [])

  function remember(next: TutorMessage[]) {
    const bounded = next.slice(-20)
    conversations.set(scope, bounded)
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

  function recover(next: Recovery) {
    if (next.retrySeconds) setTutorCooldown(next.retrySeconds)
    setRecovery(next)
  }

  async function send(text: string): Promise<'sent' | 'unavailable' | 'failed' | 'cancelled'> {
    const message = text.trim()
    if (!message || controller.current || cooldown.blocked) return 'cancelled'
    if (message.length > 4000) {
      recover({ reason: 'validation', message: 'Please keep your question between 1 and 4,000 characters.', canRetry: false })
      return 'failed'
    }
    if (!navigator.onLine) { recover(OFFLINE_RECOVERY); return 'unavailable' }
    const request = new AbortController()
    controller.current = request
    const generation = useAuthStore.getState().sessionGeneration
    const before = messagesRef.current
    let timedOut = false
    let timer: ReturnType<typeof setTimeout> | undefined
    let cancel: (() => void) | undefined
    const isCurrent = () => controller.current === request && (!request.signal.aborted || timedOut)
      && generation === useAuthStore.getState().sessionGeneration && scopeRef.current === scope
    const history = before.slice(-20).map((entry) => ({ role: entry.role, text: entry.text.slice(0, 6000) }))
    while (history.reduce((total, turn) => total + turn.text.length, 0) > 32000) history.shift()
    setMessages([...before, { role: 'user', text: message }])
    setPending(true)
    setRecovery(null)
    try {
      // A race also settles a stalled response body or a transport ignoring abort.
      const deadline = new Promise<never>((_resolve, reject) => {
        cancel = () => { clearTimeout(timer); reject(new Error('Tutor cancelled')) }
        request.signal.addEventListener('abort', cancel, { once: true })
        timer = setTimeout(() => { timedOut = true; request.abort(); reject(new Error('Tutor deadline')) }, TUTOR_REQUEST_TIMEOUT_MS)
      })
      const reply = await Promise.race([tutorApi.chat({ message, context, history }, request.signal), deadline])
      if (!isCurrent()) return 'cancelled'
      if (!reply || typeof reply.reply !== 'string' || !reply.reply.trim()
        || !['answer', 'guarded', 'unavailable'].includes(reply.response_kind)) throw new Error('Invalid tutor response')
      if (reply.response_kind === 'unavailable') {
        remember(before)
        recover(unavailableRecovery(reply.unavailable_reason, reply.retry_after_seconds))
        return 'unavailable'
      }
      remember([...before, { role: 'user', text: message }, { role: 'assistant', text: reply.reply, reply }])
      setDraft('')
      return 'sent'
    } catch (failure) {
      if (!isCurrent()) return 'cancelled'
      remember(before)
      const next = timedOut ? unavailableRecovery('timeout')
        : !navigator.onLine ? OFFLINE_RECOVERY : errorRecovery(failure, context.surface === 'command_guide')
      recover(next)
      return next.canRetry ? 'unavailable' : 'failed'
    } finally {
      clearTimeout(timer)
      if (cancel) request.signal.removeEventListener('abort', cancel)
      if (controller.current === request) {
        controller.current = null
        setPending(false)
      }
    }
  }

  function clear() {
    controller.current?.abort()
    controller.current = null
    remember([])
    setPending(false)
    setRecovery(null)
    setDraft('')
  }

  const visibleRecovery = offline ? OFFLINE_RECOVERY : recovery
    ?? (cooldown.blocked ? { ...unavailableRecovery('rate_limited'), message: 'Git-It needs a short break. You can browse FAQS while you wait.' } : null)
  return { messages, pending, recovery: visibleRecovery, offline, cooldown, draft, setDraft, send, clear }
}
