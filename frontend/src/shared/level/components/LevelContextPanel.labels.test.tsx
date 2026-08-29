import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { LevelStoryCard } from '@/shared/level/components/LevelContextPanel'

const context = {
  story: 'A repository has an untracked README.',
  task: 'Stage README.md before committing.',
  details: [{ label: 'Commit message', value: 'ready' }],
}

describe('LevelStoryCard labels', () => {
  afterEach(() => cleanup())

  it('preserves the shared Adventure-facing defaults', () => {
    render(<LevelStoryCard title="Adventure" context={context} />)

    expect(screen.getByText('Story')).toBeVisible()
    expect(screen.getByText('Task')).toBeVisible()
    expect(screen.getByText('Copy details')).toBeVisible()
    expect(screen.getByText('Commit message')).toHaveClass('sr-only')
  })

  it('renders plain Challenge labels and visible required-value names', () => {
    render(
      <LevelStoryCard
        title="Challenge"
        context={context}
        labels={{
          story: 'Scenario',
          task: 'Objective',
          details: 'Required values',
          detailsAriaLabel: 'Values required by the challenge',
        }}
        showDetailLabels
      />,
    )

    expect(screen.getByText('Scenario')).toBeVisible()
    expect(screen.getByText('Objective')).toBeVisible()
    expect(screen.getByText('Required values')).toBeVisible()
    expect(screen.getByText('Commit message')).not.toHaveClass('sr-only')
    expect(screen.getByRole('list', { name: 'Values required by the challenge' })).toBeVisible()
    expect(screen.getByRole('button', { name: 'Copy Commit message' })).toBeVisible()
  })
})
