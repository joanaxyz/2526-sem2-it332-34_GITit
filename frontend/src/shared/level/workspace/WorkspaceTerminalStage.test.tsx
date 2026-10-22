import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { WorkspaceRun } from '@/shared/level/workspace/types'

import { WorkspaceTerminalStage } from './WorkspaceTerminalStage'

const scene = { runQueryKey: ['tier-run', 1] }

function makeRun(): WorkspaceRun {
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
  } as unknown as WorkspaceRun
}

afterEach(cleanup)

describe('WorkspaceTerminalStage', () => {
  it('keeps command-guide navigation out of the terminal title bar', () => {
    render(
      <WorkspaceTerminalStage
        run={makeRun()}
        scene={scene}
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
      <WorkspaceTerminalStage
        run={{ ...makeRun(), scaffolding: { live_dag: true, expected_state: true, contextual_feedback: true } } as WorkspaceRun}
        scene={scene}
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

  it('renders the prompt inside the terminal scrollback', () => {
    render(
      <WorkspaceTerminalStage
        run={makeRun()}
        scene={scene}
        lines={[]}
        prompt="learner"
        mutationPending={false}
        dagAnimating={false}
        battleAnimating={false}
        onCommand={vi.fn()}
      />,
    )
    expect(screen.getByRole('log')).toContainElement(screen.getByLabelText('Git command'))
    expect(document.querySelector('.terminal-input-dock')).toBeNull()
  })
})
