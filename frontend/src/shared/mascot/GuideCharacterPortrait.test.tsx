import { act, cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { GuideCharacterPortrait } from './GuideCharacterPortrait'
import { applyGuideMascotVisibility } from './guideMascotVisibility'

const mocks = vi.hoisted(() => ({ usePlayerLoadout: vi.fn() }))

vi.mock('@/shared/player-loadout/usePlayerLoadout', () => ({ usePlayerLoadout: mocks.usePlayerLoadout }))

const companion = { label: 'Ember', sprites: { portrait: { src: '/companions/ember/portrait.png' } } }

afterEach(() => {
  cleanup()
  delete document.documentElement.dataset.guideMascotVisible
  mocks.usePlayerLoadout.mockReset()
})

describe('guide character portrait', () => {
  it('uses the Git-It mascot portrait while the mascot setting is on, even with a companion equipped', () => {
    mocks.usePlayerLoadout.mockReturnValue({ companion, hasCompanion: true })
    applyGuideMascotVisibility(true)
    render(<GuideCharacterPortrait alt="Learning guide" />)

    const portrait = screen.getByRole('img', { name: 'Learning guide' })
    expect(portrait).toHaveAttribute('src', '/mascot/portrait.png')
    expect(portrait).toHaveAttribute('data-guide-character', 'mascot')
    expect(mocks.usePlayerLoadout).not.toHaveBeenCalled()
  })

  it('uses the equipped companion portrait when the mascot is hidden and switches back live', () => {
    mocks.usePlayerLoadout.mockReturnValue({ companion, hasCompanion: true })
    applyGuideMascotVisibility(false)
    render(<GuideCharacterPortrait alt="Learning guide" />)

    expect(screen.getByRole('img', { name: 'Ember companion' })).toHaveAttribute('src', '/companions/ember/portrait.png')

    act(() => applyGuideMascotVisibility(true))
    expect(screen.getByRole('img', { name: 'Learning guide' })).toHaveAttribute('src', '/mascot/portrait.png')
  })

  it('falls back to the mascot portrait when the mascot is hidden and no companion is equipped', () => {
    mocks.usePlayerLoadout.mockReturnValue({ companion, hasCompanion: false })
    applyGuideMascotVisibility(false)
    render(<GuideCharacterPortrait alt="Learning guide" />)

    expect(screen.getByRole('img', { name: 'Learning guide' })).toHaveAttribute('data-guide-character', 'mascot')
  })
})
