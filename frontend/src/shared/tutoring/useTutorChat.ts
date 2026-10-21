import { useEffect, useRef, useState } from 'react'

import { useAuthStore } from '@/shared/auth/useAuth'
import { tutorApi, type TutorContext, type TutorReply } from './tutorApi'

export type TutorMessage = { role: 'user'; text: string } | { role: 'assistant'; text: string; reply: TutorReply }
const conversations = new Map<string, TutorMessage[]>()

// A conversation belongs to one sign-in lifetime, including across mounted views.
useAuthStore.subscribe((current, previous) => {
  if (current.sessionGeneration !== previous.sessionGeneration) conversations.clear()
})

export function useTutorChat(context: TutorContext, scope: string) {
  const [messages, setMessages] = useState<TutorMessage[]>(() => conversations.get(scope) ?? [])
  const [pending, setPending] = useState(false)
  const [error, setError] = useState('')
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

  async function send(text: string) {
    const message = text.trim()
    if (!message || message.length > 4000 || controller.current) return
    const request = new AbortController()
    controller.current = request
    const generation = useAuthStore.getState().sessionGeneration
    const before = messagesRef.current
    const history = before.filter((entry) => entry.role === 'user').map((entry) => entry.text).slice(-8)
    while (history.join('').length > 12000) history.shift()
    remember([...before, { role: 'user', text: message }])
    setPending(true)
    setError('')
    try {
      const reply = await tutorApi.chat({ message, context, history }, request.signal)
      if (request.signal.aborted || generation !== useAuthStore.getState().sessionGeneration || scopeRef.current !== scope) return
      remember([...messagesRef.current, { role: 'assistant', text: reply.reply, reply }])
    } catch {
      if (!request.signal.aborted && generation === useAuthStore.getState().sessionGeneration) {
        setError('Help could not be reached. Please try again in a moment.')
      }
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
  }

  return { messages, pending, error, send, clear }
}
