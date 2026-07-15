import { describe, expect, it } from 'vitest'

import { isExitCommand } from '@/shared/level-runtime/commands'

describe('isExitCommand', () => {
  it('matches exit commands case-insensitively after trimming', () => {
    expect(isExitCommand('exit')).toBe(true)
    expect(isExitCommand(' EXIT ')).toBe(true)
    expect(isExitCommand('git exit')).toBe(false)
  })
})
