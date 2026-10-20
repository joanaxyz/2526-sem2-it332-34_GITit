import { afterEach, describe, expect, it, vi } from 'vitest'

import type { User } from '@/shared/auth/types'
import { useAuthStore } from '@/shared/auth/useAuth'

import {
  readStoryMapSnapshot,
  storyMapSnapshotKeys,
  writeStoryMapSnapshot,
} from './storyMapSnapshot'

function signIn(id: number) {
  useAuthStore.setState({
    accessToken: `token-${id}`,
    user: { id, username: `player-${id}` } as User,
    sessionUserId: id,
  })
}

const key = storyMapSnapshotKeys.chapterOverview(7)

afterEach(() => {
  vi.useRealTimers()
  window.localStorage.clear()
  useAuthStore.setState({ accessToken: null, user: null, sessionUserId: null })
})

describe('storyMapSnapshot', () => {
  it('returns the last payload written for the same player', () => {
    signIn(1)
    writeStoryMapSnapshot(key, { chapter_id: 7, adventures: [] })

    expect(readStoryMapSnapshot(key)).toEqual({ chapter_id: 7, adventures: [] })
  })

  it('never hands one player another player\'s map', () => {
    signIn(1)
    writeStoryMapSnapshot(key, { chapter_id: 7 })
    signIn(2)

    expect(readStoryMapSnapshot(key)).toBeUndefined()
  })

  it('neither reads nor writes without a confirmed session', () => {
    writeStoryMapSnapshot(key, { chapter_id: 7 })
    expect(window.localStorage.length).toBe(0)

    signIn(1)
    writeStoryMapSnapshot(key, { chapter_id: 7 })
    useAuthStore.setState({ accessToken: null })

    expect(readStoryMapSnapshot(key)).toBeUndefined()
  })

  it('drops a snapshot older than a week', () => {
    vi.useFakeTimers()
    signIn(1)
    writeStoryMapSnapshot(key, { chapter_id: 7 })
    vi.advanceTimersByTime(8 * 24 * 60 * 60 * 1000)

    expect(readStoryMapSnapshot(key)).toBeUndefined()
    expect(window.localStorage.length).toBe(0)
  })
})
