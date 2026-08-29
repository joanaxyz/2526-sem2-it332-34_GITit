import { describe, expect, it } from 'vitest'
import { classifyCommand } from './classifier'

describe('classifyCommand', () => {
  it.each([
    'git status',
    'git status -s',
    'git status --short',
    'git status --porcelain',
  ])('classifies "%s" as diagnostic', (cmd) => {
    expect(classifyCommand(cmd)).toBe('diagnostic')
  })

  it.each([
    'git log',
    'git log --oneline',
    'git log --oneline --graph --all',
    'git log --format="%H %s"',
    'git log HEAD~3..HEAD',
    'git log src/file.js',
  ])('classifies "%s" as diagnostic', (cmd) => {
    expect(classifyCommand(cmd)).toBe('diagnostic')
  })

  it.each([
    'git reflog',
    'git reflog show',
    'git reflog HEAD',
    'git reflog --all',
  ])('classifies "%s" as diagnostic', (cmd) => {
    expect(classifyCommand(cmd)).toBe('diagnostic')
  })

  it.each([
    'git diff',
    'git diff HEAD',
    'git diff HEAD~1 src/file.js',
    'git diff --staged',
    'git diff main..feature',
  ])('classifies "%s" as diagnostic', (cmd) => {
    expect(classifyCommand(cmd)).toBe('diagnostic')
  })

  it('classifies bare "git branch" as diagnostic', () => {
    expect(classifyCommand('git branch')).toBe('diagnostic')
  })

  it.each([
    'git branch -v',
    'git branch --verbose',
    'git branch --list',
    'git branch -v --all',
    'git branch -vv',
    'git branch --all',
  ])('classifies read-only "%s" as diagnostic', (cmd) => {
    expect(classifyCommand(cmd)).toBe('diagnostic')
  })

  it.each([
    ['git branch new-feature', 'positional arg = create'],
    ['git branch -d old-branch', '-d = delete'],
    ['git branch -D old-branch', '-D = force delete'],
    ['git branch -m old new', '-m = rename'],
    ['git branch --delete old-branch', '--delete flag'],
    ['git branch --set-upstream-to=origin/main', '--set-upstream-to flag'],
  ])('classifies "%s" as action (%s)', (cmd) => {
    expect(classifyCommand(cmd)).toBe('action')
  })

  it.each([
    'git commit -m "fix"',
    'git merge feature',
    'git rebase main',
    'git reset --hard HEAD~1',
    'git checkout main',
    'git switch -c new-branch',
    'git cherry-pick abc123',
    'git add .',
    'git push origin main',
    'git pull',
    'git stash',
    'git init',
  ])('classifies "%s" as action', (cmd) => {
    expect(classifyCommand(cmd)).toBe('action')
  })

  it('classifies non-git command as action', () => {
    expect(classifyCommand('ls -la')).toBe('action')
    expect(classifyCommand('echo hello')).toBe('action')
  })

  it('handles leading/trailing whitespace', () => {
    expect(classifyCommand('  git status  ')).toBe('diagnostic')
    expect(classifyCommand('  git commit -m "x"  ')).toBe('action')
  })
})
