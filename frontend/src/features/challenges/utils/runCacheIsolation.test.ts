import { QueryClient } from '@tanstack/react-query'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { ChallengeRun } from '@/features/challenges/types'
import { clearChallengeRunBootstrap, readChallengeRunBootstrap, writeChallengeRunBootstrap } from '@/features/challenges/utils/challengeRunBootstrap'
import { subscribeToChallengeRunSync, syncChallengeRunInCache, updateChallengeRunCache } from '@/features/challenges/utils/challengeRunCache'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { clearTierRunBootstrap, readTierRunBootstrap, writeTierRunBootstrap } from '@/features/story-map/utils/tierRunBootstrap'
import { subscribeToTierRunSync, syncTierRunInCache, updateTierRunCache } from '@/features/story-map/utils/tierRunCache'
import { queryKeys } from '@/shared/api/queryKeys'
import { useAuthStore } from '@/shared/auth/useAuth'

class TestChannel extends EventTarget {
  static open = new Set<TestChannel>()
  static sent: unknown[] = []
  readonly name: string

  constructor(name: string) {
    super()
    this.name = name
    TestChannel.open.add(this)
  }

  postMessage(message: unknown) {
    TestChannel.sent.push(message)
    for (const peer of TestChannel.open) {
      if (peer !== this && peer.name === this.name) {
        peer.dispatchEvent(new MessageEvent('message', { data: message }))
      }
    }
  }

  close() {
    TestChannel.open.delete(this)
  }
}

function signIn(userId: number, generation: number) {
  useAuthStore.setState({
    accessToken: `token-${userId}`,
    user: { id: userId, username: `learner-${userId}`, email: `${userId}@example.com`, is_staff: false },
    sessionUserId: userId,
    sessionGeneration: generation,
  })
}

const runA = { id: 42, replay: false } as ChallengeRun & TierRun
const runB = { id: 43, replay: false } as ChallengeRun & TierRun
const modes = [
  {
    name: 'challenge',
    channel: 'git-it:challenge-run-sync',
    messageType: 'challenge-run-updated',
    prefix: 'git-it:challenge-run-bootstrap:',
    write: writeChallengeRunBootstrap,
    read: readChallengeRunBootstrap,
    clear: clearChallengeRunBootstrap,
    subscribe: subscribeToChallengeRunSync,
    sync: syncChallengeRunInCache,
    update: updateChallengeRunCache,
    key: queryKeys.challengeRun,
  },
  {
    name: 'tier',
    channel: 'git-it:adventure-tier-run-sync',
    messageType: 'adventure-tier-run-updated',
    prefix: 'git-it:tier-run-bootstrap:',
    write: writeTierRunBootstrap,
    read: readTierRunBootstrap,
    clear: clearTierRunBootstrap,
    subscribe: subscribeToTierRunSync,
    sync: syncTierRunInCache,
    update: updateTierRunCache,
    key: queryKeys.adventureTierRun,
  },
]

describe.each(modes)('$name run cache account isolation', (mode) => {
  const cleanups: (() => void)[] = []

  function client(subscribe = false) {
    const result = new QueryClient()
    cleanups.push(() => result.clear())
    if (subscribe) cleanups.push(mode.subscribe(result))
    return result
  }

  function deliver(message: unknown, transport: 'broadcast' | 'storage' = 'broadcast') {
    if (transport === 'storage') {
      window.dispatchEvent(new StorageEvent('storage', {
        key: mode.channel,
        newValue: JSON.stringify(message),
      }))
      return
    }
    const sender = new TestChannel(mode.channel)
    sender.postMessage(message)
    sender.close()
  }

  beforeEach(() => {
    vi.stubGlobal('BroadcastChannel', TestChannel)
    window.sessionStorage.clear()
    window.localStorage.clear()
    TestChannel.sent = []
    signIn(1, 1)
  })

  afterEach(() => {
    for (const cleanup of cleanups.splice(0).reverse()) cleanup()
    TestChannel.open.clear()
    useAuthStore.setState({ accessToken: null, user: null, sessionUserId: null, sessionGeneration: 0 })
    vi.unstubAllGlobals()
  })

  it('keeps account bootstraps separate and preserves unrelated or legacy storage', () => {
    const legacyKey = `${mode.prefix}${runA.id}`
    window.sessionStorage.setItem(legacyKey, JSON.stringify({ run: runA, storedAt: Date.now() }))
    window.sessionStorage.setItem('unrelated-user-data', 'keep')
    // The old unowned entry is never trusted or deleted.
    expect(mode.read(runA.id)).toBeUndefined()
    mode.write(runA)
    expect(mode.read(runA.id)).toEqual(runA)

    signIn(2, 2)
    expect(mode.read(runA.id)).toBeUndefined()
    mode.clear(runA.id)
    mode.write(runB)
    expect(mode.read(runB.id)).toEqual(runB)

    signIn(1, 3)
    expect(mode.read(runA.id)).toEqual(runA)
    expect(mode.read(runB.id)).toBeUndefined()
    mode.clear(runA.id)
    expect(mode.read(runA.id)).toBeUndefined()
    expect(window.sessionStorage.getItem(legacyKey)).not.toBeNull()
    expect(window.sessionStorage.getItem('unrelated-user-data')).toBe('keep')
    signIn(2, 4)
    expect(mode.read(runB.id)).toEqual(runB)
  })

  it('requires a confirmed account for bootstrap reads and writes', () => {
    mode.write(runA)
    useAuthStore.setState({ user: null })
    expect(mode.read(runA.id)).toBeUndefined()
    mode.write(runB)
    signIn(1, 1)
    expect(mode.read(runB.id)).toBeUndefined()
    expect(mode.read(runA.id)).toEqual(runA)
    useAuthStore.setState({ accessToken: null })
    expect(mode.read(runA.id)).toBeUndefined()
  })

  it('rejects unowned data even if it appears under the scoped key', () => {
    window.sessionStorage.setItem(`${mode.prefix}1:${runA.id}`, JSON.stringify({
      run: runA, storedAt: Date.now(),
    }))
    expect(mode.read(runA.id)).toBeUndefined()
  })

  it('tags outgoing sync and updates a same-account tab', () => {
    const receiver = client(true)
    mode.sync(client(), runA)
    expect(receiver.getQueryData(mode.key(runA.id))).toEqual(runA)
    expect(mode.read(runA.id)).toEqual(runA)
    expect(TestChannel.sent).toContainEqual({ type: mode.messageType, userId: 1, run: runA })
    expect(JSON.parse(window.localStorage.getItem(mode.channel)!)).toMatchObject({
      type: mode.messageType, userId: 1, run: runA,
    })
  })

  it.each(['broadcast', 'storage'] as const)('rejects another account and legacy %s messages', (transport) => {
    mode.sync(client(), runA)
    signIn(2, 2)
    const receiver = client(true)
    deliver({ type: mode.messageType, userId: 1, run: runA }, transport)
    deliver({ type: mode.messageType, run: runA }, transport)
    expect(receiver.getQueryData(mode.key(runA.id))).toBeUndefined()
    expect(mode.read(runA.id)).toBeUndefined()

    deliver({ type: mode.messageType, userId: 2, run: runB }, transport)
    expect(receiver.getQueryData(mode.key(runB.id))).toEqual(runB)
  })

  it('ignores old-generation listeners and late writers after an account switch', () => {
    const oldClient = client(true)
    signIn(2, 2)
    const currentClient = client(true)
    deliver({ type: mode.messageType, userId: 1, run: runA })
    deliver({ type: mode.messageType, userId: 2, run: runB })
    expect(oldClient.getQueryData(mode.key(runA.id))).toBeUndefined()
    expect(oldClient.getQueryData(mode.key(runB.id))).toBeUndefined()
    expect(currentClient.getQueryData(mode.key(runB.id))).toEqual(runB)

    TestChannel.sent = []
    mode.sync(oldClient, runA)
    mode.update(oldClient, runA)
    expect(TestChannel.sent).toEqual([])
    expect(oldClient.getQueryData(mode.key(runA.id))).toBeUndefined()
    expect(mode.read(runA.id)).toBeUndefined()
  })

  it('waits for confirmation and survives same-account token rotation only', () => {
    useAuthStore.setState({ user: null })
    const receiver = client(true)
    deliver({ type: mode.messageType, userId: 1, run: runA })
    expect(receiver.getQueryData(mode.key(runA.id))).toBeUndefined()
    signIn(1, 1)
    useAuthStore.setState({ accessToken: 'rotated-token' })
    deliver({ type: mode.messageType, userId: 1, run: runA })
    expect(receiver.getQueryData(mode.key(runA.id))).toEqual(runA)

    signIn(1, 2)
    deliver({ type: mode.messageType, userId: 1, run: runB })
    expect(receiver.getQueryData(mode.key(runB.id))).toBeUndefined()
  })
})
