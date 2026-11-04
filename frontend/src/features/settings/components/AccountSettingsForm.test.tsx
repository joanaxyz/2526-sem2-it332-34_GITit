import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '@/shared/api/apiError'
import { useAuthStore } from '@/shared/auth/useAuth'

import { AccountSettingsForm } from './AccountSettingsForm'

const mocks = vi.hoisted(() => ({ update: vi.fn(), confirm: vi.fn() }))
vi.mock('@/shared/auth/authApi', () => ({
  authApi: { updateAccount: mocks.update, confirmEmailChange: mocks.confirm },
}))

const user = { id: 42, username: 'archivist', email: 'archivist@example.com', is_staff: false }

function renderForm() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(<QueryClientProvider client={client}><AccountSettingsForm user={user} /></QueryClientProvider>)
}

beforeEach(() => {
  useAuthStore.getState().setSession('test-token', user)
})

afterEach(() => {
  cleanup()
  vi.resetAllMocks()
  useAuthStore.getState().clearSession()
})

describe('account settings', () => {
  it('edits and saves the username, updates the session, and retains the access token', async () => {
    mocks.update.mockResolvedValue({ user: { ...user, username: 'newarchivist' }, pending_email: null })
    renderForm()
    expect(screen.getByRole('button', { name: 'Save account' })).toBeDisabled()
    expect(screen.getByLabelText('Username')).not.toHaveAttribute('readonly')
    expect(screen.getByLabelText('Email')).not.toHaveAttribute('readonly')
    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'newarchivist' } })
    fireEvent.click(screen.getByRole('button', { name: 'Save account' }))
    await waitFor(() => expect(useAuthStore.getState().user?.username).toBe('newarchivist'))
    expect(mocks.update.mock.calls[0][0]).toEqual({ username: 'newarchivist', email: user.email })
    expect(useAuthStore.getState().accessToken).toBe('test-token')
    expect(screen.getByRole('button', { name: 'Save account' })).toBeDisabled()
  })

  it('shows duplicate username errors at the field and allows correction', async () => {
    mocks.update.mockRejectedValueOnce(new ApiError('Taken', 400, {}, { username: ['This username is taken.'] }))
    mocks.update.mockResolvedValue({ user: { ...user, username: 'available' }, pending_email: null })
    renderForm()
    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'taken' } })
    fireEvent.click(screen.getByRole('button', { name: 'Save account' }))
    expect(await screen.findByText('This username is taken.')).toBeInTheDocument()
    expect(screen.getByLabelText('Username')).toHaveAttribute('aria-invalid', 'true')
    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'available' } })
    fireEvent.click(screen.getByRole('button', { name: 'Save account' }))
    await waitFor(() => expect(useAuthStore.getState().user?.username).toBe('available'))
  })

  it('keeps the old email until the new inbox code is confirmed', async () => {
    mocks.update.mockResolvedValue({ user, pending_email: 'new@example.com' })
    mocks.confirm.mockResolvedValue({ ...user, email: 'new@example.com' })
    renderForm()
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'new@example.com' } })
    fireEvent.click(screen.getByRole('button', { name: 'Save account' }))
    const code = await screen.findByLabelText('Email verification code')
    expect(useAuthStore.getState().user?.email).toBe(user.email)
    expect(screen.getByRole('button', { name: 'Send a new code' })).toBeDisabled()
    fireEvent.change(code, { target: { value: '123456' } })
    fireEvent.click(screen.getByRole('button', { name: 'Confirm email' }))
    await waitFor(() => expect(useAuthStore.getState().user?.email).toBe('new@example.com'))
    expect(mocks.confirm.mock.calls[0][0]).toEqual({ code: '123456' })
    expect(screen.queryByLabelText('Email verification code')).not.toBeInTheDocument()
  })

  it('displays wrong-code errors and lets the player edit the address', async () => {
    mocks.update.mockResolvedValue({ user, pending_email: 'new@example.com' })
    mocks.confirm.mockRejectedValue(new ApiError('Wrong code', 400, {}, { code: ['That code has expired.'] }))
    renderForm()
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'new@example.com' } })
    fireEvent.click(screen.getByRole('button', { name: 'Save account' }))
    fireEvent.change(await screen.findByLabelText('Email verification code'), { target: { value: '123456' } })
    fireEvent.click(screen.getByRole('button', { name: 'Confirm email' }))
    expect(await screen.findByText('That code has expired.')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Edit email' }))
    expect(screen.getByLabelText('Email')).toBeEnabled()
    expect(screen.getByRole('button', { name: 'Save account' })).toBeEnabled()
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'different@example.com' } })
    expect(screen.getByRole('button', { name: 'Save account' })).toBeEnabled()
    fireEvent.click(screen.getByRole('button', { name: 'Save account' }))
    expect(await screen.findByLabelText('Email verification code')).toBeInTheDocument()
    expect(screen.queryByText('That code has expired.')).not.toBeInTheDocument()
  })

  it('keeps edits available after a network failure and prevents duplicate saves while pending', async () => {
    let reject!: (reason: Error) => void
    mocks.update.mockReturnValue(new Promise((_, fail) => { reject = fail }))
    renderForm()
    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'newarchivist' } })
    fireEvent.click(screen.getByRole('button', { name: 'Save account' }))
    expect(await screen.findByRole('button', { name: 'Saving…' })).toBeDisabled()
    expect(screen.getByLabelText('Username')).toBeDisabled()
    await act(async () => reject(new Error('Could not reach the server.')))
    expect(await screen.findByText('Could not reach the server.')).toBeInTheDocument()
    expect(screen.getByLabelText('Username')).toHaveValue('newarchivist')
    expect(screen.getByRole('button', { name: 'Save account' })).toBeEnabled()
  })
})
