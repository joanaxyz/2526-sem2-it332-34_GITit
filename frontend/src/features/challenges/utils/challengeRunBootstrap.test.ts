import { describe, expect, it } from 'vitest'

import {
  clearChallengeRunBootstrap,
  readChallengeRunBootstrap,
  writeChallengeRunBootstrap,
} from '@/features/challenges/utils/challengeRunBootstrap'
import type { ChallengeRun } from '@/shared/practice/types'

const run = { id: 42 } as ChallengeRun

describe('challengeRunBootstrap', () => {
  it('stores and reads a challenge run briefly', () => {
    writeChallengeRunBootstrap(run)

    expect(readChallengeRunBootstrap(42)).toEqual(run)

    clearChallengeRunBootstrap(42)
    expect(readChallengeRunBootstrap(42)).toBeUndefined()
  })
})
