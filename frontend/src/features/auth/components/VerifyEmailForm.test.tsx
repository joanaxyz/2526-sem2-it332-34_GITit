import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '@/shared/api/apiError'

import { VerifyEmailForm } from './VerifyEmailForm'

const mocks = vi.hoisted(() => ({ confirm: vi.fn(), resend: vi.fn() }))

vi.mock('@/shared/auth/authApi', () => ({
  authApi: { confirmEmailVerification: mocks.confirm, resendEmailVerification: mocks.resend },
}))

const INVALID = 'That code is incorrect or has expired. Check it or send a new one.'

function renderForm(entry = '/verify-email?email=archivist%40example.test') {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[entry]}>
        <VerifyEmailForm />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
  vi.useRealTimers()
})

describe('VerifyEmailForm', () => {
  it('keeps only digits and submits a pasted code once', async () => {
    mocks.confirm.mockRejectedValue(new ApiError(INVALID, 400, { detail: INVALID }))
    renderForm()

    fireEvent.change(screen.getByPlaceholderText('000000'), { target: { value: '12 34-56' } })

    expect(screen.getByPlaceholderText('000000')).toHaveValue('123456')
    expect(await screen.findByText(INVALID)).toBeInTheDocument()
    expect(mocks.confirm).toHaveBeenCalledTimes(1)
    expect(mocks.confirm).toHaveBeenCalledWith({ email: 'archivist@example.test', code: '123456' })
  })

  it('lets the player retry the same code with the button', async () => {
    mocks.confirm.mockRejectedValue(new ApiError(INVALID, 400, { detail: INVALID }))
    renderForm()
    fireEvent.change(screen.getByPlaceholderText('000000'), { target: { value: '123456' } })
    await screen.findByText(INVALID)

    fireEvent.click(screen.getByRole('button', { name: 'Verify email' }))

    await waitFor(() => expect(mocks.confirm).toHaveBeenCalledTimes(2))
  })

  it('holds the resend button through the cooldown, then sends a new code', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
    mocks.resend.mockResolvedValue({ detail: 'If that account still needs verification, a new code is on its way.' })
    renderForm()

    expect(screen.getByRole('button', { name: 'Send a new code in 60s' })).toBeDisabled()
    await act(async () => {
      vi.advanceTimersByTime(60_000)
    })
    fireEvent.click(screen.getByRole('button', { name: 'Send a new code' }))

    expect(await screen.findByRole('status')).toHaveTextContent('a new code is on its way')
    expect(mocks.resend).toHaveBeenCalledWith({ email: 'archivist@example.test' })
    expect(screen.getByRole('button', { name: 'Send a new code in 60s' })).toBeDisabled()
  })

  it('points back to sign-in when the page has no email to verify', () => {
    renderForm('/verify-email')

    expect(screen.getByRole('heading', { name: 'Confirm your email' })).toBeInTheDocument()
    expect(screen.queryByPlaceholderText('000000')).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Back to sign in' })).toHaveAttribute('href', '/login')
  })
})
