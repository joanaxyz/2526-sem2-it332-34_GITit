import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes, useNavigate, useParams } from 'react-router-dom'

import { startBackgroundMusic, stopBackgroundMusic } from '@/shared/audio/battleAudio'
import { LevelLayout } from './LevelLayout'

vi.mock('@/shared/audio/battleAudio', () => ({
  startBackgroundMusic: vi.fn(),
  stopBackgroundMusic: vi.fn(),
}))

function ChallengeRunProbe() {
  const navigate = useNavigate()
  const { runId } = useParams()
  const isFirstRun = runId === '1'

  return (
    <button type="button" onClick={() => navigate(isFirstRun ? '/challenge-runs/2' : '/home')}>
      {isFirstRun ? 'Retry result' : 'Leave battle'}
    </button>
  )
}

describe('LevelLayout', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  it('requests battle music again when retry navigation replaces the active run', async () => {
    render(
      <MemoryRouter initialEntries={['/challenge-runs/1']}>
        <Routes>
          <Route element={<LevelLayout />}>
            <Route path="/challenge-runs/:runId" element={<ChallengeRunProbe />} />
          </Route>
          <Route path="/home" element={<div>Home</div>} />
        </Routes>
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(startBackgroundMusic).toHaveBeenCalledWith('inside')
    })
    expect(startBackgroundMusic).toHaveBeenCalledTimes(1)

    fireEvent.click(screen.getByRole('button', { name: /retry result/i }))

    await waitFor(() => {
      expect(startBackgroundMusic).toHaveBeenCalledTimes(2)
    })
    expect(startBackgroundMusic).toHaveBeenLastCalledWith('inside')
    expect(stopBackgroundMusic).not.toHaveBeenCalled()

    fireEvent.click(screen.getByRole('button', { name: /leave battle/i }))

    await waitFor(() => {
      expect(stopBackgroundMusic).toHaveBeenCalledWith('inside')
    })
    expect(stopBackgroundMusic).toHaveBeenCalledTimes(1)
  })
})
