import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { StarRating } from './StarRating'

afterEach(cleanup)

describe('StarRating', () => {
  it('includes half stars in its accessible score', () => {
    render(<StarRating fillStates={['full', 'half', 'empty']} label="Difficulty progress" />)

    expect(screen.getByRole('img', { name: 'Difficulty progress: 1.5 of 3' })).toBeInTheDocument()
  })

  it('only counts the three visible star slots', () => {
    render(<StarRating fillStates={['full', 'full', 'full', 'full']} />)

    expect(screen.getByRole('img', { name: 'Stars earned: 3 of 3' })).toBeInTheDocument()
  })

  it.each([0.5, 1.5, 2.5])('renders a numeric %s rating with a half star', (stars) => {
    const { container } = render(<StarRating stars={stars} />)

    expect(screen.getByRole('img', { name: `Stars earned: ${stars} of 3` })).toBeInTheDocument()
    expect(container.querySelector('[style*="clip-path: inset(0 50% 0 0)"]')).toBeInTheDocument()
  })

  it.each([undefined, NaN, Infinity, -1, 0])('renders %s as no stars', (stars) => {
    render(<StarRating stars={stars} />)

    expect(screen.getByRole('img', { name: 'Stars earned: 0 of 3' })).toBeInTheDocument()
  })
})
