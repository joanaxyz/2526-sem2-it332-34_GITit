import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { HealthBar } from './HealthBar'

describe('HealthBar', () => {
  afterEach(() => cleanup())

  it('drains from the left edge instead of collapsing toward center', () => {
    render(<HealthBar value={2} max={4} aria-label="Blue health" />)

    const meter = screen.getByRole('meter', { name: 'Blue health' })
    const fill = meter.querySelector('.health-bar__fill')

    expect(fill).not.toBeNull()
    expect(fill).toHaveStyle({
      transform: 'scaleX(0.5)',
      transformOrigin: 'left center',
    })
  })
})
