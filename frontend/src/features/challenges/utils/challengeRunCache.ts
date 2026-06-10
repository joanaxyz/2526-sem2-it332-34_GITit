import type { QueryClient } from '@tanstack/react-query'

import { writeChallengeRunBootstrap } from '@/features/challenges/utils/challengeRunBootstrap'
import type { ChallengeRun } from '@/shared/practice/types'
import { queryKeyRoots, queryKeys } from '@/shared/api/queryKeys'

const challengeRunSyncChannel = 'git-it:challenge-run-sync'

type ChallengeRunSyncMessage = {
  type: 'challenge-run-updated'
  run: ChallengeRun
}

export function syncChallengeRunInCache(
  queryClient: QueryClient,
  run: ChallengeRun,
  options: { broadcast?: boolean } = {},
) {
  updateChallengeRunCache(queryClient, run)
  if (options.broadcast !== false && !run.review_mode) {
    broadcastChallengeRunSync(run)
  }

  invalidatePracticeProgressQueries(queryClient)
}

export function updateChallengeRunCache(queryClient: QueryClient, run: ChallengeRun) {
  writeChallengeRunBootstrap(run)
  queryClient.setQueryData(queryKeys.challengeRun(run.id), run)
}

export function subscribeToChallengeRunSync(queryClient: QueryClient) {
  if (typeof window === 'undefined') return () => {}

  const handleMessage = (message: unknown) => {
    if (!isChallengeRunSyncMessage(message)) return
    syncChallengeRunInCache(queryClient, message.run, { broadcast: false })
  }

  const channel = typeof BroadcastChannel !== 'undefined'
    ? new BroadcastChannel(challengeRunSyncChannel)
    : null
  const handleBroadcastMessage = (event: MessageEvent<unknown>) => handleMessage(event.data)
  channel?.addEventListener('message', handleBroadcastMessage)

  const handleStorage = (event: StorageEvent) => {
    if (event.key !== challengeRunSyncChannel || !event.newValue) return
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
  void queryClient.invalidateQueries({ queryKey: queryKeys.storeys })
  void queryClient.invalidateQueries({ queryKey: queryKeys.dashboardSummary })
  void queryClient.invalidateQueries({ queryKey: queryKeyRoots.storeyContent })
  void queryClient.invalidateQueries({ queryKey: queryKeys.wallet })
}

function broadcastChallengeRunSync(run: ChallengeRun) {
  if (typeof window === 'undefined') return
  const message: ChallengeRunSyncMessage = {
    type: 'challenge-run-updated',
    run,
  }
  if (typeof BroadcastChannel !== 'undefined') {
    const channel = new BroadcastChannel(challengeRunSyncChannel)
    channel.postMessage(message)
    channel.close()
  }
  try {
    window.localStorage.setItem(
      challengeRunSyncChannel,
      JSON.stringify({ ...message, sentAt: Date.now() }),
    )
  } catch {
    // Some browsers disable storage; BroadcastChannel is enough when available.
  }
}

function isChallengeRunSyncMessage(value: unknown): value is ChallengeRunSyncMessage {
  if (!value || typeof value !== 'object') return false
  const message = value as Partial<ChallengeRunSyncMessage>
  return message.type === 'challenge-run-updated' && Boolean(message.run)
}
