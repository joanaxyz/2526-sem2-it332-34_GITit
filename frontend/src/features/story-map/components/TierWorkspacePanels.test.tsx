import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { TierDagAnimationController } from '@/features/story-map/hooks/useTierDagAnimation'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'

vi.mock('@/features/story-map/components/TierDagStage', () => ({
  TierDagStage: () => <div data-testid="tier-dag-stage">Live DAG</div>,
}))

vi.mock('@/shared/level/components/LiveDagPanel', () => ({
  LiveDagPanel: ({ title }: { title: string }) => <div data-testid="expected-dag-stage">{title}</div>,
}))

import { TierDiagramStage } from './TierWorkspacePanels'

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
    repository_state: snapshot,
    expected_state: expectedState ? snapshot : null,
  } as unknown as TierRun
}

afterEach(cleanup)

describe('TierDiagramStage', () => {
  it('always renders the Live DAG without a collapse control', () => {
    render(<TierDiagramStage run={makeRun(false)} animation={animation} />)

    expect(screen.getByTestId('tier-dag-stage')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /live dag panel/i })).not.toBeInTheDocument()
    expect(screen.queryByTestId('expected-dag-stage')).not.toBeInTheDocument()
    expect(document.querySelector('.tier-repository-view')).not.toHaveClass('has-target')
  })

  it('stacks Expected State with Live DAG when target scaffolding is available', () => {
    render(<TierDiagramStage run={makeRun(true)} animation={animation} />)

    expect(screen.getByTestId('tier-dag-stage')).toBeInTheDocument()
    expect(screen.getByTestId('expected-dag-stage')).toHaveTextContent('Expected State · Target')
    expect(document.querySelector('.tier-repository-view')).toHaveClass('has-target')
    expect(screen.queryByRole('tablist')).not.toBeInTheDocument()
  })
})
