import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { useAuthStore } from '@/shared/auth/useAuth'
import { ApiError } from '@/shared/api/apiError'
import { setGuideMascotVisibility } from '@/shared/mascot/guideMascotVisibility'
import { GuideTutor } from './GuideTutor'
import { HomeTutor } from './HomeTutor'
import { tutorApi, type TutorReply } from './tutorApi'

vi.mock('./tutorApi', () => ({ tutorApi: { chat: vi.fn() } }))
const reply: TutorReply = { reply: 'A waiting area for the changes you want in your next commit.',
  suggested_topics: [], scenario_related: false, response_kind: 'answer' }

beforeEach(() => {
  Object.defineProperty(navigator, 'onLine', { configurable: true, value: true })
  localStorage.clear()
  useAuthStore.getState().setSession('test', { id: 1, username: 'learner', email: 'learner@example.com', is_staff: false })
  vi.mocked(tutorApi.chat).mockReset().mockResolvedValue(reply)
})
afterEach(() => { cleanup(); useAuthStore.getState().clearSession(); setGuideMascotVisibility(true) })

function renderGuideTutor() {
  const view = render(<GuideTutor runId={17} teachingKey="command:add" usageForm="git add <path>" guideToken="signed-guide" />)
  fireEvent.click(screen.getByRole('button', { name: 'Ask Git-It' }))
  return view
}

function ask(text: string) {
  fireEvent.change(screen.getByRole('textbox', { name: 'Ask Git-It a question' }), { target: { value: text } })
  fireEvent.click(screen.getByRole('button', { name: 'Send question' }))
}

describe('shared tutoring surfaces', () => {
  it('browses saved explanations manually without calling AI', () => {
    render(<HomeTutor />)
    fireEvent.click(screen.getByRole('button', { name: 'FAQS' }))
    expect(screen.getByRole('region', { name: 'Saved Git explanations' })).toBeVisible()
    expect(screen.getByText('What is a branch?')).toBeVisible()
    expect(tutorApi.chat).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    expect(screen.getByRole('textbox')).toHaveFocus()
  })

  it('stays in Chat offline and offers FAQs without submitting', () => {
    Object.defineProperty(navigator, 'onLine', { configurable: true, value: false })
    render(<HomeTutor />)
    expect(screen.getByRole('region', { name: 'Chat recovery' })).toBeVisible()
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Explain staging' } })
    expect(screen.getByRole('button', { name: 'Send question' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Browse FAQS' }))
    expect(screen.getByRole('region', { name: 'Saved Git explanations' })).toBeVisible()
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    Object.defineProperty(navigator, 'onLine', { configurable: true, value: true })
    fireEvent(window, new Event('online'))
    expect(screen.getByRole('textbox')).toHaveValue('Explain staging')
    expect(screen.getByRole('button', { name: 'Send question' })).toBeEnabled()
    expect(tutorApi.chat).not.toHaveBeenCalled()
  })

  it.each([
    ['network failure', new Error('network')],
    ['server failure', new ApiError('unavailable', 503, {})],
    ['provider unavailable', null],
  ])('retains the draft and excludes %s from retry history', async (_label, failure) => {
    if (failure) vi.mocked(tutorApi.chat).mockRejectedValueOnce(failure)
    else vi.mocked(tutorApi.chat).mockResolvedValueOnce({ ...reply, response_kind: 'unavailable', reply: 'AI is unavailable.' })
    render(<HomeTutor />)
    ask('Explain staging')
    expect(await screen.findByRole('region', { name: 'Chat recovery' })).toBeVisible()
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    expect(screen.getByRole('textbox')).toHaveValue('Explain staging')
    expect(screen.queryByRole('article')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Send question' }))
    await screen.findByText(reply.reply)
    expect(vi.mocked(tutorApi.chat).mock.calls[1][0].history).toEqual([])
    expect(screen.getByRole('textbox')).toHaveValue('')
    expect(screen.getByRole('textbox')).toHaveFocus()
    expect(screen.queryByText(/AI help is unavailable. Your question is saved/)).not.toBeInTheDocument()
  })

  it('keeps a failed draft when closing and reopening the window', async () => {
    vi.mocked(tutorApi.chat).mockRejectedValueOnce(new Error('network'))
    render(<HomeTutor />)
    ask('Explain branches')
    await screen.findByRole('region', { name: 'Chat recovery' })
    fireEvent.click(screen.getByRole('button', { name: 'Close Ask Blue' }))
    fireEvent.click(screen.getByRole('button', { name: 'Ask Git-It' }))
    expect(screen.getByRole('textbox')).toHaveValue('Explain branches')
  })

  it('keeps Chat and the draft when the connection drops and returns', () => {
    render(<HomeTutor />)
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Explain staging' } })
    Object.defineProperty(navigator, 'onLine', { configurable: true, value: false })
    fireEvent(window, new Event('offline'))
    expect(screen.getByRole('region', { name: 'Chat recovery' })).toBeVisible()
    expect(screen.getByRole('textbox')).toHaveFocus()
    Object.defineProperty(navigator, 'onLine', { configurable: true, value: true })
    fireEvent(window, new Event('online'))
    expect(screen.getByRole('textbox')).toHaveValue('Explain staging')
    expect(tutorApi.chat).not.toHaveBeenCalled()
  })

  it('does not retain an unanswered exchange after closing an in-flight chat', async () => {
    let resolve!: (value: TutorReply) => void
    vi.mocked(tutorApi.chat).mockImplementationOnce(() => new Promise((done) => { resolve = done }))
    render(<HomeTutor />)
    ask('Explain branches')
    fireEvent.click(screen.getByRole('button', { name: 'Close Ask Blue' }))
    fireEvent.click(screen.getByRole('button', { name: 'Ask Git-It' }))
    await act(async () => { resolve(reply) })
    expect(screen.getByRole('textbox')).toHaveValue('Explain branches')
    expect(screen.queryByRole('article')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Send question' }))
    await screen.findByText(reply.reply)
    expect(vi.mocked(tutorApi.chat).mock.calls[1][0].history).toEqual([])
  })

  it('clears saved drafts across sign-in lifetimes', () => {
    render(<HomeTutor />)
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Private unsent question' } })
    act(() => useAuthStore.getState().clearSession())
    act(() => useAuthStore.getState().setSession('second', { id: 2, username: 'other', email: 'other@example.com', is_staff: false }))
    expect(screen.getByRole('textbox')).toHaveValue('')
  })

  it('keeps validation errors in Chat with the original question', async () => {
    vi.mocked(tutorApi.chat).mockRejectedValueOnce(new ApiError('invalid guide', 400, { context: ['invalid guide'] }))
    renderGuideTutor()
    ask('Explain this guide')
    expect(await screen.findByRole('region', { name: 'Chat recovery' })).toHaveTextContent('Reopen it')
    expect(screen.getByRole('textbox')).toHaveValue('Explain this guide')
    expect(screen.queryByRole('region', { name: 'Saved Git explanations' })).not.toBeInTheDocument()
  })

  it('prevents duplicate sends and ignores a response after New chat', async () => {
    let resolve!: (value: TutorReply) => void
    vi.mocked(tutorApi.chat).mockImplementationOnce(() => new Promise((done) => { resolve = done }))
    render(<HomeTutor />)
    ask('Explain staging')
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'Enter' })
    expect(tutorApi.chat).toHaveBeenCalledTimes(1)
    fireEvent.click(screen.getByRole('button', { name: 'Start a new conversation' }))
    await act(async () => { resolve(reply) })
    expect(screen.queryByText(reply.reply)).not.toBeInTheDocument()
    expect(screen.getByRole('textbox')).toHaveValue('')
    ask('Explain branches')
    await screen.findByText(reply.reply)
    expect(vi.mocked(tutorApi.chat).mock.calls[1][0].history).toEqual([])
  })

  it('keeps the reading position until the learner requests the new message', async () => {
    let resolve!: (value: TutorReply) => void
    vi.mocked(tutorApi.chat).mockImplementationOnce(() => new Promise((done) => { resolve = done }))
    render(<HomeTutor />)
    ask('Explain staging')
    const log = screen.getByRole('log')
    Object.defineProperties(log, {
      scrollHeight: { configurable: true, value: 900 },
      clientHeight: { configurable: true, value: 200 },
    })
    log.scrollTop = 100
    fireEvent.scroll(log)
    await act(async () => { resolve(reply) })
    expect(log.scrollTop).toBe(100)
    fireEvent.click(screen.getByRole('button', { name: 'New message' }))
    expect(log.scrollTop).toBe(900)
    expect(screen.queryByRole('button', { name: 'New message' })).not.toBeInTheDocument()
  })

  it('follows replies when already near the bottom', async () => {
    let resolve!: (value: TutorReply) => void
    vi.mocked(tutorApi.chat).mockImplementationOnce(() => new Promise((done) => { resolve = done }))
    render(<HomeTutor />)
    ask('Explain staging')
    const log = screen.getByRole('log')
    Object.defineProperties(log, {
      scrollHeight: { configurable: true, value: 900 },
      clientHeight: { configurable: true, value: 200 },
    })
    log.scrollTop = 680
    fireEvent.scroll(log)
    await act(async () => { resolve(reply) })
    expect(log.scrollTop).toBe(900)
    expect(screen.queryByRole('button', { name: 'New message' })).not.toBeInTheDocument()
  })

  it('cancels old guide requests when the guide changes', async () => {
    let resolve!: (value: TutorReply) => void
    vi.mocked(tutorApi.chat).mockImplementationOnce(() => new Promise((done) => { resolve = done }))
    const view = renderGuideTutor()
    ask('Old guide question')
    const signal = vi.mocked(tutorApi.chat).mock.calls[0][1]
    view.rerender(<GuideTutor runId={17} teachingKey="command:status" usageForm="git status" guideToken="new-guide" />)
    expect(signal.aborted).toBe(true)
    await act(async () => { resolve(reply) })
    expect(screen.queryByText(reply.reply)).not.toBeInTheDocument()
    expect(screen.getByRole('textbox')).toHaveValue('')
  })

  it('opens Home help independently of guide and mascot appearance settings', async () => {
    setGuideMascotVisibility(false)
    render(<HomeTutor />)
    expect(screen.queryByRole('button', { name: 'Ask Git-It' })).not.toBeInTheDocument()
    expect(screen.getByRole('dialog').parentElement?.querySelector('.tutor-window__portrait img')).toHaveAttribute('src', '/mascot/portrait.png')
    expect(screen.getByRole('dialog').querySelector('.tutor-window__portrait img')).toBeInTheDocument()
    ask('Explain staging')
    expect(await screen.findByText(reply.reply)).toBeInTheDocument()
    expect(screen.getByRole('article', { name: 'Git-It' })).toHaveTextContent(reply.reply)
    expect(screen.getByRole('dialog').querySelector('.tutor-window__portrait img')).toBeInTheDocument()
    expect(tutorApi.chat).toHaveBeenCalledWith({ message: 'Explain staging', context: { surface: 'home' }, history: [] }, expect.any(AbortSignal))
    fireEvent.keyDown(document, { key: 'Escape' })
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    const trigger = screen.getByRole('button', { name: 'Ask Git-It' })
    expect(trigger).toHaveTextContent('Ask Git-It')
    expect(trigger.querySelector('img')).toHaveAttribute('src', '/mascot/portrait.png')
    expect(trigger).toHaveFocus()
    fireEvent.click(trigger)
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Ask Git-It' })).not.toBeInTheDocument()
  })

  it('opens workspace help in a separate chat window and cancels when its guide closes', async () => {
    let signal: AbortSignal | undefined
    vi.mocked(tutorApi.chat).mockImplementation((_body, nextSignal) => {
      signal = nextSignal
      return new Promise(() => {})
    })
    const view = render(<section aria-label="Guide container"><GuideTutor runId={17} teachingKey="form:git add <path>" usageForm="git add <path>" guideToken="signed-guide" /></section>)
    fireEvent.click(screen.getByRole('button', { name: 'Ask Git-It' }))
    const window = screen.getByRole('dialog', { name: 'Ask Blue' })
    expect(window.querySelector('.tutor-window__portrait img')).toBeInTheDocument()
    expect(screen.getByRole('region', { name: 'Guide container' })).not.toContainElement(window)
    expect(screen.getByRole('textbox')).toHaveFocus()
    ask('Explain this placeholder')
    await waitFor(() => expect(tutorApi.chat).toHaveBeenCalled())
    expect(vi.mocked(tutorApi.chat).mock.calls[0][0].context).toEqual({ surface: 'command_guide', run_id: 17, teaching_key: 'form:git add <path>', usage_form: 'git add <path>', guide_token: 'signed-guide' })
    view.unmount()
    expect(signal?.aborted).toBe(true)
  })

  it('starts workspace help as a launcher so it never covers the guide, and remembers it open', () => {
    const view = render(<GuideTutor runId={17} teachingKey="command:add" usageForm="git add <path>" guideToken="signed-guide" />)
    expect(screen.queryByRole('dialog', { name: 'Ask Blue' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Ask Git-It' }))
    expect(screen.getByRole('dialog', { name: 'Ask Blue' })).toBeInTheDocument()
    view.unmount()
    // The next guide opens with the chat as the learner left it.
    render(<GuideTutor runId={17} teachingKey="command:status" usageForm="git status" guideToken="signed-guide" />)
    expect(screen.getByRole('dialog', { name: 'Ask Blue' })).toBeInTheDocument()
  })

  it('keeps workspace help open while the learner works elsewhere; Escape or close puts only the chat away', () => {
    const guideEscape = vi.fn()
    window.addEventListener('keydown', guideEscape)
    renderGuideTutor()
    fireEvent.pointerDown(document.body)
    expect(screen.getByRole('dialog', { name: 'Ask Blue' })).toBeInTheDocument()
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'Escape' })
    expect(screen.queryByRole('dialog', { name: 'Ask Blue' })).not.toBeInTheDocument()
    expect(guideEscape).not.toHaveBeenCalled()
    const launcher = screen.getByRole('button', { name: 'Ask Git-It' })
    expect(launcher).toHaveFocus()
    fireEvent.click(launcher)
    fireEvent.click(screen.getByRole('button', { name: 'Close Ask Blue' }))
    expect(screen.queryByRole('dialog', { name: 'Ask Blue' })).not.toBeInTheDocument()
    window.removeEventListener('keydown', guideEscape)
  })

  it('collapses Home help into its launcher on a click outside, leaving focus alone', () => {
    render(<><button type="button">Elsewhere</button><HomeTutor /></>)
    fireEvent.pointerDown(screen.getByRole('dialog'))
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    const elsewhere = screen.getByRole('button', { name: 'Elsewhere' })
    elsewhere.focus()
    fireEvent.pointerDown(elsewhere)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Ask Git-It' })).toBeInTheDocument()
    expect(elsewhere).toHaveFocus()
  })

  it('closes Home help from a visible close button and stays closed on the next page', () => {
    const view = render(<HomeTutor />)
    fireEvent.click(screen.getByRole('button', { name: 'Close Ask Blue' }))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Ask Git-It' })).toHaveFocus()
    view.unmount()
    render(<HomeTutor />)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Ask Git-It' })).toBeInTheDocument()
  })

  it('starts Home help as its launcher on a phone', () => {
    const width = window.innerWidth
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 390 })
    render(<HomeTutor />)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Ask Git-It' })).toBeInTheDocument()
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: width })
  })

  it('keeps the panel fixed during pointer gestures and exposes no movement controls', () => {
    render(<HomeTutor />)
    expect(screen.queryByRole('button', { name: 'Move AI chat window' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Resize AI chat window' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Close Ask Blue' }))
    const launcher = screen.getByRole('button', { name: 'Ask Git-It' })
    expect(launcher).toHaveAttribute('title', 'Ask Git-It')
    expect(launcher.parentElement).toHaveAttribute('data-fixed')
    fireEvent.click(launcher)
    const frame = screen.getByRole('dialog').parentElement!
    const before = frame.getAttribute('style')
    fireEvent.pointerDown(frame.querySelector('.tutor-window__header')!, { button: 0, pointerId: 1, clientX: 500, clientY: 200 })
    fireEvent.pointerMove(frame, { pointerId: 1, clientX: 100, clientY: 400 })
    fireEvent.pointerUp(frame, { pointerId: 1 })
    expect(frame.getAttribute('style')).toBe(before)
    expect(screen.getByText(/Concept guidance only/)).toBeVisible()
  })

  it('sends a suggested question using the current tutor history', async () => {
    render(<HomeTutor />)
    fireEvent.click(screen.getByRole('button', { name: 'How does staging work?' }))
    await screen.findByText(reply.reply)
    expect(tutorApi.chat).toHaveBeenCalledWith(expect.objectContaining({ message: 'How does staging work?', history: [] }), expect.anything())
  })

  it('retains a suggested question for retry when the provider fails', async () => {
    vi.mocked(tutorApi.chat).mockRejectedValueOnce(new Error('network'))
    render(<HomeTutor />)
    fireEvent.click(screen.getByRole('button', { name: 'How does staging work?' }))
    await screen.findByRole('region', { name: 'Chat recovery' })
    expect(screen.getByRole('textbox')).toHaveValue('How does staging work?')
    fireEvent.click(screen.getByRole('button', { name: 'Retry question' }))
    await screen.findByText(reply.reply)
    expect(vi.mocked(tutorApi.chat).mock.calls[1][0].history).toEqual([])
  })

  it('sends both sides of the conversation so follow-ups can refer to the last answer', async () => {
    render(<HomeTutor />)
    ask('Explain staging')
    await screen.findByText(reply.reply)
    ask('What do you mean by waiting area?')
    await waitFor(() => expect(tutorApi.chat).toHaveBeenCalledTimes(2))
    expect(vi.mocked(tutorApi.chat).mock.calls[1][0].history).toEqual([
      { role: 'user', text: 'Explain staging' },
      { role: 'assistant', text: reply.reply },
    ])
  })

  it('renders light Markdown', async () => {
    vi.mocked(tutorApi.chat).mockResolvedValue({
      ...reply,
      reply: 'Use **placeholders**:\n\n```\ngit switch -c <branch>\n```\n\n- one\n- two',
      response_kind: 'guarded',
    })
    render(<HomeTutor />)
    ask('Explain switching')
    const answer = await screen.findByRole('article', { name: 'Git-It' })
    expect(answer).not.toHaveTextContent('Scenario guidance')
    expect(answer.querySelector('strong')).toHaveTextContent('placeholders')
    expect(answer.querySelector('pre')).toHaveTextContent('git switch -c <branch>')
    expect(answer.querySelectorAll('li')).toHaveLength(2)
  })

  it('marks a Home reply that declined a scenario', async () => {
    vi.mocked(tutorApi.chat).mockResolvedValue({
      ...reply,
      reply: "I can help you understand Git, but I can’t solve a scenario here. Ask about the concept, or open the command guide for help understanding its syntax.",
      scenario_related: true,
      response_kind: 'guarded',
    })
    render(<HomeTutor />)
    ask('Pasted scenario')
    const answer = await screen.findByRole('article', { name: 'Git-It' })
    expect(answer).toHaveTextContent('Scenario guidance')
    expect(answer).toHaveTextContent('Ask about the concept')
  })

  it('does not mark workspace replies, which are always protected', async () => {
    vi.mocked(tutorApi.chat).mockResolvedValue({ ...reply, scenario_related: true, response_kind: 'guarded' })
    renderGuideTutor()
    ask('Explain this')
    expect(await screen.findByRole('article', { name: 'Git-It' })).not.toHaveTextContent('Scenario guidance')
  })

  it('discards delayed responses and clears conversation across account changes', async () => {
    let resolve!: (value: TutorReply) => void
    let signal: AbortSignal | undefined
    vi.mocked(tutorApi.chat).mockImplementation((_body, nextSignal) => {
      signal = nextSignal
      return new Promise((done) => { resolve = done })
    })
    render(<HomeTutor />)
    ask('Private account question')
    act(() => useAuthStore.getState().setSession('second', { id: 2, username: 'other', email: 'other@example.com', is_staff: false }))
    expect(signal?.aborted).toBe(true)
    await act(async () => { resolve(reply) })
    expect(screen.queryByText('Private account question')).not.toBeInTheDocument()
    expect(screen.queryByText(reply.reply)).not.toBeInTheDocument()
  })
})
