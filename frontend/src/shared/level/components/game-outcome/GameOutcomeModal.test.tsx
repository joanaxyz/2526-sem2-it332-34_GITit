import { cleanup, fireEvent, render, screen } from '@testing-library/react'
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

    expect(screen.getByRole('img', { name: `${stars} of 3 stars earned` }).querySelector('img'))
      .toHaveAttribute('src', `/outcomes/win-${stars}.webp`)
    expect(document.querySelectorAll('.game-outcome-star-cell.is-earned')).toHaveLength(stars)
    expect(document.querySelectorAll('.game-outcome-star-cell:not(.is-earned)')).toHaveLength(3 - stars)
  })

  it('always shows the loss artwork for a failed run', () => {
    renderOutcome(3, 'failure')

    expect(screen.getByRole('img', { name: 'No stars earned' }).querySelector('img'))
      .toHaveAttribute('src', '/outcomes/lose.webp')
  })

  it('shows three unlit stars for an explicit zero-star grade', () => {
    renderOutcome(0)

    expect(screen.getByRole('img', { name: 'No stars earned' }).querySelector('img'))
      .toHaveAttribute('src', '/outcomes/lose.webp')
    expect(document.querySelectorAll('.game-outcome-star-cell')).toHaveLength(3)
    expect(document.querySelectorAll('.game-outcome-star-cell.is-earned')).toHaveLength(0)
  })

  it('starts the sprite sequence after the artwork has loaded', () => {
    renderOutcome(2)

    const crest = screen.getByRole('img', { name: '2 of 3 stars earned' })
    expect(crest).not.toHaveClass('is-ready')
    fireEvent.load(crest.querySelector('img')!)
    expect(crest).toHaveClass('is-ready')
  })

  it('loads matching artwork and restarts the sequence when the grade changes', () => {
    const { rerender } = renderOutcome(3)
    fireEvent.load(screen.getByRole('img', { name: '3 of 3 stars earned' }).querySelector('img')!)

    rerender(<GameOutcomeModal open onClose={() => {}} title="Run result" icon={Star}
      headline="Run complete" message="Your result" stars={1} />)

    const crest = screen.getByRole('img', { name: '1 of 3 stars earned' })
    expect(crest).not.toHaveClass('is-ready')
    expect(crest.querySelector('img')).toHaveAttribute('src', '/outcomes/win-1.webp')
    expect(document.querySelectorAll('.game-outcome-star-cell.is-earned')).toHaveLength(1)
  })

  it('replays the same grade when the result is reopened', () => {
    const props = { onClose: () => {}, title: 'Run result', icon: Star, headline: 'Run complete', message: 'Your result', stars: 3 }
    const { rerender } = render(<GameOutcomeModal {...props} open />)
    fireEvent.load(screen.getByRole('img', { name: '3 of 3 stars earned' }).querySelector('img')!)

    rerender(<GameOutcomeModal {...props} open={false} />)
    rerender(<GameOutcomeModal {...props} open />)

    expect(screen.getByRole('img', { name: '3 of 3 stars earned' })).not.toHaveClass('is-ready')
  })

  it.each([undefined, NaN, Infinity])('keeps the icon crest when no grade is available (%s)', (stars) => {
    renderOutcome(stars)

    expect(document.querySelector('.game-outcome-star-art')).not.toBeInTheDocument()
    expect(document.querySelector('.game-outcome-icon-crest')).toBeInTheDocument()
  })
})

describe('GameOutcomeModal dismissal', () => {
  it('has no close button and closes on a click anywhere', () => {
    const close = vi.fn()
    render(<GameOutcomeModal open onClose={close} title="Run result" icon={Star} headline="Run complete" message="Your result" />)

    expect(screen.queryByRole('button', { name: 'Close modal' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByText('Your result'))
    expect(close).toHaveBeenCalledOnce()
  })

  it('lets header actions keep their own keyboard activation', () => {
    const close = vi.fn()
    render(<GameOutcomeModal open onClose={close} title="Run result" icon={Star} headline="Run complete" message="Your result"
      headerActions={<button type="button">Back to Map</button>} />)

    fireEvent.keyDown(screen.getByRole('button', { name: 'Back to Map' }), { key: 'Enter' })
    expect(close).not.toHaveBeenCalled()
    fireEvent.keyDown(screen.getByRole('dialog'), { key: 'Enter' })
    expect(close).toHaveBeenCalledOnce()
  })
})
