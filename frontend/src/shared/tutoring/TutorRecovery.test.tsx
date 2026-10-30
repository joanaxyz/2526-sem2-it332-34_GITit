import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '@/shared/api/apiError'
import { useAuthStore } from '@/shared/auth/useAuth'
import { TutorChatPanel } from './TutorChatPanel'
import { tutorApi, type TutorReply } from './tutorApi'
import { findOfflineFaq } from './offlineFaqs'
import { retrySeconds } from './tutorRecovery'

vi.mock('./tutorApi', () => ({ tutorApi: { chat: vi.fn() } }))
const answer: TutorReply = { reply: 'A branch names a line of work.', suggested_topics: [], scenario_related: false, response_kind: 'answer' }
const home = { surface: 'home' } as const

beforeEach(() => {
  Object.defineProperty(navigator, 'onLine', { configurable: true, value: true })
  useAuthStore.getState().setSession('test', { id: 1, username: 'learner', email: 'learner@example.com', is_staff: false })
  vi.mocked(tutorApi.chat).mockReset().mockResolvedValue(answer)
})
afterEach(() => { cleanup(); useAuthStore.getState().clearSession(); vi.useRealTimers() })

async function ask(message: string) {
  await act(async () => {
    fireEvent.change(screen.getByRole('textbox'), { target: { value: message } })
    fireEvent.click(screen.getByRole('button', { name: 'Send question' }))
  })
}

describe('tutor recovery', () => {
  it.each(['http', 'provider'])('honors %s retry timing and waits for explicit retry', async (source) => {
    vi.useFakeTimers()
    if (source === 'http') vi.mocked(tutorApi.chat).mockRejectedValueOnce(new ApiError('busy', 429, { retry_after_seconds: 2 }))
    else vi.mocked(tutorApi.chat).mockResolvedValueOnce({ ...answer, response_kind: 'unavailable', unavailable_reason: 'rate_limited', retry_after_seconds: 2 })
    render(<TutorChatPanel context={home} />)
    await ask('Explain branches')
    expect(screen.getByRole('textbox')).toHaveValue('Explain branches')
    expect(screen.getByText('Retry in 2s')).toBeVisible()
    expect(screen.getByRole('button', { name: 'Send question' })).toBeDisabled()
    expect(screen.getByRole('textbox')).toBeEnabled()
    expect(screen.getByRole('status')).toHaveTextContent('short break')
    const announcement = screen.getByRole('status').textContent
    fireEvent.click(screen.getByRole('button', { name: 'Browse FAQS' }))
    expect(screen.getByRole('region', { name: 'Saved Git explanations' })).toBeVisible()
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    await act(async () => { await vi.advanceTimersByTimeAsync(2000) })
    expect(tutorApi.chat).toHaveBeenCalledTimes(1)
    expect(screen.getByRole('status').textContent).toBe(announcement)
    expect(screen.getByRole('button', { name: 'Retry question' })).toBeEnabled()
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: 'Retry question' })) })
    expect(screen.getByText(answer.reply)).toBeVisible()
    expect(vi.mocked(tutorApi.chat).mock.calls[1][0].history).toEqual([])
  })

  it('shares the cooldown across windows and clears it after account changes', async () => {
    vi.useFakeTimers()
    vi.mocked(tutorApi.chat).mockRejectedValueOnce(new ApiError('busy', 429, {}))
    const view = render(<TutorChatPanel context={home} />)
    await ask('Explain branches')
    expect(screen.getByText('Retry in 60s')).toBeVisible()
    view.rerender(<TutorChatPanel context={{ surface: 'command_guide', run_id: 17, teaching_key: 'add', guide_token: 'signed' }} />)
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Explain staging' } })
    expect(screen.getByRole('button', { name: 'Send question' })).toBeDisabled()
    await act(async () => { useAuthStore.getState().setSession('other', { id: 2, username: 'other', email: 'other@example.com', is_staff: false }) })
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Explain staging' } })
    expect(screen.getByRole('button', { name: 'Send question' })).toBeEnabled()
  })

  it('settles a hung request after 40 seconds and ignores its late answer', async () => {
    vi.useFakeTimers()
    let resolve!: (value: TutorReply) => void
    vi.mocked(tutorApi.chat).mockImplementationOnce(() => new Promise((done) => { resolve = done }))
    render(<TutorChatPanel context={home} />)
    await ask('Explain branches')
    const signal = vi.mocked(tutorApi.chat).mock.calls[0][1]
    await act(async () => { await vi.advanceTimersByTimeAsync(40000) })
    expect(signal.aborted).toBe(true)
    expect(screen.getByRole('status')).toHaveTextContent('longer than expected')
    expect(screen.getByRole('textbox')).toBeEnabled()
    await act(async () => { resolve(answer) })
    expect(screen.queryByText(answer.reply)).not.toBeInTheDocument()
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: 'Retry question' })) })
    expect(screen.getByText(answer.reply)).toBeVisible()
  })

  it('offers a saved explanation for a contextual follow-up without sending it as history', async () => {
    render(<TutorChatPanel context={home} />)
    await ask('What is HEAD?')
    vi.mocked(tutorApi.chat).mockRejectedValueOnce(new Error('network'))
    await ask('what do u mean?')
    expect(screen.getByText(/Saved explanation: What is HEAD/)).toBeVisible()
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: 'Retry question' })) })
    const history = vi.mocked(tutorApi.chat).mock.calls[2][0].history
    expect(history).toEqual([{ role: 'user', text: 'What is HEAD?' }, { role: 'assistant', text: answer.reply }])
  })

  it.each([
    [400, { message: ['Too long'] }, 'between 1 and 4,000'],
    [400, { history: ['Too long'] }, 'Start a new chat'],
    [413, {}, 'between 1 and 4,000'],
    [401, {}, 'sign in again'],
    [403, {}, 'available for this account'],
  ])('gives a specific correction for HTTP %s', async (status, payload, text) => {
    vi.mocked(tutorApi.chat).mockRejectedValueOnce(new ApiError('failure', status, payload))
    render(<TutorChatPanel context={home} />)
    await ask('Explain branches')
    expect(screen.getByRole('status')).toHaveTextContent(text)
    expect(screen.queryByRole('button', { name: 'Retry question' })).not.toBeInTheDocument()
    expect(screen.getByRole('status')).not.toHaveTextContent('Reopen')
  })

  it.each([null, { ...answer, reply: '' }])('recovers from a malformed backend response', async (value) => {
    vi.mocked(tutorApi.chat).mockResolvedValueOnce(value as TutorReply)
    render(<TutorChatPanel context={home} />)
    await ask('Explain branches')
    expect(screen.getByRole('status')).toHaveTextContent('couldn’t get an AI response')
    expect(screen.getByRole('textbox')).toHaveValue('Explain branches')
  })

  it.each([400, 403, 404])('keeps the draft when a guide returns HTTP %s', async (status) => {
    vi.mocked(tutorApi.chat).mockRejectedValueOnce(new ApiError('guide unavailable', status, status === 400 ? { context: ['expired'] } : {}))
    render(<TutorChatPanel context={{ surface: 'command_guide', run_id: 17, teaching_key: 'add', guide_token: 'signed' }} />)
    await ask('Explain this guide')
    expect(screen.getByRole('status')).toHaveTextContent('Reopen it from the workspace')
    expect(screen.getByRole('textbox')).toHaveValue('Explain this guide')
    expect(screen.queryByRole('button', { name: 'Retry question' })).not.toBeInTheDocument()
  })
})

describe('saved explanation relevance', () => {
  it.each([
    ['How is rebase different from merge?', 'rebase'],
    ['merge vs rebase', 'rebase'],
    ['What is a branch?', 'branches'],
    ['What is HEAD?', 'head'],
    ['How do staging and commits differ?', undefined],
    ['What is the difference between fetch and pull?', 'remotes'],
    ['Tell me a joke', undefined],
  ])('matches %s conservatively', (question, expected) => {
    expect(findOfflineFaq(question)?.id).toBe(expected)
  })
  it('uses learner history for clarification but not a clear topic change', () => {
    const history = [{ role: 'user', text: 'Explain staging' }, { role: 'assistant', text: 'The index...' }]
    expect(findOfflineFaq('what do u mean?', history)?.id).toBe('staging')
    expect(findOfflineFaq('Help with calculus', history)).toBeUndefined()
  })
  it.each([undefined, -1, 0, NaN, Infinity, '5'])('defaults invalid retry timing %s to 60 seconds', (value) => {
    expect(retrySeconds(value)).toBe(60)
  })
})
