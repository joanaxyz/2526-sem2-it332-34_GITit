import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { TierDagAnimationController } from '@/features/story-map/hooks/useTierDagAnimation'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'

vi.mock('@/features/story-map/components/TierDagStage', () => ({
  TierDagStage: ({ showHeader = true }: { showHeader?: boolean }) => (
    <div data-testid="tier-dag-stage">{showHeader ? 'Live DAG' : null}</div>
  ),
}))

vi.mock('@/shared/level/components/LiveDagPanel', () => ({
  LiveDagPanel: ({ title }: { title: string }) => <div data-testid="expected-dag-stage">{title}</div>,
}))

import { TierDiagramStage } from './TierDiagramStage'

const animation = {
  activity: 'idle',
  animating: false,
  onCommandStart: vi.fn(),
  onCommandResolved: vi.fn(),
  onCommandError: vi.fn(),
} satisfies TierDagAnimationController

function makeRun(expectedState: boolean): TierRun {
  const snapshot = {
    repository_initialized: true,
    commits: [],
    branches: {},
    head: null,
    staging: {},
    working_tree: {},
    conflicts: [],
  }

  return {
    id: 1,
    scaffolding: {
      live_dag: true,
      expected_state: expectedState,
      contextual_feedback: false,
    },
    counts: { counted_action_total: 0 },
    repository_state: snapshot,
    expected_state: expectedState ? snapshot : null,
  } as unknown as TierRun
}

afterEach(cleanup)

describe('TierDiagramStage', () => {
  it('shows the Live DAG under its own title, with no tab bar, when there is no Expected State', () => {
    render(<TierDiagramStage run={makeRun(false)} animation={animation} />)

    expect(screen.getByTestId('tier-dag-stage')).toHaveTextContent('Live DAG')
    expect(screen.queryByRole('tablist')).not.toBeInTheDocument()
    expect(screen.queryByTestId('expected-dag-stage')).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /live dag panel/i })).not.toBeInTheDocument()
  })

  it('puts Live DAG and Expected State behind tabs when target scaffolding is available', () => {
    render(<TierDiagramStage run={makeRun(true)} animation={animation} />)

    expect(screen.getByRole('tablist')).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Live DAG' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.getByRole('tab', { name: 'Expected state' })).toHaveAttribute('aria-selected', 'false')
    expect(screen.getByTestId('tier-dag-stage')).toBeInTheDocument()
    expect(screen.getByTestId('expected-dag-stage')).toBeInTheDocument()
  })

  it('treats a missing expected snapshot as no Expected State', () => {
    const run = { ...makeRun(true), expected_state: null } as TierRun
    render(<TierDiagramStage run={run} animation={animation} />)

    expect(screen.queryByRole('tablist')).not.toBeInTheDocument()
  })
})
