import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { useAuthStore } from '@/shared/auth/useAuth'
import { setGuideMascotVisibility } from '@/shared/mascot/guideMascotVisibility'
import { GuideTutor } from './GuideTutor'
import { HomeTutor } from './HomeTutor'
import { tutorApi, type TutorReply } from './tutorApi'

vi.mock('./tutorApi', () => ({ tutorApi: { chat: vi.fn() } }))
const reply: TutorReply = { reply: 'A waiting area for the changes you want in your next commit.',
  suggested_topics: [], scenario_related: false, response_kind: 'answer' }

beforeEach(() => {
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
  it('opens Home help independently of guide and mascot appearance settings', async () => {
    setGuideMascotVisibility(false)
    render(<HomeTutor />)
    expect(screen.queryByRole('button', { name: 'Ask Git-It' })).not.toBeInTheDocument()
    expect(screen.getByRole('dialog').parentElement?.querySelector('.tutor-window__speaker')).toHaveAttribute('src', '/mascot/portrait.png')
    expect(screen.getByRole('dialog').querySelector('img')).not.toBeInTheDocument()
    ask('Explain staging')
    expect(await screen.findByText(reply.reply)).toBeInTheDocument()
    expect(screen.getByRole('article', { name: 'Git-It' })).toHaveTextContent(reply.reply)
    expect(screen.getByRole('dialog').querySelector('img')).not.toBeInTheDocument()
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
    const window = screen.getByRole('dialog', { name: 'Ask Git-It' })
    expect(window.querySelector('img')).not.toBeInTheDocument()
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
    expect(screen.queryByRole('dialog', { name: 'Ask Git-It' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Ask Git-It' }))
    expect(screen.getByRole('dialog', { name: 'Ask Git-It' })).toBeInTheDocument()
    view.unmount()
    // The next guide opens with the chat as the learner left it.
    render(<GuideTutor runId={17} teachingKey="command:status" usageForm="git status" guideToken="signed-guide" />)
    expect(screen.getByRole('dialog', { name: 'Ask Git-It' })).toBeInTheDocument()
  })

  it('keeps workspace help open while the learner works elsewhere; Escape or close puts only the chat away', () => {
    const guideEscape = vi.fn()
    window.addEventListener('keydown', guideEscape)
    renderGuideTutor()
    fireEvent.pointerDown(document.body)
    expect(screen.getByRole('dialog', { name: 'Ask Git-It' })).toBeInTheDocument()
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'Escape' })
    expect(screen.queryByRole('dialog', { name: 'Ask Git-It' })).not.toBeInTheDocument()
    expect(guideEscape).not.toHaveBeenCalled()
    const launcher = screen.getByRole('button', { name: 'Ask Git-It' })
    expect(launcher).toHaveFocus()
    fireEvent.click(launcher)
    fireEvent.click(screen.getByRole('button', { name: 'Close Ask Git-It' }))
    expect(screen.queryByRole('dialog', { name: 'Ask Git-It' })).not.toBeInTheDocument()
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
    fireEvent.click(screen.getByRole('button', { name: 'Close Ask Git-It' }))
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

  it.each([
    { name: 'header', selector: '.tutor-window__heading', x: 120, y: 30 },
    { name: 'body', selector: '.tutor-chat__transcript', x: 120, y: 200 },
    { name: 'side mascot', selector: '.tutor-window__speaker', x: -40, y: 40 },
  ])('moves from its $name and resizes from its edges', ({ selector, x, y }) => {
    render(<HomeTutor />)
    const frame = screen.getByRole('dialog').parentElement!
    const box = () => {
      const [left, top, width, height] = ['left', 'top', 'width', 'height'].map((side) => Number.parseFloat(frame.style.getPropertyValue(side)))
      return { left, top, width, height }
    }
    frame.getBoundingClientRect = () => {
      const { left, top, width, height } = box()
      return DOMRect.fromRect({ x: left, y: top, width, height })
    }
    const start = box()
    const handle = frame.querySelector(selector)!
    fireEvent.pointerDown(handle, { button: 0, pointerId: 1, clientX: start.left + x, clientY: start.top + y })
    fireEvent.pointerMove(frame, { pointerId: 1, clientX: start.left + x - 50, clientY: start.top + y + 20 })
    fireEvent.pointerUp(frame, { pointerId: 1 })
    expect(box()).toEqual({ ...start, left: start.left - 50, top: start.top + 20 })

    const moved = box()
    const rightEdge = moved.left + moved.width - 2
    fireEvent.pointerDown(frame, { button: 0, pointerId: 2, clientX: rightEdge, clientY: moved.top + 200 })
    fireEvent.pointerMove(frame, { pointerId: 2, clientX: rightEdge - 40, clientY: moved.top + 200 })
    fireEvent.pointerUp(frame, { pointerId: 2 })
    expect(box()).toEqual({ ...moved, width: moved.width - 40 })

    // Text selection, typing and the send button keep their native pointer behavior.
    for (const target of [
      screen.getByText('Ask what a command means, why it works, or which idea feels unclear.'),
      screen.getByRole('textbox'),
      screen.getByRole('button', { name: 'Send question' }),
    ]) {
      fireEvent.pointerDown(target, { button: 0, pointerId: 3, clientX: moved.left + 100, clientY: moved.top + 200 })
      fireEvent.pointerMove(frame, { pointerId: 3, clientX: moved.left + 10, clientY: moved.top + 300 })
      fireEvent.pointerUp(frame, { pointerId: 3 })
      expect(box()).toEqual({ ...moved, width: moved.width - 40 })
    }
  })

  it('moves and resizes with keyboard controls and stays within a resized viewport', () => {
    render(<HomeTutor />)
    const frame = screen.getByRole('dialog').parentElement!
    const startX = Number.parseFloat(frame.style.left)
    const startWidth = Number.parseFloat(frame.style.width)
    fireEvent.keyDown(screen.getByRole('button', { name: 'Move AI chat window' }), { key: 'ArrowLeft' })
    expect(Number.parseFloat(frame.style.left)).toBe(startX - 10)
    fireEvent.keyDown(screen.getByRole('button', { name: 'Resize AI chat window' }), { key: 'ArrowRight' })
    expect(Number.parseFloat(frame.style.width)).toBe(startWidth + 10)
    const width = window.innerWidth
    const height = window.innerHeight
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 390 })
    Object.defineProperty(window, 'innerHeight', { configurable: true, value: 844 })
    fireEvent(window, new Event('resize'))
    expect(Number.parseFloat(frame.style.left) + Number.parseFloat(frame.style.width)).toBeLessThanOrEqual(378)
    expect(Number.parseFloat(frame.style.top) + Number.parseFloat(frame.style.height)).toBeLessThanOrEqual(756)
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: width })
    Object.defineProperty(window, 'innerHeight', { configurable: true, value: height })
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
    expect(answer).not.toHaveTextContent('Scenario spotted')
    expect(answer.querySelector('strong')).toHaveTextContent('placeholders')
    expect(answer.querySelector('pre')).toHaveTextContent('git switch -c <branch>')
    expect(answer.querySelectorAll('li')).toHaveLength(2)
  })

  it('marks a Home reply that declined a scenario', async () => {
    vi.mocked(tutorApi.chat).mockResolvedValue({
      ...reply,
      reply: "Asking about GIT it! scenarios isn't allowed here, so I can't help with this one. Ask me another Git question instead.",
      scenario_related: true,
      response_kind: 'guarded',
    })
    render(<HomeTutor />)
    ask('Pasted scenario')
    const answer = await screen.findByRole('article', { name: 'Git-It' })
    expect(answer).toHaveTextContent('Scenario spotted')
    expect(answer).toHaveTextContent('Ask me another Git question instead.')
  })

  it('does not mark workspace replies, which are always protected', async () => {
    vi.mocked(tutorApi.chat).mockResolvedValue({ ...reply, scenario_related: true, response_kind: 'guarded' })
    renderGuideTutor()
    ask('Explain this')
    expect(await screen.findByRole('article', { name: 'Git-It' })).not.toHaveTextContent('Scenario spotted')
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
