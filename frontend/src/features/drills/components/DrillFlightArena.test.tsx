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

  it('keeps the actor mounted and sends the next wave without another launch', () => {
    const view = render(<DrillFlightArena options={options} verdict={null} lives={2} started round={1}
      onStart={vi.fn()} onCollide={collide} voice="machine" />)
    const actor = document.querySelector('.drill-flight-actor')
    expect(screen.getByTestId('pose')).toHaveTextContent('fly')
    const nextOptions = [{ value: 'git init', gloss: 'Create' }, { value: 'git log', gloss: 'History' }]
    view.rerender(<DrillFlightArena options={nextOptions} verdict={null} lives={2} started round={2}
      onStart={vi.fn()} onCollide={collide} voice="machine" />)
    expect(document.querySelector('.drill-flight-actor')).toBe(actor)
    expect(screen.queryByText('Take flight.')).not.toBeInTheDocument()
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
})
