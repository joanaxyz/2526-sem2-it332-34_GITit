import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'

import type { LearningChapter } from '@/features/story-map/types'

import { StoryChapterList } from './StoryChapterList'

const baseChapter: LearningChapter = {
  adventure_level_count: 1,
  challenge_count: 0,
  chest_schedule: [],
  command_skill_count: 1,
  description: '',
  id: 1,
  is_orientation: false,
  is_playable: true,
  level_completion: { denominator: 1, numerator: 0, value: 0 },
  lock_reason: '',
  locked: false,
  number: 1,
  slug: 'module-1',
  sort_order: 1,
  story: { id: 1, slug: 'legacy', title: 'Legacy', world_slug: 'arcane-spire' },
  title: 'Module 1',
}

describe('StoryChapterList', () => {
  afterEach(cleanup)

  it('keeps Module 0 in the chapter list and retains the diamond selector', () => {
    const selectChapter = vi.fn()
    const orientation = {
      ...baseChapter,
      adventure_level_count: 0,
      command_skill_count: 0,
      id: 0,
      is_orientation: true,
      level_completion: { denominator: 0, numerator: 0, value: 0 },
      number: 0,
      slug: 'module-0-orientation',
      sort_order: 0,
      title: 'Module 0',
    }
    render(
      <MemoryRouter>
        <StoryChapterList
          chapters={[orientation, baseChapter]}
          activeChapterId={orientation.id}
          onSelectChapter={selectChapter}
        />
      </MemoryRouter>,
    )

    expect(screen.getByRole('link', { name: 'All stories' })).toHaveAttribute('href', '/stories')
    const trigger = screen.getByRole('button', { name: /current 00 Module 0/i })
    expect(trigger.querySelector('.story-chapter-diamond')).toBeInTheDocument()
    fireEvent.click(trigger)
    const menu = screen.getByRole('group', { name: 'Chapters' })
    expect(menu?.parentElement).toBe(document.body)
    expect(screen.queryByText('Onboarding')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: '00 Module 0' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /01 Module 1/i }))
    expect(selectChapter).toHaveBeenCalledWith(baseChapter.id)
    expect(trigger).toHaveAttribute('aria-expanded', 'false')
  })
})
