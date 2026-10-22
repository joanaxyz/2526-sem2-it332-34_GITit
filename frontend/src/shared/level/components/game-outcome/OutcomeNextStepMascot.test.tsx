import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { FloatingMascotLauncher } from '@/shared/mascot/FloatingMascotLauncher'
import { OutcomeNextStepMascot } from './OutcomeNextStepMascot'

afterEach(cleanup)

describe('OutcomeNextStepMascot', () => {
  it('speaks the next step and moves on from the mascot or its bubble', () => {
    const select = vi.fn()
    render(<OutcomeNextStepMascot step={{
      caption: 'Continue',
      prompt: 'Click me to continue to the next scenario!',
      detail: 'Next: Publish and track',
      onSelect: select,
    }} />)

    const mascot = screen.getByRole('button', { name: 'Click me to continue to the next scenario! Next: Publish and track' })
    expect(mascot).toHaveFocus()
    fireEvent.click(mascot)
    fireEvent.click(screen.getByText('Click me to continue to the next scenario!'))
    expect(select).toHaveBeenCalledTimes(2)
  })

  it('holds still while the step is under way', () => {
    const select = vi.fn()
    render(<OutcomeNextStepMascot step={{
      caption: 'Continue',
      prompt: 'Click me to continue to the Medium trial!',
      pending: true,
      pendingPrompt: 'Opening the next trial…',
      onSelect: select,
    }} />)

    fireEvent.click(screen.getByRole('button', { name: 'Opening the next trial…' }))
    expect(select).not.toHaveBeenCalled()
  })

  it('takes over the spot where the workspace guide mascot last stood', () => {
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 1200 })
    Object.defineProperty(window, 'innerHeight', { configurable: true, value: 800 })
    const guide = render(<FloatingMascotLauncher name="command-guide" label="Open command guide" caption="Guide" onOpen={vi.fn()} />)
    const guideButton = screen.getByRole('button', { name: 'Open command guide' })
    fireEvent.pointerDown(guideButton, { button: 0, pointerId: 1, clientX: 900, clientY: 300 })
    fireEvent.pointerMove(guideButton, { pointerId: 1, clientX: 300, clientY: 500 })
    fireEvent.pointerUp(guideButton, { pointerId: 1, clientX: 300, clientY: 500 })
    const guideFrame = guideButton.parentElement!
    const guideLeft = parseFloat(guideFrame.style.left)
    const guideTop = parseFloat(guideFrame.style.top)
    guide.unmount()

    render(<OutcomeNextStepMascot step={{ caption: 'Continue', prompt: 'Click me to continue!', onSelect: vi.fn() }} />)
    const frame = screen.getByRole('button', { name: 'Click me to continue!' }).parentElement!

    // The larger Git-It is centred on the guide's spot, standing on the same line.
    expect(parseFloat(frame.style.left)).toBe(guideLeft + 76 / 2 - 128 / 2)
    expect(parseFloat(frame.style.top)).toBe(guideTop + 104 - 180)
    expect(frame).toHaveAttribute('data-size', 'large')
  })
})
