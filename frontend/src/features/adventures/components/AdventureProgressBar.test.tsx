import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { AdventureProgressBar } from './AdventureProgressBar'
import type { AdventureRun } from '@/features/adventures/types'

const run = {
  current_wave: 1,
  total_waves: 4,
  replay: false,
  mastery: {
    commands_mastered: 0,
    total_commands: 4,
    total_achievable: 4,
    passed: false,
  },
} as AdventureRun

describe('AdventureProgressBar', () => {
  afterEach(() => cleanup())

  it('stories active wave progress in the battle footer', () => {
    render(<AdventureProgressBar run={run} variant="battle" currentWave={1} totalWaves={4} />)

    const progress = screen.getByRole('progressbar', { name: 'Wave 1 of 4' })
    expect(progress).toHaveAttribute('aria-valuenow', '0')
    expect(progress).toHaveAttribute('aria-valuemax', '4')
    expect(progress).toHaveAttribute('aria-valuetext', 'Wave 1 of 4, 0 cleared')
    expect(progress.querySelector('[style*="0%"]')).not.toBeNull()
  })

  it('fills only for cleared waves while an adventure is in progress', () => {
    render(<AdventureProgressBar run={run} variant="battle" currentWave={2} totalWaves={4} />)

    const progress = screen.getByRole('progressbar', { name: 'Wave 2 of 4' })
    expect(progress).toHaveAttribute('aria-valuenow', '1')
    expect(progress).toHaveAttribute('aria-valuetext', 'Wave 2 of 4, 1 cleared')
    expect(progress.querySelector('[style*="25%"]')).not.toBeNull()
  })

  it('fills completely when the adventure is completed', () => {
    render(
      <AdventureProgressBar
        run={{ ...run, status: 'completed' }}
        variant="battle"
        currentWave={4}
        totalWaves={4}
      />,
    )

    const progress = screen.getByRole('progressbar', { name: 'Wave 4 of 4' })
    expect(progress).toHaveAttribute('aria-valuenow', '4')
    expect(progress.querySelector('[style*="100%"]')).not.toBeNull()
  })
})
