import { describe, expect, it } from 'vitest'

import { isExitCommand, isGitCommand } from '@/shared/level-runtime/commands'

describe('isExitCommand', () => {
  it('matches exit commands case-insensitively after trimming', () => {
    expect(isExitCommand('exit')).toBe(true)
    expect(isExitCommand(' EXIT ')).toBe(true)
    expect(isExitCommand('git exit')).toBe(false)
  })
})

describe('isGitCommand', () => {
  it.each(['git', 'git status', '  git\tcommit -m test  ', 'git comit'])('recognizes Git input: %s', (command) => {
    expect(isGitCommand(command)).toBe(true)
  })

  it.each(['', 'cd src', 'ls', 'pwd', 'echo git status', 'gitignore', 'gti status', 'GIT status'])('rejects non-Git input: %s', (command) => {
    expect(isGitCommand(command)).toBe(false)
  })
})
