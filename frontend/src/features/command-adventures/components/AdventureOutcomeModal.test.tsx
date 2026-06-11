import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { AdventureOutcomeModal } from './AdventureOutcomeModal'
import type { AdventureRun } from '@/features/command-adventures/types'

const run: AdventureRun = {
  id: 1,
  status: 'completed',
  mode: 'primary',
  is_passed: true,
  command_adventure: { id: 1, slug: 'repo-basecamp', title: 'Repository Basecamp', description: '' },
  storey_id: 1,
  current_problem_index: 2,
  total_problems: 2,
  session_score: 50,
  passed: true,
  mastery_progress_gained: 0.85,
  mastery: {
    commands: [
      { slug: 'git-init', title: 'git init', strength: 2, mastered_bar: 2, introduced: true, mastered: true },
      { slug: 'git-status', title: 'git status', strength: 1, mastered_bar: 2, introduced: true, mastered: false },
    ],
    commands_mastered: 1,
    total_commands: 2,
    session_score: 50,
    pass_bar: 36,
    total_achievable: 80,
    passed: true,
  },
  completed_at: '2026-06-07T00:00:00Z',
  current_attempt: null,
  results: [],
  progress: { completed: 2, total: 2 },
}

describe('AdventureOutcomeModal', () => {
  afterEach(() => cleanup())

  it('surfaces the pass state, session-score stats, and per-command mastery', () => {
    render(<AdventureOutcomeModal open run={run} onRestart={vi.fn()} onClose={vi.fn()} />)
    expect(screen.getByText('Challenge unlocked')).toBeInTheDocument()
    expect(screen.getByText('Session score')).toBeInTheDocument()
    expect(screen.getByText('Mastered')).toBeInTheDocument()
    expect(screen.getByText('In progress')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /play again/i })).toBeInTheDocument()
  })

  it('frames a replay as uncounted free-play instead of a pass', () => {
    render(
      <AdventureOutcomeModal
        open
        run={{ ...run, mode: 'replay', passed: false, mastery: { ...run.mastery, passed: false } }}
        onRestart={vi.fn()}
        onClose={vi.fn()}
      />,
    )
    expect(screen.getByText('Free play')).toBeInTheDocument()
    expect(screen.queryByText('Challenge unlocked')).not.toBeInTheDocument()
    expect(screen.queryByText('Session score')).not.toBeInTheDocument()
  })
})
