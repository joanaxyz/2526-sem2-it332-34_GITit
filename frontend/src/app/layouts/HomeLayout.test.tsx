import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes, useNavigate } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { HomeLayout } from './HomeLayout'

vi.mock('@/shared/audio/battleAudio', () => ({ startBackgroundMusic: vi.fn(), stopBackgroundMusic: vi.fn() }))
vi.mock('@/shared/components/CursorGlow', () => ({ CursorGlow: () => null }))
vi.mock('@/shared/navigation/AppNavigation', () => ({ AppTopbar: () => null, AppMobileNav: () => null }))
vi.mock('@/features/onboarding/components/OnboardingProvider', () => ({ OnboardingProvider: ({ children }: { children: React.ReactNode }) => children }))

afterEach(cleanup)

function Page() {
  const navigate = useNavigate()
  return <button onClick={() => navigate('/shop')}>Visit shop</button>
}

function setup(path: string) {
  render(<MemoryRouter initialEntries={[path]}><Routes><Route element={<HomeLayout />}>
    <Route path="*" element={<Page />} />
  </Route></Routes></MemoryRouter>)
}

describe('general learning help routes', () => {
  it.each(['/home', '/stories', '/stories/arcane-spire', '/shop'])('offers independent help on %s', (path) => {
    setup(path)
    expect(screen.getByRole('dialog', { name: 'Ask Git-It' })).toBeInTheDocument()
  })

  it('keeps its separate window open when navigating from Dashboard to Shop', () => {
    setup('/home')
    fireEvent.click(screen.getByRole('button', { name: 'Visit shop' }))
    expect(screen.getByRole('dialog', { name: 'Ask Git-It' })).toBeInTheDocument()
  })

  it('does not add general help to settings', () => {
    setup('/settings')
    expect(screen.queryByRole('dialog', { name: 'Ask Git-It' })).not.toBeInTheDocument()
  })
})
