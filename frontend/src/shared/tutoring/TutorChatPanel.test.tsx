import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { useAuthStore } from '@/shared/auth/useAuth'
import { setGuideMascotVisibility } from '@/shared/mascot/guideMascotVisibility'
import { GuideTutor } from './GuideTutor'
import { HomeTutor } from './HomeTutor'
import { tutorApi, type TutorReply } from './tutorApi'

vi.mock('./tutorApi', () => ({ tutorApi: { chat: vi.fn() } }))
const reply: TutorReply = { reply: 'A waiting area for the changes you want in your next commit.',
  sources: [{ id: 'concept:staging-area', title: 'Staging area' }], suggested_topics: [],
  scenario_related: false, response_kind: 'explanation' }

beforeEach(() => {
  localStorage.clear()
  useAuthStore.getState().setSession('test', { id: 1, username: 'learner', email: 'learner@example.com', is_staff: false })
  vi.mocked(tutorApi.chat).mockReset().mockResolvedValue(reply)
})
afterEach(() => { cleanup(); useAuthStore.getState().clearSession(); setGuideMascotVisibility(true) })

function ask(text: string) {
  fireEvent.change(screen.getByRole('textbox', { name: 'Ask Git-It a question' }), { target: { value: text } })
  fireEvent.click(screen.getByRole('button', { name: 'Send question' }))
}

describe('shared tutoring surfaces', () => {
  it('opens Home help independently of guide and mascot appearance settings', async () => {
    setGuideMascotVisibility(false)
    render(<HomeTutor />)
    expect(screen.queryByRole('button', { name: 'Ask Git-It' })).not.toBeInTheDocument()
    expect(screen.getByRole('dialog').querySelector('img')).toHaveAttribute('src', '/mascot/portrait.png')
    ask('Explain staging')
    expect(await screen.findByText(reply.reply)).toBeInTheDocument()
    expect(screen.getByText(reply.reply).closest('.tutor-chat__bubble')).toBeInTheDocument()
    expect(screen.getByText(reply.reply).closest('.tutor-chat__message')?.querySelector('img')).toHaveAttribute('src', '/mascot/portrait.png')
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
    const window = screen.getByRole('dialog', { name: 'Ask Git-It' })
    expect(window.querySelector('img')).toHaveAttribute('src', '/mascot/portrait.png')
    expect(screen.getByRole('region', { name: 'Guide container' })).not.toContainElement(window)
    expect(screen.getByRole('textbox')).toHaveFocus()
    ask('Explain this placeholder')
    await waitFor(() => expect(tutorApi.chat).toHaveBeenCalled())
    expect(vi.mocked(tutorApi.chat).mock.calls[0][0].context).toEqual({ surface: 'command_guide', run_id: 17, teaching_key: 'form:git add <path>', usage_form: 'git add <path>', guide_token: 'signed-guide' })
    view.unmount()
    expect(signal?.aborted).toBe(true)
  })

  it('leaves closing to its command guide: no launcher of its own, and Escape reaches the guide', () => {
    const guideEscape = vi.fn()
    window.addEventListener('keydown', guideEscape)
    render(<GuideTutor runId={17} teachingKey="command:add" usageForm="git add <path>" guideToken="signed-guide" />)
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'Escape' })
    fireEvent.pointerDown(document.body)
    expect(guideEscape).toHaveBeenCalledOnce()
    expect(screen.getByRole('dialog', { name: 'Ask Git-It' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Ask Git-It' })).not.toBeInTheDocument()
    window.removeEventListener('keydown', guideEscape)
  })

  it('collapses Home help into its launcher on a click outside, leaving focus alone', () => {
    render(<><button type="button">Elsewhere</button><HomeTutor /></>)
    expect(screen.queryByRole('button', { name: /close/i })).not.toBeInTheDocument()
    fireEvent.pointerDown(screen.getByRole('dialog'))
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    const elsewhere = screen.getByRole('button', { name: 'Elsewhere' })
    elsewhere.focus()
    fireEvent.pointerDown(elsewhere)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Ask Git-It' })).toBeInTheDocument()
    expect(elsewhere).toHaveFocus()
  })

  it('moves when its header is dragged and resizes from its edges', () => {
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
    const header = screen.getByRole('heading', { name: 'Ask Git-It' })
    fireEvent.pointerDown(header, { button: 0, pointerId: 1, clientX: start.left + 120, clientY: start.top + 30 })
    fireEvent.pointerMove(frame, { pointerId: 1, clientX: start.left + 70, clientY: start.top + 50 })
    fireEvent.pointerUp(frame, { pointerId: 1 })
    expect(box()).toEqual({ ...start, left: start.left - 50, top: start.top + 20 })

    const moved = box()
    const rightEdge = moved.left + moved.width - 2
    fireEvent.pointerDown(frame, { button: 0, pointerId: 2, clientX: rightEdge, clientY: moved.top + 200 })
    fireEvent.pointerMove(frame, { pointerId: 2, clientX: rightEdge - 40, clientY: moved.top + 200 })
    fireEvent.pointerUp(frame, { pointerId: 2 })
    expect(box()).toEqual({ ...moved, width: moved.width - 40 })

    // A press inside the conversation selects text instead of moving the window.
    fireEvent.pointerDown(screen.getByRole('log'), { button: 0, pointerId: 3, clientX: moved.left + 100, clientY: moved.top + 200 })
    fireEvent.pointerMove(frame, { pointerId: 3, clientX: moved.left + 10, clientY: moved.top + 300 })
    expect(box()).toEqual({ ...moved, width: moved.width - 40 })
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
