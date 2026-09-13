import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '@/shared/api/apiError'

import { RegisterForm } from './RegisterForm'

const mocks = vi.hoisted(() => ({ register: vi.fn(), login: vi.fn() }))

vi.mock('@/shared/auth/authApi', () => ({
  authApi: { register: mocks.register, login: mocks.login },
}))

const TOO_COMMON = 'This password is too common.'

function rejectedPassword() {
  return new ApiError(TOO_COMMON, 400, { password: [TOO_COMMON] }, { password: [TOO_COMMON] })
}

function renderForm() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <RegisterForm />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function fillValidForm() {
  fireEvent.change(screen.getByPlaceholderText('Username'), { target: { value: 'jcgako' } })
  fireEvent.change(screen.getByPlaceholderText('Email'), { target: { value: 'student@example.com' } })
  fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password' } })
  fireEvent.change(screen.getByPlaceholderText('Confirm password'), { target: { value: 'password' } })
}

function submit() {
  fireEvent.click(screen.getByRole('button', { name: 'Create account' }))
}

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

beforeEach(() => {
  mocks.login.mockResolvedValue(null)
})

describe('RegisterForm password rejection', () => {
  it('shows the rule Django rejected the password with, under the password field', async () => {
    mocks.register.mockRejectedValue(rejectedPassword())
    renderForm()
    fillValidForm()
    submit()

    // The bug this guards: a field-only 400 has no `detail`, so the form used to
    // show the bare "Bad Request" status text instead of the actual rule.
    expect(await screen.findByText(TOO_COMMON)).toBeInTheDocument()
    expect(screen.queryByText('Bad Request')).not.toBeInTheDocument()
    expect(document.querySelector('.auth-error-box')).toBeNull()
  })

  it('re-states the rule when the same password is submitted again', async () => {
    mocks.register.mockRejectedValue(rejectedPassword())
    renderForm()
    fillValidForm()
    submit()
    expect(await screen.findByText(TOO_COMMON)).toBeInTheDocument()

    // handleSubmit clears the form's errors on its way out, so an identically
    // worded second rejection still has to re-apply the message.
    submit()
    await waitFor(() => expect(mocks.register).toHaveBeenCalledTimes(2))
    expect(await screen.findByText(TOO_COMMON)).toBeInTheDocument()
  })

  it('falls back to the summary box for errors that belong to no field', async () => {
    mocks.register.mockRejectedValue(new ApiError('Service unavailable.', 503, { detail: 'Service unavailable.' }))
    renderForm()
    fillValidForm()
    submit()

    const box = await waitFor(() => {
      const found = document.querySelector('.auth-error-box')
      expect(found).not.toBeNull()
      return found as HTMLElement
    })
    expect(box).toHaveTextContent('Something went wrong. Try again.')
  })
})
