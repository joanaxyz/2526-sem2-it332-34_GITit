import { cleanup, render, screen } from '@testing-library/react'
import { GitBranch } from 'lucide-react'
import { afterEach, describe, expect, it } from 'vitest'

import { LevelStoryCard } from '@/shared/level/components/LevelContextPanel'

describe('LevelStoryCard', () => {
  afterEach(() => cleanup())

  it('shows only the copy value while keeping the field name accessible', () => {
    render(
      <LevelStoryCard
        title="Adventure: Stage and commit"
        titleIcon={GitBranch}
        context={{
          story: 'Use the required commit message shown below.',
          task: '',
          details: [{ label: 'Commit message', value: 'Save staged work' }],
        }}
      />,
    )

    expect(screen.getByText('Save staged work')).toBeVisible()
    expect(screen.getByText('Commit message:')).toHaveClass('sr-only')
    expect(screen.getByRole('button', { name: 'Copy Commit message' })).toBeVisible()
  })

  it('can omit the repeated workspace header while retaining an accessible name', () => {
    render(
      <LevelStoryCard
        title="Clean Snapshots"
        context={{ story: 'Inspect the repository.', task: 'Repair the commit.', details: [] }}
        showHeader={false}
      />,
    )

    expect(screen.getByLabelText('Clean Snapshots')).toBeVisible()
    expect(screen.queryByText('Level Context')).not.toBeInTheDocument()
    expect(screen.queryByText('Clean Snapshots')).not.toBeInTheDocument()
    expect(screen.getByText('Inspect the repository.')).toBeVisible()
  })
})
