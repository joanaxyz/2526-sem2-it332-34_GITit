import type { QueryClient } from '@tanstack/react-query'

import type { PracticeSession } from '@/features/practice/types'
import { writeSessionBootstrap } from '@/features/practice/utils/sessionBootstrap'
import { queryKeyRoots, queryKeys } from '@/shared/api/queryKeys'

const practiceSessionSyncChannel = 'git-it:practice-session-sync'

type PracticeSessionSyncMessage = {
  type: 'practice-session-updated'
  session: PracticeSession
}

export function syncPracticeSessionInCache(
  queryClient: QueryClient,
  session: PracticeSession,
  options: { broadcast?: boolean } = {},
) {
  updatePracticeSessionCache(queryClient, session)
  if (options.broadcast !== false && !session.review_mode) {
    broadcastPracticeSessionSync(session)
  }

  invalidatePracticeProgressQueries(queryClient)
}

export function updatePracticeSessionCache(queryClient: QueryClient, session: PracticeSession) {
  writeSessionBootstrap(session)
  queryClient.setQueryData(queryKeys.practiceSession(session.id), session)
}

export function subscribeToPracticeSessionSync(queryClient: QueryClient) {
  if (typeof window === 'undefined') return () => {}

  const handleMessage = (message: unknown) => {
    if (!isPracticeSessionSyncMessage(message)) return
    syncPracticeSessionInCache(queryClient, message.session, { broadcast: false })
  }

  const channel = typeof BroadcastChannel !== 'undefined'
    ? new BroadcastChannel(practiceSessionSyncChannel)
    : null
  const handleBroadcastMessage = (event: MessageEvent<unknown>) => handleMessage(event.data)
  channel?.addEventListener('message', handleBroadcastMessage)

  const handleStorage = (event: StorageEvent) => {
    if (event.key !== practiceSessionSyncChannel || !event.newValue) return
    try {
      handleMessage(JSON.parse(event.newValue))
    } catch {
      // Ignore malformed cross-tab messages.
    }
  }
  window.addEventListener('storage', handleStorage)

  return () => {
    channel?.removeEventListener('message', handleBroadcastMessage)
    channel?.close()
    window.removeEventListener('storage', handleStorage)
  }
}

export function invalidatePracticeProgressQueries(queryClient: QueryClient) {
  void queryClient.invalidateQueries({ queryKey: queryKeys.modules })
  void queryClient.invalidateQueries({ queryKey: queryKeys.dashboardSummary })
  void queryClient.invalidateQueries({ queryKey: queryKeyRoots.moduleContent })
}

function broadcastPracticeSessionSync(session: PracticeSession) {
  if (typeof window === 'undefined') return
  const message: PracticeSessionSyncMessage = {
    type: 'practice-session-updated',
    session,
  }
  if (typeof BroadcastChannel !== 'undefined') {
    const channel = new BroadcastChannel(practiceSessionSyncChannel)
    channel.postMessage(message)
    channel.close()
  }
  try {
    window.localStorage.setItem(
      practiceSessionSyncChannel,
      JSON.stringify({ ...message, sentAt: Date.now() }),
    )
  } catch {
    // Some browsers disable storage; BroadcastChannel is enough when available.
  }
}

function isPracticeSessionSyncMessage(value: unknown): value is PracticeSessionSyncMessage {
  if (!value || typeof value !== 'object') return false
  const message = value as Partial<PracticeSessionSyncMessage>
  return message.type === 'practice-session-updated' && Boolean(message.session)
}
