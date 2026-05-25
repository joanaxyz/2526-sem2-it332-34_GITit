import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import type { RepositorySnapshot, ScenarioSession } from '@/features/practice/types'
import { ExpectedStatePanel } from './ExpectedStatePanel'
import { LiveDagPanel } from './LiveDagPanel'

const snapshot: RepositorySnapshot = {
  repository_initialized: true,
  commits: [
    {
      id: 'c1',
      message: 'Base',
      parents: [],
      tree: {
        'README.md': 'readme-v1',
        'src/form.js': 'form-validation-v1',
      },
      changes: {
        'README.md': { change_type: 'added', before: null, after: 'readme-v1' },
      },
    },
    {
      id: 'c2',
      message: 'Update form validation',
      parents: ['c1'],
      tree: {
        'README.md': 'readme-v1',
        'src/form.js': 'form-validation-v2',
      },
      changes: {
        'src/form.js': {
          change_type: 'modified',
          before: 'form-validation-v1',
          after: 'form-validation-v2',
        },
      },
    },
  ],
  branches: { main: 'c2' },
  head: { type: 'branch' as const, name: 'main', target: 'c2' },
  staging: { 'src/form.js': 'form-validation-v2' },
  working_tree: { 'debug.log': 'debug-v1' },
  conflicts: [],
  remotes: { origin: 'https://example.test/repo.git' },
  remote_branches: { 'origin/main': 'c1' },
  upstream_tracking: { main: 'origin/main' },
  stash_stack: [{ working_tree: { 'notes.md': 'draft' }, staging: {}, conflicts: [] }],
  reflog: [],
  partial_hunks: {},
  operation_metadata: {},
}

describe('LiveDagPanel', () => {
  afterEach(() => cleanup())

  it('renders commit details in the diagram overlay when a node is active', () => {
    render(<LiveDagPanel snapshot={snapshot} />)

    const commitButton = screen.getByTitle(/commit c2/i)
    fireEvent.focus(commitButton)

    expect(screen.getByTestId('commit-details-overlay')).toBeInTheDocument()
    expect(screen.getByText('Message: Update form validation')).toBeInTheDocument()
    expect(screen.getByText(/modified src\/form\.js/i)).toBeInTheDocument()
    expect(screen.getByText(/src\/form\.js @ form-validation-v2/i)).toBeInTheDocument()
  })
})

describe('ExpectedStatePanel', () => {
  afterEach(() => cleanup())

  it('renders the expected state with the shared repository diagram', () => {
    const session = {
      scaffolding: { expected_state: true, live_dag: true, contextual_feedback: true },
      expected_state: snapshot,
    } as unknown as ScenarioSession

    render(<ExpectedStatePanel session={session} />)

    expect(screen.getByText('Expected-State Diagram')).toBeInTheDocument()
    fireEvent.focus(screen.getByTitle(/commit c2/i))
    expect(screen.getByText('Message: Update form validation')).toBeInTheDocument()
  })
})
