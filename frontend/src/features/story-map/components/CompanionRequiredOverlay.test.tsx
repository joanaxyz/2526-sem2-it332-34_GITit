import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import { CompanionRequiredOverlay } from './CompanionRequiredOverlay'

const targetBox = {
  x: 360,
  y: 90,
  top: 90,
  right: 480,
  bottom: 132,
  left: 360,
  width: 120,
  height: 42,
  toJSON: () => ({}),
}

describe('CompanionRequiredOverlay', () => {
  beforeEach(() => {
    Object.defineProperty(window, 'matchMedia', {
      configurable: true,
      value: vi.fn(() => ({
        matches: false,
        media: '',
        onchange: null,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        addListener: vi.fn(),
        removeListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    })
    vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockReturnValue(targetBox)
  })

  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
  })

  it('spotlights the Shop and takes the learner there from the primary action', async () => {
    render(
      <MemoryRouter initialEntries={['/stories/arcane-spire']}>
        <a href="/shop" data-companion-shop-target="desktop">Shop</a>
        <CompanionRequiredOverlay open onDismiss={vi.fn()} />
        <Routes>
          <Route path="/stories/:storySlug" element={null} />
          <Route path="/shop" element={<div>Shop destination</div>} />
        </Routes>
      </MemoryRouter>,
    )

    expect(await screen.findByRole('dialog', {
      name: 'Choose a companion before you enter',
    })).toBeInTheDocument()
    expect(screen.getByTestId('workspace-tour-spotlight')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Shop' })).toHaveClass(
      'is-companion-required-target',
    )
    expect(screen.getByText('Choose a companion before you enter')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Buy a companion' }))

    await waitFor(() => expect(screen.getByText('Shop destination')).toBeInTheDocument())
  })

  it('dismisses without navigating when the learner chooses not now', async () => {
    const onDismiss = vi.fn()
    render(
      <MemoryRouter>
        <a href="/shop" data-companion-shop-target="desktop">Shop</a>
        <CompanionRequiredOverlay open onDismiss={onDismiss} />
      </MemoryRouter>,
    )

    fireEvent.click(await screen.findByRole('button', { name: 'Not now' }))
    expect(onDismiss).toHaveBeenCalledOnce()
  })
})
