import { act, cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { VIGNETTE_COMMANDS } from '@/features/landing/utils/landingContent'
import { useAuthStore } from '@/shared/auth/useAuth'
import { LandingPage } from './LandingPage'

function renderLanding() {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/stories/arcane-spire" element={<h1>Story map</h1>} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('LandingPage', () => {
  afterEach(() => {
    cleanup()
    vi.useRealTimers()
    delete document.documentElement.dataset.motion
    useAuthStore.setState({ accessToken: null, user: null })
  })

  it('invites a visitor to register, and signs in through the story map', () => {
    renderLanding()

    expect(screen.getByRole('heading', { level: 1, name: /start reading the repository/i })).toBeInTheDocument()
    for (const link of screen.getAllByRole('link', { name: 'Begin your quest' })) {
      expect(link).toHaveAttribute('href', '/register')
    }
    expect(screen.getByRole('link', { name: 'Sign in' })).toHaveAttribute('href', '/stories/arcane-spire')
  })

  it('sends a live session straight to the story map', async () => {
    useAuthStore.setState({
      accessToken: 'test-token',
      user: { id: 13, username: 'archivist', email: 'archivist@example.test', is_staff: false },
    })
    renderLanding()

    expect(await screen.findByRole('heading', { name: 'Story map' })).toBeInTheDocument()
  })

  it('plays the scenario one command at a time until it clears', () => {
    vi.useFakeTimers()
    renderLanding()

    expect(screen.queryByText(VIGNETTE_COMMANDS[0].command)).not.toBeInTheDocument()
    act(() => vi.advanceTimersByTime(600))
    expect(screen.getByText(VIGNETTE_COMMANDS[0].command)).toBeInTheDocument()
    expect(screen.getByText(/HEAD → spellbook/)).toBeInTheDocument()

    // Each step schedules the next after it renders, so advance one at a time.
    for (let step = 1; step < VIGNETTE_COMMANDS.length; step += 1) act(() => vi.advanceTimersByTime(1700))
    expect(screen.getByText('Target state reached. Scenario cleared.')).toBeInTheDocument()
    expect(screen.getByText(/HEAD → main/)).toBeInTheDocument()
  })

  it('shows the finished scenario at once when motion is reduced', () => {
    document.documentElement.dataset.motion = 'reduced'
    renderLanding()

    for (const line of VIGNETTE_COMMANDS) expect(screen.getByText(line.command)).toBeInTheDocument()
    expect(screen.getByText('Target state reached. Scenario cleared.')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Replay' })).not.toBeInTheDocument()
  })
})
