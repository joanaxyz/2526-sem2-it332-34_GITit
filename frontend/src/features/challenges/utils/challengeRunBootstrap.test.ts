import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import {
  clearChallengeRunBootstrap,
  readChallengeRunBootstrap,
  writeChallengeRunBootstrap,
} from '@/features/challenges/utils/challengeRunBootstrap'
import type { ChallengeRun } from '@/features/challenges/types'
import { useAuthStore } from '@/shared/auth/useAuth'

const run = { id: 42 } as ChallengeRun

describe('challengeRunBootstrap', () => {
  beforeEach(() => {
    useAuthStore.setState({
      accessToken: 'test-token',
      user: { id: 1, username: 'learner', email: 'learner@example.com', is_staff: false },
      sessionUserId: 1,
      sessionGeneration: 1,
    })
  })

  afterEach(() => {
    useAuthStore.setState({ accessToken: null, user: null, sessionUserId: null, sessionGeneration: 0 })
  })

  it('stores and reads a challenge run briefly', () => {
    writeChallengeRunBootstrap(run)

    expect(readChallengeRunBootstrap(42)).toEqual(run)

    clearChallengeRunBootstrap(42)
    expect(readChallengeRunBootstrap(42)).toBeUndefined()
  })
})
