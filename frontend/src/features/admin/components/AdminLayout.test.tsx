import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import { useAuthStore } from '@/shared/auth/useAuth'

import { AdminLayout } from './AdminLayout'

function renderLayout() {
  return render(
    <MemoryRouter initialEntries={['/admin']}>
      <Routes>
        <Route path="/home" element={<p>Player home</p>} />
        <Route path="/login" element={<p>Sign in</p>} />
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<p>Admin dashboard content</p>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  )
}

describe('AdminLayout access boundary', () => {
  afterEach(() => {
    cleanup()
    useAuthStore.setState({ accessToken: null, user: null })
  })

  it('renders the console and nested route for staff', () => {
    useAuthStore.setState({
      accessToken: 'staff-token',
      user: {
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        is_staff: true,
      },
    })

    renderLayout()

    expect(screen.getByText('Observatory Console')).toBeInTheDocument()
    expect(screen.getByText('Admin dashboard content')).toBeInTheDocument()
    expect(screen.getAllByRole('link', { name: 'Users' })).toHaveLength(2)
  })

  it('redirects signed-out users to login', () => {
    useAuthStore.setState({ accessToken: null, user: null })

    renderLayout()

    expect(screen.getByText('Sign in')).toBeInTheDocument()
    expect(screen.queryByText('Observatory Console')).not.toBeInTheDocument()
  })

  it('redirects non-staff users to the player app', () => {
    useAuthStore.setState({
      accessToken: 'player-token',
      user: {
        id: 2,
        username: 'player',
        email: 'player@example.com',
        is_staff: false,
      },
    })

    renderLayout()

    expect(screen.getByText('Player home')).toBeInTheDocument()
    expect(screen.queryByText('Observatory Console')).not.toBeInTheDocument()
  })
})
