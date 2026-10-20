import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { WorldMascot } from './WorldMascot'

vi.mock('./MascotSprite', () => ({ MascotSprite: () => null }))
vi.mock('@/shared/sprites/preload', () => ({ warmImages: vi.fn().mockResolvedValue(undefined) }))

let reduced = true
let now = 0
let nextFrame: FrameRequestCallback
let boxes: Record<string, DOMRect>

beforeEach(() => {
  reduced = true
  now = 0
  boxes = {
    left: new DOMRect(30, 200, 300, 250),
    right: new DOMRect(720, 300, 280, 250),
    node: new DOMRect(480, 400, 56, 56),
    rail: new DOMRect(20, 150, 320, 500),
  }
  vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockImplementation(function (this: HTMLElement) {
    if (this.classList.contains('world-mascot')) return new DOMRect(0, 0, 1024, 768)
    return boxes[this.dataset.box ?? ''] ?? new DOMRect()
  })
  vi.spyOn(performance, 'now').mockImplementation(() => now)
  vi.stubGlobal('matchMedia', () => ({ matches: reduced, addEventListener: vi.fn(), removeEventListener: vi.fn() }))
  vi.stubGlobal('requestAnimationFrame', (callback: FrameRequestCallback) => { nextFrame = callback; return 1 })
  vi.stubGlobal('cancelAnimationFrame', vi.fn())
})
afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllGlobals() })

function advance(milliseconds: number) {
  act(() => { for (let elapsed = 0; elapsed < milliseconds; elapsed += 40) { now += 40; nextFrame(now) } })
}
function setup() {
  const onSelectNode = vi.fn()
  const view = render(<main>
    <WorldMascot surface="track" />
    <aside data-box="rail" style={{ overflowY: 'auto' }}><section data-box="left" aria-label="Left panel" /></aside>
    <section><button data-mascot-perch onClick={onSelectNode} aria-label="Level one">
      <span data-box="node" data-mascot-platform>1</span>
    </button></section>
    <aside><section data-box="right" aria-label="Right panel" /></aside>
  </main>)
  return { ...view, actor: screen.getByRole('button', { name: 'Learning guide: share a Git tip' }), onSelectNode }
}

describe('page-wide mascot landings', () => {
  it('escapes the page stacking context and lands on both sibling rails', () => {
    const { container, actor } = setup()
    expect(container.querySelector('.world-mascot')).toBeNull()
    expect(actor.parentElement?.parentElement).toBe(document.body)
    fireEvent.pointerUp(screen.getByRole('region', { name: 'Left panel' }), { button: 0, clientX: 140, clientY: 210 })
    expect(actor).toHaveAttribute('data-pose', 'idle')
    expect(actor.style.transform).toContain('translate(140px, 200px)')
    fireEvent.pointerUp(screen.getByRole('region', { name: 'Right panel' }), { button: 0, clientX: 850, clientY: 310 })
    expect(actor).toHaveAttribute('data-pose', 'idle')
    expect(actor.style.transform).toContain('translate(850px, 300px)')
  })

  it('centers above a small node for pointer and keyboard activation, then follows layout changes', () => {
    const { actor, onSelectNode } = setup()
    fireEvent.pointerUp(screen.getByText('1'), { button: 0, clientX: 490, clientY: 450 })
    expect(actor.style.transform).toContain('translate(508px, 400px)')
    fireEvent.click(screen.getByRole('button', { name: 'Level one' }), { detail: 0 })
    expect(actor).toHaveAttribute('data-pose', 'idle')
    expect(actor.style.transform).toContain('translate(508px, 400px)')
    expect(onSelectNode).toHaveBeenCalledOnce()
    boxes.node = new DOMRect(580, 250, 56, 56)
    advance(40)
    expect(actor.style.transform).toContain('translate(608px, 250px)')
  })

  it('walks and runs along ledges, then takes off and lands on a different rail', () => {
    reduced = false
    const { actor } = setup()
    const left = screen.getByRole('region', { name: 'Left panel' })
    fireEvent.pointerUp(left, { button: 0, clientX: 55, clientY: 205 })
    advance(5000)
    expect(actor).toHaveAttribute('data-pose', 'idle')
    fireEvent.pointerUp(left, { button: 0, clientX: 105, clientY: 205 })
    expect(actor).toHaveAttribute('data-pose', 'walk')
    advance(1000)
    fireEvent.pointerUp(left, { button: 0, clientX: 310, clientY: 205 })
    expect(actor).toHaveAttribute('data-pose', 'run')
    advance(1500)
    expect(actor.style.transform).toContain('translate(310px, 200px)')
    fireEvent.pointerUp(screen.getByRole('region', { name: 'Right panel' }), { button: 0, clientX: 850, clientY: 310 })
    expect(actor).toHaveAttribute('data-pose', 'take-off')
    advance(6000)
    expect(actor).toHaveAttribute('data-pose', 'idle')
    expect(actor.style.transform).toContain('translate(850px, 300px)')
  })

  it('detaches from a clipped ledge and ignores clicks outside its page', () => {
    const { actor } = setup()
    const left = screen.getByRole('region', { name: 'Left panel' })
    fireEvent.pointerUp(left, { button: 0, clientX: 140, clientY: 210 })
    boxes.left = new DOMRect(30, 100, 300, 250)
    fireEvent.scroll(left.parentElement!)
    advance(40)
    expect(actor).toHaveAttribute('data-pose', 'float')
    const position = actor.style.transform
    fireEvent.pointerUp(document.body, { button: 0, clientX: 800, clientY: 600 })
    expect(actor.style.transform).toBe(position)
  })
})
