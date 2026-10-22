import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { StarRating } from './StarRating'

afterEach(cleanup)

describe('StarRating', () => {
  it.each([1, 2, 3])('renders %s earned stars from left to right', (stars) => {
    const { container } = render(<StarRating stars={stars} label="Difficulty progress" />)

    expect(screen.getByRole('img', { name: `Difficulty progress: ${stars} of 3` })).toBeInTheDocument()
    const icons = container.querySelectorAll('svg')
    expect(icons).toHaveLength(3)
    icons.forEach((icon, index) => {
      expect(icon).toHaveClass(index < stars ? 'fill-primary' : 'star-empty')
    })
  })

  it.each([0.5, 1.5, 2.5])('shows only whole stars for a fractional input (%s)', (stars) => {
    const { container } = render(<StarRating stars={stars} />)

    expect(screen.getByRole('img', { name: `Stars earned: ${Math.floor(stars)} of 3` })).toBeInTheDocument()
    expect(container.querySelectorAll('svg')).toHaveLength(3)
    expect(container.querySelector('[style*="clip-path"]')).not.toBeInTheDocument()
  })

  it('caps scores at three stars', () => {
    render(<StarRating stars={4} />)

    expect(screen.getByRole('img', { name: 'Stars earned: 3 of 3' })).toBeInTheDocument()
  })

  it.each([undefined, NaN, Infinity, -1, 0])('renders %s as no stars', (stars) => {
    render(<StarRating stars={stars} />)

    expect(screen.getByRole('img', { name: 'Stars earned: 0 of 3' })).toBeInTheDocument()
  })
})
