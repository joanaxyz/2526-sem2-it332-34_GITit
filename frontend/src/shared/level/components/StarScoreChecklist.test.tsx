import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { StarScoreChecklist } from './StarScoreChecklist'
import type { StarBreakdown } from './StarScoreChecklist'

afterEach(cleanup)

const threeStars: StarBreakdown = {
  stars: 3, available_stars: 3, counted_commands: 2, command_target: 2, graded_under_previous_rules: false, retry_count: 1,
  criteria: [
    { key: 'clear', state: 'earned', reason: null },
    { key: 'command_target', state: 'earned', reason: null },
    { key: 'retry_allowance', state: 'earned', reason: null },
  ],
}

describe('StarScoreChecklist', () => {
  it('explains all three earned stars and free commands', () => {
    render(<StarScoreChecklist breakdown={threeStars} />)
    expect(screen.getAllByText('+1 earned')).toHaveLength(3)
    expect(screen.getByText('2 / 2 counted commands.')).toBeInTheDocument()
    expect(screen.getByText('1 retry / 1 allowed.')).toBeInTheDocument()
    const summary = screen.getByText('What counts toward the score?')
    fireEvent.click(summary)
    expect(summary.closest('details')).toHaveAttribute('open')
    expect(screen.getByText(/Valid inspections, file edits and opening the command guide are free/)).toBeVisible()
  })

  it('explains the retry loss while keeping command and clear stars earned', () => {
    render(<StarScoreChecklist breakdown={{
      ...threeStars, stars: 2, available_stars: 2, retry_count: 2,
      criteria: [...threeStars.criteria.slice(0, 2), { key: 'retry_allowance', state: 'missed', reason: 'retry_allowance_exceeded' }],
    }} tier multiScenario savedStars={3} />)
    expect(screen.getAllByText('+1 earned')).toHaveLength(2)
    expect(screen.getByText('Not earned')).toBeInTheDocument()
    expect(screen.getByText('2 retries / 1 allowed.')).toBeInTheDocument()
    expect(screen.getByText(/across scenarios in this difficulty tier/)).toBeInTheDocument()
    expect(screen.getByText(/lowest scenario best/)).toBeInTheDocument()
    expect(screen.getByText(/Saved best for this level:/)).toHaveTextContent('3 / 3')
  })

  it('never shows an earned bonus for an unsolved failure', () => {
    render(<StarScoreChecklist breakdown={{
      ...threeStars, stars: 0, available_stars: 0,
      criteria: threeStars.criteria.map((criterion) => ({ ...criterion, state: 'missed', reason: 'not_cleared' })),
    }} />)
    expect(screen.getByText('The target state was not reached. No stars earned.')).toBeInTheDocument()
    expect(screen.getAllByText('Not earned')).toHaveLength(3)
    expect(within(screen.getByRole('region', { name: 'Star checklist' })).getByText('0 / 3')).toBeInTheDocument()
  })

  it('explains historical grades without inventing a retry penalty', () => {
    render(<StarScoreChecklist breakdown={{
      ...threeStars, stars: 2, available_stars: 2, graded_under_previous_rules: true,
      criteria: [...threeStars.criteria.slice(0, 2), { key: 'retry_allowance', state: 'missed', reason: 'previous_scoring_rules' }],
    }} />)
    expect(screen.getByText(/This run was graded under earlier scoring rules/)).toBeInTheDocument()
    expect(screen.queryByText(/retry allowance was exceeded/)).not.toBeInTheDocument()
  })
})
