import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { executeGitCommand } from '@/shared/git/simulator/engine'
import { normalizeState } from '@/shared/git/simulator/state'
import { RepositoryStateMap } from './RepositoryStateMap'
import { buildGraph, normalizeSnapshot } from './graph'

afterEach(cleanup)

describe('repository state diagram', () => {
  it('distinguishes an ordinary folder from initialized metadata without inventing a commit', () => {
    const folder = normalizeState({ repository_initialized: false, working_tree: { 'README.md': 'ready' } })
    const { rerender } = render(<RepositoryStateMap snapshot={folder} />)
    expect(screen.getByText('Ordinary folder')).toBeInTheDocument()
    expect(screen.getByText('.git metadata absent')).toBeInTheDocument()
    expect(buildGraph(normalizeSnapshot(folder), 'cyan', 'vertical').nodes[0].data.initialized).toBe(false)
    const initialized = executeGitCommand(folder, 'git init').next_state
    rerender(<RepositoryStateMap snapshot={initialized} />)
    expect(screen.getByText('Git repository')).toBeInTheDocument()
    expect(screen.getByText('.git metadata present')).toBeInTheDocument()
    expect(initialized.commits).toHaveLength(0)
    expect(buildGraph(normalizeSnapshot(initialized), 'cyan', 'vertical').nodes[0].data.initialized).toBe(true)
  })

  it('moves a file from working changes to staging while the commit graph stays empty', () => {
    const state = normalizeState({ repository_initialized: true, working_tree: { 'README.md': 'ready' } })
    const { rerender } = render(<RepositoryStateMap snapshot={state} />)
    expect(screen.getByText('README.md').closest('details')).toHaveTextContent('Working changes')
    const staged = executeGitCommand(state, 'git add README.md').next_state
    rerender(<RepositoryStateMap snapshot={staged} />)
    expect(screen.getByText('README.md').closest('details')).toHaveTextContent('Staging area')
    expect(staged.commits).toHaveLength(0)
  })

  it('keeps configuration, remotes, stash and conflicts visible as repository state', () => {
    const state = normalizeState({ repository_initialized: true })
    const configured = executeGitCommand(state, 'git config --global user.name "Learner"').next_state
    const snapshot = normalizeSnapshot({ ...configured,
      remotes: { origin: 'https://example.test/project.git' },
      stash_stack: [{ message: 'Saved draft', working_tree: { 'notes.md': 'draft' } }],
      conflicts: ['app.py'],
    })
    render(<RepositoryStateMap snapshot={snapshot} />)
    expect(screen.getByText('Configuration · 1')).toBeInTheDocument()
    expect(screen.getByText('user.name')).toBeInTheDocument()
    expect(screen.getByText('Remotes · 1')).toBeInTheDocument()
    expect(screen.getByText('Stash · 1')).toBeInTheDocument()
    expect(screen.getByText('Conflicts: app.py')).toBeInTheDocument()
  })
})
