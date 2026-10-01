import type { QueryClient } from '@tanstack/react-query'

import { writeChallengeRunBootstrap } from '@/features/challenges/utils/challengeRunBootstrap'
import type { ChallengeRun } from '@/features/challenges/types'
import { queryKeyRoots, queryKeys } from '@/shared/api/queryKeys'
import { useAuthStore } from '@/shared/auth/useAuth'

const challengeRunSyncChannel = 'git-it:challenge-run-sync'

type ChallengeRunSyncMessage = {
  type: 'challenge-run-updated'
  userId: number
  run: ChallengeRun
}

type CacheOwner = { userId: number | null; generation: number }
const cacheOwners = new WeakMap<QueryClient, CacheOwner>()

function cacheOwner(queryClient: QueryClient): CacheOwner {
  let owner = cacheOwners.get(queryClient)
  if (!owner) {
    const { sessionUserId, sessionGeneration } = useAuthStore.getState()
    owner = { userId: sessionUserId, generation: sessionGeneration }
    cacheOwners.set(queryClient, owner)
  }
  return owner
}

function isCurrentOwner(owner: CacheOwner) {
  const { accessToken, user, sessionUserId, sessionGeneration } = useAuthStore.getState()
  return Boolean(accessToken && user && user.id === owner.userId
    && sessionUserId === owner.userId && sessionGeneration === owner.generation)
}

export function syncChallengeRunInCache(
  queryClient: QueryClient,
  run: ChallengeRun,
  options: { broadcast?: boolean } = {},
) {
  const owner = cacheOwner(queryClient)
  if (!isCurrentOwner(owner) || owner.userId === null) return
  updateChallengeRunCache(queryClient, run)
  if (options.broadcast !== false && !run.replay) {
    broadcastChallengeRunSync(run, owner.userId)
  }

  invalidateLevelProgressQueries(queryClient)
}

export function updateChallengeRunCache(queryClient: QueryClient, run: ChallengeRun) {
  if (!isCurrentOwner(cacheOwner(queryClient))) return
  writeChallengeRunBootstrap(run)
  queryClient.setQueryData(queryKeys.challengeRun(run.id), run)
}

export function subscribeToChallengeRunSync(queryClient: QueryClient) {
  if (typeof window === 'undefined') return () => {}
  // Bind before confirmation completes; only this generation's confirmed
  // account may use the listener, even if React has not cleaned it up yet.
  const owner = cacheOwner(queryClient)

  const handleMessage = (message: unknown) => {
    if (!isChallengeRunSyncMessage(message) || message.userId !== owner.userId || !isCurrentOwner(owner)) return
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

export function invalidateLevelProgressQueries(queryClient: QueryClient) {
  void queryClient.invalidateQueries({ queryKey: queryKeys.chapters })
  void queryClient.invalidateQueries({ queryKey: queryKeys.homeSummary })
  void queryClient.invalidateQueries({ queryKey: queryKeys.statsSummary })
  void queryClient.invalidateQueries({ queryKey: queryKeyRoots.chapterOverview })
  void queryClient.invalidateQueries({ queryKey: queryKeys.learnedSkills })
  void queryClient.invalidateQueries({ queryKey: queryKeys.wallet })
}

function broadcastChallengeRunSync(run: ChallengeRun, userId: number) {
  if (typeof window === 'undefined') return
  const message: ChallengeRunSyncMessage = {
    type: 'challenge-run-updated',
    userId,
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
  return message.type === 'challenge-run-updated' && Number.isInteger(message.userId) && Boolean(message.run)
}
