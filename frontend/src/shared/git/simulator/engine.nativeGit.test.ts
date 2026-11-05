// @vitest-environment node
import { spawnSync } from 'node:child_process'
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { devNull } from 'node:os'
import { join } from 'node:path'
import { afterAll, beforeAll, describe, expect, it } from 'vitest'

import { executeGitCommand } from '@/shared/git/simulator/engine'
import { normalizeState } from '@/shared/git/simulator/state'

const gitAvailable = spawnSync('git', ['--version']).status === 0

// Check real Git, with machine/user configuration excluded, rather than copying
// simulator output into expected strings. Git is optional for browser-only CI.
describe.skipIf(!gitAvailable)('native Git terminal parity', () => {
  let directory: string
  const env = { ...process.env, LC_ALL: 'C', GIT_CONFIG_NOSYSTEM: '1', GIT_CONFIG_GLOBAL: process.platform === 'win32' ? 'NUL' : devNull }
  const git = (...args: string[]) => spawnSync('git', ['-c', 'core.autocrlf=false', '-c', 'user.name=Learner', '-c', 'user.email=learner@example.test', ...args], { cwd: directory, env, encoding: 'utf8' })
  const repo = () => normalizeState({
    commits: [{ id: 'c0', message: 'base', parents: [], tree: { 'tracked.txt': 'base\n' } }],
    branches: { main: 'c0' }, head: { type: 'branch', name: 'main' },
  })

  beforeAll(() => {
    // Keep the disposable repository under the writable workspace on Windows.
    const temporaryRoot = join(process.cwd(), '.tmp')
    mkdirSync(temporaryRoot, { recursive: true })
    directory = mkdtempSync(join(temporaryRoot, 'git-it-terminal-'))
    const initialized = git('init', '-q', '-b', 'main')
    expect(initialized.status, initialized.stderr).toBe(0)
    writeFileSync(join(directory, 'tracked.txt'), 'base\n')
    expect(git('add', '.').status).toBe(0)
    expect(git('commit', '-qm', 'base').status).toBe(0)
  })
  afterAll(() => {
    if (directory) rmSync(directory, { recursive: true, force: true })
  })

  it.each([
    ['switch'], ['switch', '-c'], ['checkout', '-b'], ['restore'],
    ['check-ignore'], ['config'], ['branch', '-m'], ['--global', 'config'], ['frobnicate'],
  ])('matches Git error and exit status for %j', (...args) => {
    const native = git(...args)
    const simulated = executeGitCommand(repo(), ['git', ...args].join(' '))
    expect(simulated.stderr).toBe(native.stderr.trimEnd().split('\n')[0].replace(/\r$/, ''))
    expect(simulated.exit_code).toBe(native.status)
    expect(simulated.stdout).toBe('')
  })

  it('matches clean status, silent remote changes and rm output', () => {
    expect(executeGitCommand(repo(), 'git status').stdout).toBe(git('status').stdout.trimEnd())
    expect(executeGitCommand(repo(), 'git remote add origin https://example.test/repo.git').stdout)
      .toBe(git('remote', 'add', 'origin', 'https://example.test/repo.git').stdout)
    expect(executeGitCommand(repo(), 'git rm --cached tracked.txt').stdout)
      .toBe(git('rm', '--cached', 'tracked.txt').stdout.trimEnd())
    expect(git('reset', '-q', 'HEAD').status).toBe(0)
  })

  it('matches porcelain status through staging and editing a file again', () => {
    let state = repo()
    for (const [name, content] of [['new.txt', 'new\n'], ['tracked.txt', 'edited\n']]) {
      writeFileSync(join(directory, name), content)
      state.working_tree[name] = { status: name === 'new.txt' ? 'untracked' : 'modified', content }
    }
    expect(executeGitCommand(state, 'git status --porcelain').stdout).toBe(git('status', '--porcelain').stdout.trimEnd())
    expect(git('add', '.').status).toBe(0)
    state = normalizeState(executeGitCommand(state, 'git add .').next_state)
    writeFileSync(join(directory, 'tracked.txt'), 'edited again\n')
    state.working_tree['tracked.txt'] = { status: 'modified', content: 'edited again\n' }
    expect(executeGitCommand(state, 'git status --porcelain').stdout).toBe(git('status', '--porcelain').stdout.trimEnd())
  })
})
