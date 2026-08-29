import { describe, expect, it } from 'vitest'

import { GIT_COMMAND_NAMES, SUPPORTED_OPTIONS } from '@/shared/git/simulator/commandMetadata'
import { executeGitCommand } from '@/shared/git/simulator/engine'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'

function repo(): MutableRepositoryState {
  return {
    repository_initialized: true,
    commits: [{ id: 'c0', message: 'base', parents: [], tree: { 'README.md': 'hello' } }],
    branches: { main: 'c0' },
    head: { type: 'branch', name: 'main', target: 'c0' },
    staging: {},
    working_tree: {},
    conflicts: [],
  }
}

describe('simulator command inventory', () => {
  it('advertises only commands with simulator support', () => {
    expect(GIT_COMMAND_NAMES).toEqual(Object.keys(SUPPORTED_OPTIONS).sort())
    expect(GIT_COMMAND_NAMES).toContain('status')
    expect(GIT_COMMAND_NAMES).toContain('commit')
    expect(GIT_COMMAND_NAMES).not.toEqual(expect.arrayContaining(['clean', 'mv', 'update-ref', 'credential', 'cli']))
  })

  it('does not simulate unsupported Git commands from the baseline inventory', () => {
    for (const command of ['git clean -f', 'git mv README.md docs/README.md', 'git update-ref refs/heads/release HEAD', 'git credential fill']) {
      const result = executeGitCommand(repo(), command)

      expect(result.processed, command).toBe(false)
      expect(result.exit_code, command).toBe(129)
      expect(result.output, command).toContain('is not supported in this simulator')
      expect(result.next_state.commits.map((commit) => commit.id)).toEqual(['c0'])
      expect(result.next_state.branches).toEqual(repo().branches)
      expect(result.next_state.working_tree).toEqual({})
    }
  })

  it('lists only supported commands from help', () => {
    const shortHelp = executeGitCommand(repo(), 'git --help')
    expect(shortHelp.processed).toBe(true)
    expect(shortHelp.diagnostic).toBe(true)
    expect(shortHelp.output).toContain(`supports ${GIT_COMMAND_NAMES.length} commands`)
    expect(shortHelp.output).toContain("git help -a")

    const fullHelp = executeGitCommand(repo(), 'git help -a')
    expect(fullHelp.processed).toBe(true)
    expect(fullHelp.diagnostic).toBe(true)
    expect(fullHelp.output).toContain(`Supported simulator commands (${GIT_COMMAND_NAMES.length})`)
    expect(fullHelp.output).toContain('  git status')
    expect(fullHelp.output).not.toContain('Stateful reference commands')
    expect(fullHelp.output).not.toContain('  git update-ref')
    expect(fullHelp.output).not.toContain('  git credential')
  })

  it('still rejects arbitrary unknown subcommands', () => {
    const result = executeGitCommand(repo(), 'git frobnicate')

    expect(result.processed).toBe(false)
    expect(result.exit_code).toBe(129)
    expect(result.output).toContain("git: 'frobnicate' is not supported in this simulator")
  })
})
