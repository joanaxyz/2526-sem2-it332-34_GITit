import { cleanup, render, screen } from '@testing-library/react'
import { Star } from 'lucide-react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { GameOutcomeModal } from './GameOutcomeModal'

vi.mock('@/shared/utils/useLazyImage', () => ({
  useLazyImage: (key: string | null, loaders: Record<string, unknown>) => (
    key && key in loaders ? `/outcomes/${key}.webp` : null
  ),
}))

afterEach(cleanup)

function renderOutcome(stars?: number, tone: 'success' | 'failure' = 'success') {
  return render(
    <GameOutcomeModal
      open
      onClose={() => {}}
      title="Run result"
      icon={Star}
      headline="Run complete"
      message="Your result"
      stars={stars}
      tone={tone}
    />,
  )
}

describe('GameOutcomeModal star artwork', () => {
  it.each(['success', 'failure'] as const)('identifies the level on the %s screen', (tone) => {
    render(<GameOutcomeModal open onClose={() => {}} title="Run result" icon={Star}
      headline="Result" message="Your result" tone={tone}
      level={{ label: 'Level 3', title: 'Staging and Committing' }} />)

    expect(screen.getByRole('dialog')).toContainElement(screen.getByText('Level 3'))
    expect(screen.getByRole('dialog')).toContainElement(screen.getByText('Staging and Committing'))
  })

  it('keeps assessments free of star grades, including failed checkpoints', () => {
    render(<GameOutcomeModal open onClose={() => {}} title="Transfer result" icon={Star}
      headline="Result recorded" message="First attempt preserved" tone="failure" stars={0} showStars={false} />)
    expect(screen.queryByRole('img', { name: 'No stars earned' })).not.toBeInTheDocument()
  })
  it.each([1, 2, 3])('selects the %s-star victory variant', (stars) => {
    renderOutcome(stars)

    expect(screen.getByRole('img', { name: `${stars} of 3 stars earned` }))
      .toHaveAttribute('src', `/outcomes/win-${stars}.webp`)
  })

  it('always shows the loss artwork for a failed run', () => {
    renderOutcome(3, 'failure')

    expect(screen.getByRole('img', { name: 'No stars earned' }))
      .toHaveAttribute('src', '/outcomes/lose.webp')
  })

  it.each([0, undefined, NaN, Infinity])('keeps the icon crest when no grade is available (%s)', (stars) => {
    renderOutcome(stars)

    expect(document.querySelector('.game-outcome-star-art')).not.toBeInTheDocument()
    expect(document.querySelector('.game-outcome-icon-crest')).toBeInTheDocument()
  })
})
