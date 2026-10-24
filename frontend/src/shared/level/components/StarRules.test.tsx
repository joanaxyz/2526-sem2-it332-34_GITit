import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { StarTriplet } from './LevelStatValues'

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})

describe('star rules reminder', () => {
  it('opens the mascot bubble from the stars, closes with Escape, and can reopen', async () => {
    vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockReturnValue({
      x: 80, y: 100, left: 80, top: 100, right: 380, bottom: 260,
      width: 300, height: 160, toJSON: () => ({}),
    })
    render(<StarTriplet count={2} />)
    const trigger = screen.getByRole('button', { name: 'Star rules: 2 of 3 stars' })
    trigger.focus()
    fireEvent.click(trigger)

    expect(await screen.findByRole('dialog', { name: 'How to earn stars' })).toBeInTheDocument()
    expect(screen.getByAltText('Learning guide')).toBeInTheDocument()
    expect(screen.getByText('Finish within the Star target with no more than one retry.')).toBeInTheDocument()
    expect(screen.getByText('Finish within the Star target after two or more retries.')).toBeInTheDocument()
    expect(screen.getByText('Finish using more commands than the Star target.')).toBeInTheDocument()
    expect(screen.queryByText(/Opening the command guide/)).not.toBeInTheDocument()
    expect(trigger).toHaveAttribute('aria-expanded', 'true')

    fireEvent.keyDown(window, { key: 'Escape' })
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(trigger).toHaveFocus()
    fireEvent.click(trigger)
    await screen.findByRole('dialog', { name: 'How to earn stars' })
    fireEvent.click(screen.getByRole('button', { name: 'Got it' }))
    expect(trigger).toHaveAttribute('aria-expanded', 'false')
  })

  it('includes the scenario and guide rules for plain adventures', async () => {
    vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockReturnValue({
      x: 80, y: 100, left: 80, top: 100, right: 380, bottom: 260,
      width: 300, height: 160, toJSON: () => ({}),
    })
    render(<StarTriplet count={0} mode="adventure" />)
    fireEvent.click(screen.getByRole('button', { name: 'Star rules: 0 of 3 stars' }))

    await screen.findByRole('dialog', { name: 'How to earn stars' })
    expect(screen.getByText(/your lowest scenario score becomes your level score/)).toBeInTheDocument()
    expect(screen.getByText(/Opening the command guide never costs a star/)).toBeInTheDocument()
  })
})
