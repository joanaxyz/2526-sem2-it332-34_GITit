import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { AdventureAttempt, AdventureRun } from '@/features/adventures/types'
import { AdventureContextPanel } from './AdventureContextPanel'
import { AdventureWorkspaceTour } from './AdventureWorkspaceTour'

describe('AdventureWorkspaceTour', () => {
  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
  })

  it('walks through scoring and completion using the current wave budgets without opening the guide', async () => {
    vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockReturnValue({
      x: 80, y: 100, left: 80, top: 100, right: 380, bottom: 260,
      width: 300, height: 160, toJSON: () => ({}),
    })
    const onClose = vi.fn()
    const onOpenGuide = vi.fn()
    const run = { id: 81, stars: 0, total_waves: 2 } as AdventureRun
    const attempt = {
      id: 10,
      wave: 0,
      level: { title: 'Save the project', is_required: true },
      scenario_context: { story: 'Prepare the project.', task: 'Commit the file.' },
      objective_checks: [{ label: 'Commit the file', satisfied: false }],
      command_budget: { min_counted_commands: 2, max_counted_commands: 5 },
      counts: { command_count: 4, counted_command_count: 1 },
    } as AdventureAttempt
    const view = (currentAttempt: AdventureAttempt) => (
      <>
        <div data-tour-target="adventure-story">
          <AdventureContextPanel run={run} attempt={currentAttempt} />
        </div>
        <button data-tour-target="level-guide" onClick={onOpenGuide}>Command guide</button>
        <div data-testid="battle-stage" />
        <div data-tour-target="project-files" />
        <input data-command-input />
        <AdventureWorkspaceTour runId={run.id} onClose={onClose} />
      </>
    )
    const { rerender } = render(view(attempt))

    expect(await screen.findByRole('heading', { name: 'Review the objective' })).toBeInTheDocument()
    expect(screen.getByText('1 / 5')).toBeInTheDocument()
    expect(screen.getByText('≤ 2 commands')).toBeInTheDocument()
    for (const heading of [
      'Earn up to 3 stars', 'Watch the command limit', 'The guide costs a star',
      'See command results', 'Check project files', 'Run a Git command', 'Complete every wave',
    ]) {
      fireEvent.click(screen.getByRole('button', { name: /^next$/i }))
      expect(await screen.findByRole('heading', { name: heading })).toBeInTheDocument()
    }
    expect(screen.getByText('8 / 8')).toBeInTheDocument()

    rerender(view({
      ...attempt,
      wave: 1,
      counts: { command_count: 0, counted_command_count: 0 },
      command_budget: { min_counted_commands: 3, max_counted_commands: 6 },
    }))
    expect(screen.getByText('0 / 6')).toBeInTheDocument()
    expect(screen.getByText('≤ 3 commands')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /start adventure/i }))
    expect(onClose).toHaveBeenCalledOnce()
    expect(onOpenGuide).not.toHaveBeenCalled()
  }, 15_000)
})
