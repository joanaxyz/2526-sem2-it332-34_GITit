import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '@/shared/api/apiError'
import { authApi } from '@/shared/auth/authApi'
import { useAuthStore } from '@/shared/auth/useAuth'
import { LoginForm } from './LoginForm'
import { RegisterForm } from './RegisterForm'
import { VerifyEmailForm } from './VerifyEmailForm'

const session = {
  access: 'test-access',
  user: { id: 11, username: 'archivist', email: 'archivist@example.test', is_staff: false },
}
let client: QueryClient

function renderEntry(register = false) {
  client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[register ? '/register' : '/login']}>
        <Routes>
          <Route path="/register" element={<RegisterForm />} />
          <Route path="/login" element={<LoginForm />} />
          <Route path="/verify-email" element={<VerifyEmailForm />} />
          <Route path="/stories/arcane-spire" element={<h1>Story map</h1>} />
          <Route path="/home" element={<h1>Home</h1>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function fillRegistration() {
  fireEvent.change(screen.getByPlaceholderText('Username'), { target: { value: 'archivist' } })
  fireEvent.change(screen.getByPlaceholderText('Email'), { target: { value: 'archivist@example.test' } })
  fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'safe-password-123' } })
  fireEvent.change(screen.getByPlaceholderText('Confirm password'), { target: { value: 'safe-password-123' } })
  fireEvent.click(screen.getByRole('button', { name: 'Create account' }))
}

function signIn() {
  fireEvent.change(screen.getByPlaceholderText('Username or email'), { target: { value: 'archivist' } })
  fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'safe-password-123' } })
  fireEvent.click(screen.getByRole('button', { name: 'Sign in' }))
}

describe('authentication entry destination', () => {
  beforeEach(() => {
    vi.spyOn(authApi, 'login').mockResolvedValue(session)
    vi.spyOn(authApi, 'register').mockResolvedValue({ user: session.user })
    vi.spyOn(authApi, 'confirmEmailVerification').mockResolvedValue(session)
  })
  afterEach(() => {
    cleanup()
    client.clear()
    useAuthStore.setState({ accessToken: null, user: null })
    vi.restoreAllMocks()
  })

  it('opens Stories after signing in', async () => {
    renderEntry()
    signIn()
    expect(await screen.findByRole('heading', { name: 'Story map' })).toBeInTheDocument()
    expect(useAuthStore.getState().user?.id).toBe(11)
  })

  it('asks a new account for its emailed code instead of signing it in', async () => {
    renderEntry(true)
    fillRegistration()
    expect(await screen.findByRole('heading', { name: 'Check your inbox' })).toBeInTheDocument()
    expect(screen.getByText('archivist@example.test')).toBeInTheDocument()
    expect(authApi.login).not.toHaveBeenCalled()
    expect(useAuthStore.getState().user).toBeNull()
  })

  it('opens Stories once the emailed code is confirmed', async () => {
    renderEntry(true)
    fillRegistration()
    fireEvent.change(await screen.findByPlaceholderText('000000'), { target: { value: '123456' } })
    expect(await screen.findByRole('heading', { name: 'Story map' })).toBeInTheDocument()
    expect(authApi.confirmEmailVerification).toHaveBeenCalledWith({ email: 'archivist@example.test', code: '123456' })
    expect(useAuthStore.getState().user?.id).toBe(11)
  })

  it('sends an unverified sign-in to the code screen for that account', async () => {
    vi.mocked(authApi.login).mockRejectedValue(
      new ApiError('Confirm your email to finish creating your account.', 403, {
        detail: 'Confirm your email to finish creating your account.',
        code: 'email_unverified',
        email: 'archivist@example.test',
      }),
    )
    renderEntry()
    signIn()
    expect(await screen.findByRole('heading', { name: 'Check your inbox' })).toBeInTheDocument()
    expect(screen.getByText('archivist@example.test')).toBeInTheDocument()
  })
})
