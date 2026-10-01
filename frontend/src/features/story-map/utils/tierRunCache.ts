import type { QueryClient } from '@tanstack/react-query'

import { writeTierRunBootstrap } from '@/features/story-map/utils/tierRunBootstrap'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { queryKeyRoots, queryKeys } from '@/shared/api/queryKeys'
import { useAuthStore } from '@/shared/auth/useAuth'

const tierRunSyncChannel = 'git-it:adventure-tier-run-sync'

type TierRunSyncMessage = {
  type: 'adventure-tier-run-updated'
  userId: number
  run: TierRun
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

export function syncTierRunInCache(
  queryClient: QueryClient,
  run: TierRun,
  options: { broadcast?: boolean } = {},
) {
  const owner = cacheOwner(queryClient)
  if (!isCurrentOwner(owner) || owner.userId === null) return
  updateTierRunCache(queryClient, run)
  if (options.broadcast !== false && !run.replay) {
    broadcastTierRunSync(run, owner.userId)
  }

  invalidateTierProgressQueries(queryClient)
}

export function updateTierRunCache(queryClient: QueryClient, run: TierRun) {
  if (!isCurrentOwner(cacheOwner(queryClient))) return
  writeTierRunBootstrap(run)
  queryClient.setQueryData(queryKeys.adventureTierRun(run.id), run)
}

export function subscribeToTierRunSync(queryClient: QueryClient) {
  if (typeof window === 'undefined') return () => {}
  // Bind before confirmation completes; only this generation's confirmed
  // account may use the listener, even if React has not cleaned it up yet.
  const owner = cacheOwner(queryClient)

  const handleMessage = (message: unknown) => {
    if (!isTierRunSyncMessage(message) || message.userId !== owner.userId || !isCurrentOwner(owner)) return
    syncTierRunInCache(queryClient, message.run, { broadcast: false })
  }

  const channel = typeof BroadcastChannel !== 'undefined'
    ? new BroadcastChannel(tierRunSyncChannel)
    : null
  const handleBroadcastMessage = (event: MessageEvent<unknown>) => handleMessage(event.data)
  channel?.addEventListener('message', handleBroadcastMessage)

  const handleStorage = (event: StorageEvent) => {
    if (event.key !== tierRunSyncChannel || !event.newValue) return
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

export function invalidateTierProgressQueries(queryClient: QueryClient) {
  void queryClient.invalidateQueries({ queryKey: queryKeys.chapters })
  void queryClient.invalidateQueries({ queryKey: queryKeys.homeSummary })
  void queryClient.invalidateQueries({ queryKey: queryKeys.statsSummary })
  void queryClient.invalidateQueries({ queryKey: queryKeys.performanceSummary })
  void queryClient.invalidateQueries({ queryKey: queryKeyRoots.chapterOverview })
  void queryClient.invalidateQueries({ queryKey: queryKeys.learnedSkills })
  void queryClient.invalidateQueries({ queryKey: queryKeys.wallet })
}

function broadcastTierRunSync(run: TierRun, userId: number) {
  if (typeof window === 'undefined') return
  const message: TierRunSyncMessage = {
    type: 'adventure-tier-run-updated',
    userId,
    run,
  }
  if (typeof BroadcastChannel !== 'undefined') {
    const channel = new BroadcastChannel(tierRunSyncChannel)
    channel.postMessage(message)
    channel.close()
  }
  try {
    window.localStorage.setItem(
      tierRunSyncChannel,
      JSON.stringify({ ...message, sentAt: Date.now() }),
    )
  } catch {
    // Some browsers disable storage; BroadcastChannel is enough when available.
  }
}

function isTierRunSyncMessage(value: unknown): value is TierRunSyncMessage {
  if (!value || typeof value !== 'object') return false
  const message = value as Partial<TierRunSyncMessage>
  return message.type === 'adventure-tier-run-updated' && Number.isInteger(message.userId) && Boolean(message.run)
}
