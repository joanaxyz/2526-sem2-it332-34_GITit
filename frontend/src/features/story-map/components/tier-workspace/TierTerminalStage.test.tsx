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
        terminalGridRef={{ current: null }}
        terminalGridStyle={{}}
        mutationPending={false}
        dagAnimating={false}
        battleAnimating={false}
        onBeginTerminalPaneResize={vi.fn()}
        onKeyboardTerminalPaneResize={vi.fn()}
        onResetTerminalPaneResize={vi.fn()}
        onCommand={vi.fn()}
      />,
    )
    expect(screen.queryByRole('button', { name: 'Command guide' })).not.toBeInTheDocument()
  })
})
