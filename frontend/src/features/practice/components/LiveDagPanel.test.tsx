import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import type { RepositorySnapshot, PracticeSession } from '@/features/practice/types'
import { ExpectedStatePanel } from './ExpectedStatePanel'
import { graphLayoutSignature, LiveDagPanel } from './LiveDagPanel'

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

  it('keeps the same layout signature when only branch pointers move', () => {
    const movedPointerSnapshot: RepositorySnapshot = {
      ...snapshot,
      branches: { main: 'c1', feature: 'c2' },
      head: { type: 'branch', name: 'feature', target: 'c2' },
    }

    expect(graphLayoutSignature(snapshot)).toBe(graphLayoutSignature(movedPointerSnapshot))
  })

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
    } as unknown as PracticeSession

    render(<ExpectedStatePanel session={session} />)

    expect(screen.getByText('Expected-State Diagram')).toBeInTheDocument()
    fireEvent.focus(screen.getByTitle(/commit c2/i))
    expect(screen.getByText('Message: Update form validation')).toBeInTheDocument()
  })

  it('renders command drill target state as a lens instead of hidden expected state copy', () => {
    const session = {
      practice_kind: 'command_drill',
      scaffolding: { expected_state: true, target_state: true, live_dag: false, state_lens: true, contextual_feedback: true },
      expected_state: snapshot,
      visualization: {
        target_state_lens: {
          working_directory: [],
          staging_area: [{ path: 'src/form.js', status: 'modified', tokens: [] }],
          local_repository: { commit_count: 2, head: { type: 'branch', name: 'main' } },
          branch_pointers: { main: 'c2' },
          remote_tracking_branches: {},
          remotes: {},
          conflicts: [],
        },
        state_lens: {},
        command_effect_delta: {},
        commit_dag: {},
      },
    } as unknown as PracticeSession

    render(<ExpectedStatePanel session={session} />)

    expect(screen.getByText('Target State Lens')).toBeInTheDocument()
    expect(screen.getByText(/src\/form\.js - modified/i)).toBeInTheDocument()
    expect(screen.queryByText('Expected state hidden')).not.toBeInTheDocument()
  })

  it('keeps hard workflow expected state hidden', () => {
    const session = {
      practice_kind: 'workflow_scenario',
      scaffolding: { expected_state: false, live_dag: true, state_lens: true, contextual_feedback: false },
      expected_state: null,
    } as unknown as PracticeSession

    render(<ExpectedStatePanel session={session} />)

    expect(screen.getByText('Expected state hidden')).toBeInTheDocument()
  })
})
