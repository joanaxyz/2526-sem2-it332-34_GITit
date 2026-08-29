import { render, screen } from '@testing-library/react'
import { GitBranch } from 'lucide-react'
import { describe, expect, it } from 'vitest'

import { LevelStoryCard } from '@/shared/level/components/LevelContextPanel'

describe('LevelStoryCard copy details', () => {
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
})
