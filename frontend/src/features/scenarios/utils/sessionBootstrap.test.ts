import { afterEach, describe, expect, it } from 'vitest'

import type { PracticeSession } from '@/features/practice/types'
import {
  clearSessionBootstrap,
  readSessionBootstrap,
  writeSessionBootstrap,
} from '@/features/scenarios/utils/sessionBootstrap'

const session = { id: 42 } as PracticeSession

afterEach(() => {
  clearSessionBootstrap(42)
})

describe('sessionBootstrap', () => {
  it('writes and reads a bootstrap entry for the same session id', () => {
    writeSessionBootstrap(session)
    expect(readSessionBootstrap(42)).toEqual(session)
    clearSessionBootstrap(42)
    expect(readSessionBootstrap(42)).toBeUndefined()
  })

  it('returns undefined when the stored session id does not match', () => {
    writeSessionBootstrap(session)
    expect(readSessionBootstrap(99)).toBeUndefined()
  })
})
