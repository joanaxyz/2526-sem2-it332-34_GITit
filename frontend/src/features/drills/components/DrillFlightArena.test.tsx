import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { useState } from 'react'
import { DrillFlightArena } from './DrillFlightArena'

vi.mock('@/shared/mascot/MascotSprite', () => ({
  MascotSprite: ({ pose }: { pose: string }) => <span data-testid="pose">{pose}</span>,
}))

const options = [{ value: 'git add', gloss: 'Stage' }, { value: 'git status', gloss: 'Inspect' }]
const collide = vi.fn()
let frames: Map<number, FrameRequestCallback>
let nextFrame: number
let frameTime: number
let reduced = false

function Harness() {
  const [started, setStarted] = useState(false)
  return <DrillFlightArena options={options} verdict={null} lives={3} started={started}
    onStart={() => setStarted(true)} onCollide={collide} voice="machine" />
}

function step(count: number) {
  act(() => {
    for (let i = 0; i < count; i++) {
      const pending = [...frames.values()]
      frames.clear()
      frameTime += 40
      pending.forEach((callback) => callback(frameTime))
    }
  })
}

function positionOf(node: HTMLElement) {
  const match = node.style.transform.match(/translate\(([-\d.]+)px,\s*([-\d.]+)px\)/)
  expect(match).not.toBeNull()
  return { x: Number(match![1]), y: Number(match![2]) }
}

describe('flight controls and collisions', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    collide.mockReset()
    reduced = false
    nextFrame = 0
    frameTime = 0
    frames = new Map()
    vi.stubGlobal('matchMedia', () => ({ matches: reduced, addEventListener: vi.fn(), removeEventListener: vi.fn() }))
    vi.stubGlobal('requestAnimationFrame', (callback: FrameRequestCallback) => {
      frames.set(++nextFrame, callback)
      return nextFrame
    })
    vi.stubGlobal('cancelAnimationFrame', (id: number) => frames.delete(id))
    vi.spyOn(HTMLElement.prototype, 'clientWidth', 'get').mockReturnValue(1000)
    vi.spyOn(HTMLElement.prototype, 'clientHeight', 'get').mockReturnValue(400)
    vi.spyOn(HTMLElement.prototype, 'offsetWidth', 'get').mockReturnValue(180)
    vi.spyOn(HTMLElement.prototype, 'offsetHeight', 'get').mockReturnValue(44)
  })
  afterEach(() => { cleanup(); vi.useRealTimers(); vi.restoreAllMocks(); vi.unstubAllGlobals() })

  it('waits in idle, takes off on a click, and submits only once when the mascot reaches an answer', () => {
    render(<Harness />)
    expect(screen.getByTestId('pose')).toHaveTextContent('idle')
    step(200)
    expect(collide).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Fly to answer 2: git status' }))
    expect(screen.getByTestId('pose')).toHaveTextContent('take-off')
    act(() => vi.advanceTimersByTime(1350))
    expect(screen.getByTestId('pose')).toHaveTextContent('fly')
    expect(collide).not.toHaveBeenCalled()
    step(200)
    expect(collide).toHaveBeenCalledExactlyOnceWith('git status')
    step(200)
    expect(collide).toHaveBeenCalledTimes(1)
  })

  it('freezes flight while paused and resumes the same round', () => {
    render(<Harness />)
    fireEvent.click(screen.getByRole('button', { name: 'Fly to answer 1: git add' }))
    act(() => vi.advanceTimersByTime(1350))
    fireEvent.click(screen.getByRole('button', { name: 'Pause flight' }))
    step(500)
    expect(collide).not.toHaveBeenCalled()
    fireEvent.click(screen.getAllByRole('button', { name: 'Resume flight' })[0])
    step(200)
    expect(collide).toHaveBeenCalledExactlyOnceWith('git add')
  })

  it('lets a steering tap reach the right edge while keeping the mascot on screen', () => {
    render(<Harness />)
    const arena = screen.getByRole('group', { name: /^Flight arena/ })
    fireEvent.pointerDown(arena, { clientX: 150, clientY: 90 })
    act(() => vi.advanceTimersByTime(1350))
    step(40)
    fireEvent.pointerDown(arena, { clientX: 1200, clientY: 90 })
    step(100)
    expect(document.querySelector('.drill-flight-actor')).toHaveStyle({ transform: 'translate(950px, 90px)' })
    expect(collide).not.toHaveBeenCalled()
  })

  it('follows mouse movement after takeoff without requiring another click', () => {
    render(<Harness />)
    const arena = screen.getByRole('group', { name: /^Flight arena/ })
    fireEvent.pointerMove(arena, { pointerType: 'mouse', clientX: 900, clientY: 90 })
    expect(screen.getByTestId('pose')).toHaveTextContent('idle')
    fireEvent.pointerDown(arena, { clientX: 150, clientY: 90 })
    act(() => vi.advanceTimersByTime(1350))
    step(40)
    fireEvent.pointerMove(arena, { pointerType: 'mouse', clientX: 900, clientY: 90 })
    step(100)
    expect(document.querySelector('.drill-flight-actor')).toHaveStyle({ transform: 'translate(900px, 90px)' })
    expect(collide).not.toHaveBeenCalled()
  })

  it('keeps the actor mounted and sends the next wave without another launch', () => {
    const view = render(<DrillFlightArena options={options} verdict={null} lives={2} started round={1}
      onStart={vi.fn()} onCollide={collide} voice="machine" />)
    const actor = document.querySelector('.drill-flight-actor')
    expect(screen.getByTestId('pose')).toHaveTextContent('fly')
    const nextOptions = [{ value: 'git init', gloss: 'Create' }, { value: 'git log', gloss: 'History' }]
    view.rerender(<DrillFlightArena options={nextOptions} verdict={null} lives={2} started round={2}
      onStart={vi.fn()} onCollide={collide} voice="machine" />)
    expect(document.querySelector('.drill-flight-actor')).toBe(actor)
    expect(screen.queryByRole('button', { name: 'Take off' })).not.toBeInTheDocument()
    const projectile = screen.getByRole('button', { name: 'Fly to answer 1: git init' })
    const before = projectile.style.transform
    step(20)
    expect(projectile.style.transform).not.toBe(before)
  })

  it.each([320, 360, 390, 640, 1000, 1180])('moves choices one quarter of a %ipx arena in seven seconds', (width) => {
    vi.spyOn(HTMLElement.prototype, 'clientWidth', 'get').mockReturnValue(width)
    render(<DrillFlightArena options={options} verdict={null} lives={3} started
      onStart={vi.fn()} onCollide={collide} voice="machine" />)
    const projectile = screen.getByRole('button', { name: 'Fly to answer 1: git add' })
    const x = () => Number(projectile.style.transform.match(/translate\(([\d.]+)px/)?.[1])
    const start = x()
    step(176)
    expect((start - x()) / width).toBeCloseTo(0.25)
    expect(collide).not.toHaveBeenCalled()
  })

  it('preserves choice position and crossing time when the arena resizes mid-flight', () => {
    let resize = () => {}
    vi.stubGlobal('ResizeObserver', class {
      constructor(callback: () => void) { resize = callback }
      observe() {}
      disconnect() {}
    })
    const width = vi.spyOn(HTMLElement.prototype, 'clientWidth', 'get').mockReturnValue(1000)
    render(<DrillFlightArena options={options} verdict={null} lives={3} started
      onStart={vi.fn()} onCollide={collide} voice="machine" />)
    const projectile = screen.getByRole('button', { name: 'Fly to answer 1: git add' })
    const x = () => Number(projectile.style.transform.match(/translate\(([\d.]+)px/)?.[1])
    step(176)
    const beforeResize = x() / 1000
    act(() => {
      width.mockReturnValue(360)
      resize()
    })
    expect(x() / 360).toBeCloseTo(beforeResize)
    const start = x()
    step(175)
    expect((start - x()) / 360).toBeCloseTo(0.25)
    expect(collide).not.toHaveBeenCalled()
  })

  it('ends a single-pass wave only after every answer exits, without submitting a collision', () => {
    const missed = vi.fn()
    vi.spyOn(HTMLElement.prototype, 'offsetWidth', 'get').mockImplementation(function (this: HTMLElement) {
      return this.getAttribute('aria-label')?.includes('git status') ? 360 : 180
    })
    render(<DrillFlightArena options={options} verdict={null} lives={3} started
      onStart={vi.fn()} onCollide={collide} onMiss={missed} voice="machine" />)
    const answer = screen.getByRole('button', { name: 'Fly to answer 1: git add' })
    const widerAnswer = screen.getByRole('button', { name: 'Fly to answer 2: git status' })
    step(630)
    expect(positionOf(answer).x + answer.offsetWidth / 2).toBeLessThan(0)
    expect(positionOf(widerAnswer).x + widerAnswer.offsetWidth / 2).toBeGreaterThan(0)
    expect(missed).not.toHaveBeenCalled()
    expect(collide).not.toHaveBeenCalled()
    step(100)
    expect(positionOf(widerAnswer).x + widerAnswer.offsetWidth / 2).toBeLessThan(0)
    expect(missed).toHaveBeenCalledTimes(1)
    const finalPosition = answer.style.transform
    step(500)
    expect(answer.style.transform).toBe(finalPosition)
    expect(missed).toHaveBeenCalledTimes(1)
    expect(collide).not.toHaveBeenCalled()
  })

  it('replaces a hit choice with its verdict and staggers a wrong hit', () => {
    render(<DrillFlightArena options={options} verdict={{ correct: false, picked: 'git status', pickedGloss: 'Inspect' }}
      lives={2} started onStart={vi.fn()} onCollide={collide} voice="machine" />)
    expect(screen.getByRole('button', { name: 'Wrong' })).toHaveTextContent('Wrong')
    expect(document.querySelector('.drill-flight-recoil')).toHaveAttribute('data-stagger')
    expect(screen.getByTestId('pose')).toHaveTextContent('float')
  })

  it('lets reduced-motion users choose directly without waiting for a moving target', () => {
    reduced = true
    render(<DrillFlightArena options={options} verdict={null} lives={2} started round={2}
      onStart={vi.fn()} onCollide={collide} voice="machine" />)
    const button = screen.getByRole('button', { name: 'Fly to answer 1: git add' })
    const x = Number(button.style.transform.match(/translate\(([\d.]+)px/)?.[1])
    expect(x + button.offsetWidth / 2).toBeLessThanOrEqual(1000)
    fireEvent.click(button)
    expect(collide).toHaveBeenCalledExactlyOnceWith('git add')
    step(200)
    expect(collide).toHaveBeenCalledTimes(1)
  })

  it('keeps answer lanes and steering below the measured in-arena question', () => {
    vi.spyOn(HTMLElement.prototype, 'offsetTop', 'get').mockImplementation(function (this: HTMLElement) {
      return this.classList.contains('drill-flight-question') ? 40 : 0
    })
    vi.spyOn(HTMLElement.prototype, 'offsetHeight', 'get').mockImplementation(function (this: HTMLElement) {
      return this.classList.contains('drill-flight-question') ? 120 : 44
    })
    render(<DrillFlightArena options={options} verdict={null} lives={3} started
      onStart={vi.fn()} onCollide={collide} voice="machine">
      <section aria-label="Question">Which command stages the selected files?</section>
    </DrillFlightArena>)
    const question = document.querySelector<HTMLElement>('.drill-flight-question')!
    const questionBottom = question.offsetTop + question.offsetHeight
    for (const answer of screen.getAllByRole('button', { name: /^Fly to answer/ })) {
      expect(positionOf(answer).y - answer.offsetHeight / 2).toBeGreaterThan(questionBottom)
    }
    fireEvent.pointerDown(screen.getByRole('group', { name: /^Flight arena/ }), { clientX: 50, clientY: 0 })
    step(40)
    const actor = document.querySelector<HTMLElement>('.drill-flight-actor')!
    expect(positionOf(actor).y).toBeGreaterThanOrEqual(questionBottom + 28)
    expect(collide).not.toHaveBeenCalled()
  })

  it('updates lanes and clamps steering when the question grows without restarting the wave', () => {
    let questionHeight = 80
    let resize = () => {}
    const observed = new Set<Element>()
    vi.stubGlobal('ResizeObserver', class {
      constructor(callback: () => void) { resize = callback }
      observe(element: Element) { observed.add(element) }
      disconnect() {}
    })
    vi.spyOn(HTMLElement.prototype, 'offsetTop', 'get').mockImplementation(function (this: HTMLElement) {
      return this.classList.contains('drill-flight-question') ? 40 : 0
    })
    vi.spyOn(HTMLElement.prototype, 'offsetHeight', 'get').mockImplementation(function (this: HTMLElement) {
      return this.classList.contains('drill-flight-question') ? questionHeight : 44
    })
    render(<DrillFlightArena options={options} verdict={null} lives={3} started
      onStart={vi.fn()} onCollide={collide} voice="machine"><p>Stage the selected files.</p></DrillFlightArena>)
    const question = document.querySelector<HTMLElement>('.drill-flight-question')!
    expect(observed.has(question)).toBe(true)
    fireEvent.pointerDown(screen.getByRole('group', { name: /^Flight arena/ }), { clientX: 50, clientY: 0 })
    step(176)
    const projectile = screen.getByRole('button', { name: 'Fly to answer 1: git add' })
    const before = positionOf(projectile)
    act(() => {
      questionHeight = 120
      resize()
    })
    const after = positionOf(projectile)
    expect(after.x).toBeCloseTo(before.x)
    expect(after.y).toBeGreaterThan(before.y)
    const questionBottom = question.offsetTop + question.offsetHeight
    expect(after.y - projectile.offsetHeight / 2).toBeGreaterThan(questionBottom)
    expect(positionOf(document.querySelector<HTMLElement>('.drill-flight-actor')!).y).toBeGreaterThanOrEqual(questionBottom + 28)
    step(175)
    expect(before.x - positionOf(projectile).x).toBeCloseTo(250)
    expect(collide).not.toHaveBeenCalled()
  })

  it('keeps long reduced-motion answers fully visible in a 320px arena', () => {
    reduced = true
    const missed = vi.fn()
    vi.spyOn(HTMLElement.prototype, 'clientWidth', 'get').mockReturnValue(320)
    vi.spyOn(HTMLElement.prototype, 'offsetWidth', 'get').mockReturnValue(260)
    const longOptions = [
      { value: 'Stage changes below the current folder', gloss: 'Folder' },
      { value: 'Stage selected paths for the next commit', gloss: 'Paths' },
      { value: 'Discard changes in the working directory', gloss: 'Restore' },
      { value: 'Unstage selected paths without losing edits', gloss: 'Unstage' },
    ]
    render(<DrillFlightArena options={longOptions} verdict={null} lives={3} started round={2}
      onStart={vi.fn()} onCollide={collide} onMiss={missed} voice="prose"><p>What does this command do?</p></DrillFlightArena>)
    const answers = screen.getAllByRole('button', { name: /^Fly to answer/ })
    const positions = answers.map((answer) => answer.style.transform)
    for (const answer of answers) {
      const { x } = positionOf(answer)
      expect(x - answer.offsetWidth / 2).toBeGreaterThanOrEqual(16)
      expect(x + answer.offsetWidth / 2).toBeLessThanOrEqual(320 - 16)
    }
    step(2000)
    expect(answers.map((answer) => answer.style.transform)).toEqual(positions)
    expect(collide).not.toHaveBeenCalled()
    expect(missed).not.toHaveBeenCalled()
  })
})
