import { cleanup, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { TierDagAnimationController } from '@/features/story-map/hooks/useTierDagAnimation'
import type { RepositorySnapshot } from '@/shared/level/types'

import { TierDagTabs } from './TierDagTabs'

// Real diagrams (no mocks): the browser bug was the inactive graph painting
// through, so this checks where each graph's nodes actually render.
const animation = {
  activity: 'idle',
  animating: false,
  onCommandStart: vi.fn(),
  onCommandResolved: vi.fn(),
  onCommandError: vi.fn(),
} satisfies TierDagAnimationController

const uninitialized: RepositorySnapshot = {
  repository_initialized: false,
  commits: [],
  branches: {},
  head: { type: 'branch', name: 'main' },
  staging: {},
  working_tree: {},
  conflicts: [],
} as unknown as RepositorySnapshot

const target: RepositorySnapshot = {
  repository_initialized: true,
  commits: [{ id: 'r39', message: 'Create docs portal', parents: [], tree: { 'README.md': 'v1' } }],
  branches: { main: 'r39' },
  head: { type: 'branch', name: 'main', target: 'r39' },
  staging: {},
  working_tree: {},
  conflicts: [],
} as unknown as RepositorySnapshot

afterEach(cleanup)

describe('TierDagTabs panes', () => {
  it('renders the "Git is not initialized" placeholder only inside the Live pane', () => {
    render(<TierDagTabs snapshot={uninitialized} expectedState={target} countedCommands={0} animation={animation} />)

    const livePane = document.getElementById(
      screen.getByRole('tab', { name: 'Live DAG' }).getAttribute('aria-controls')!,
    )!
    const expectedPane = document.getElementById(
      screen.getByRole('tab', { name: 'Expected state' }).getAttribute('aria-controls')!,
    )!

    expect(within(livePane).getByText('Git is not initialized')).toBeInTheDocument()
    expect(within(expectedPane).queryByText('Git is not initialized')).not.toBeInTheDocument()
    expect(within(expectedPane).getByTitle(/commit r39/i)).toBeInTheDocument()
    expect(within(livePane).queryByTitle(/commit r39/i)).not.toBeInTheDocument()

    expect(expectedPane).toHaveClass('is-inactive')
    expect(expectedPane).toHaveAttribute('inert')
  })
})
