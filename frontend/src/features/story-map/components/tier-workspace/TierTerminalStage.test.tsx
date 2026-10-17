import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'

import { TierTerminalStage } from './TierTerminalStage'

function makeRun(): TierRun {
  return {
    id: 1,
    status: 'started',
    scaffolding: {
      live_dag: true,
      expected_state: false,
      contextual_feedback: false,
    },
    repository_state: {
      repository_initialized: true,
      commits: [],
      branches: {},
      head: null,
      staging: {},
      working_tree: {},
      conflicts: [],
    },
    expected_state: null,
  } as unknown as TierRun
}

afterEach(cleanup)

describe('TierTerminalStage', () => {
  it('keeps command-guide navigation out of the terminal title bar', () => {
    render(
      <TierTerminalStage
        run={makeRun()}
        lines={[]}
        prompt="learner"
        mutationPending={false}
        dagAnimating={false}
        battleAnimating={false}
        onCommand={vi.fn()}
      />,
    )
    expect(screen.queryByRole('button', { name: 'Command guide' })).not.toBeInTheDocument()
  })

  it('renders the terminal alone, with no feedback split or resize handle', () => {
    render(
      <TierTerminalStage
        run={{ ...makeRun(), scaffolding: { live_dag: true, expected_state: true, contextual_feedback: true } } as TierRun}
        lines={[]}
        prompt="learner"
        mutationPending={false}
        dagAnimating={false}
        battleAnimating={false}
        onCommand={vi.fn()}
      />,
    )
    const stage = screen.getByTestId('tier-terminal-stage')
    expect(stage).not.toHaveClass('has-feedback')
    expect(stage.querySelector('[data-tour-target="feedback"]')).toBeNull()
    expect(screen.queryByRole('separator')).not.toBeInTheDocument()
  })
})
