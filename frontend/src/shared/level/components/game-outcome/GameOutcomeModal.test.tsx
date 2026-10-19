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
  it.each([0.5, 1, 1.5, 2, 2.5, 3])('selects the %s-star victory variant', (stars) => {
    renderOutcome(stars)

    expect(screen.getByRole('img', { name: `${stars} of 3 stars earned` }))
      .toHaveAttribute('src', `/outcomes/win-${stars}.webp`)
  })

  it('always shows the loss artwork for a failed run', () => {
    renderOutcome(2.5, 'failure')

    expect(screen.getByRole('img', { name: 'No stars earned' }))
      .toHaveAttribute('src', '/outcomes/lose.webp')
  })

  it.each([0, undefined, NaN, Infinity])('keeps the icon crest when no grade is available (%s)', (stars) => {
    renderOutcome(stars)

    expect(document.querySelector('.game-outcome-star-art')).not.toBeInTheDocument()
    expect(document.querySelector('.game-outcome-icon-crest')).toBeInTheDocument()
  })
})
