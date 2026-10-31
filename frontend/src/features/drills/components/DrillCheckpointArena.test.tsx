import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { DrillCheckpointArena } from './DrillCheckpointArena'
import type { DrillAnswer } from '@/features/drills/types'

vi.mock('@/shared/mascot/MascotSprite', () => ({
  MascotSprite: ({ pose }: { pose: string }) => <span data-testid="pose">{pose}</span>,
}))

const expected = ['git', 'init', '-b', 'main']
let onResolve = vi.fn<(answer: DrillAnswer | null, fell: boolean) => void>()
let onAnswer = vi.fn<(answer: DrillAnswer | null) => void>()

function mount(variant: 'tokens' | 'steps' = 'tokens', blocks = expected) {
  return render(<DrillCheckpointArena values={blocks} expected={blocks} variant={variant}
    onAnswer={onAnswer} onResolve={onResolve} verdict={null} />)
}
function place(values: string[]) {
  for (const name of values) fireEvent.click(screen.getByRole('button', { name }))
}
function type(value: string, target: Window | Document | Node = window) {
  for (const key of value) fireEvent.keyDown(target, { key })
}
async function advance(ms: number) {
  await act(async () => { await vi.advanceTimersByTimeAsync(ms) })
}

describe('walking checkpoint', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.stubGlobal('matchMedia', () => ({ matches: false, addEventListener: vi.fn(), removeEventListener: vi.fn() }))
    onResolve = vi.fn()
    onAnswer = vi.fn()
  })
  afterEach(() => { cleanup(); vi.useRealTimers(); vi.unstubAllGlobals() })

  it('runs to a distant wrong block and falls at main in git init main -b', async () => {
    mount()
    place(['git', 'init', 'main', '-b'])
    expect(document.querySelectorAll('[data-collapsed]').length).toBe(0)
    await advance(100)
    expect(screen.getByRole('button', { name: 'Wrong block main at position 3' })).toBeDisabled()
    expect(document.querySelectorAll('[data-collapsed]').length).toBe(1)
    expect(screen.getByTestId('pose')).toHaveTextContent('run')
    expect(screen.queryByText('The path holds. Heading for the checkpoint.')).not.toBeInTheDocument()
    await advance(3200)
    expect(onResolve).not.toHaveBeenCalled()
    expect(screen.getByTestId('pose')).toHaveTextContent('run')
    await advance(700)
    expect(document.querySelector('.drill-checkpoint')).toHaveAttribute('data-phase', 'falling')
    expect(onResolve).not.toHaveBeenCalled()
    await advance(1200)
    expect(onResolve).toHaveBeenCalledExactlyOnceWith({ kind: 'tokens', values: ['git', 'init', 'main', '-b'] }, true)
    expect(screen.getByTestId('pose')).toHaveTextContent('idle')
  })

  it('keeps a nearby wrong block locked and walks to its hole', async () => {
    mount()
    const answer = ['init', 'git', '-b', 'main']
    place(answer)
    await advance(100)
    const wrong = screen.getByRole('button', { name: 'Wrong block init at position 1' })
    expect(wrong).toBeDisabled()
    expect(screen.getByTestId('pose')).toHaveTextContent('walk')
    fireEvent.click(wrong)
    await advance(2000)
    expect(screen.getByTestId('pose')).toHaveTextContent('walk')
    expect(onResolve).not.toHaveBeenCalled()
    await advance(7000)
    expect(onResolve).toHaveBeenCalledExactlyOnceWith({ kind: 'tokens', values: answer }, true)
  })

  it('falls through the first unfilled gap before the answer is complete', async () => {
    mount()
    place(['git'])
    await advance(15000)
    expect(onResolve).toHaveBeenCalledExactlyOnceWith({ kind: 'tokens', values: ['git'] }, true)
    expect(document.querySelector('[data-collapsed]')).toBe(document.querySelectorAll('.drill-path-block')[1])
  })

  it('lets the learner finish the path while Blue walks, then reaches the checkpoint', async () => {
    mount()
    await advance(1000)
    place(expected)
    await advance(31000)
    expect(onResolve).toHaveBeenCalledExactlyOnceWith({ kind: 'tokens', values: expected }, false)
    expect(document.querySelector('[data-collapsed]')).toBeNull()
  })

  it('waits for the whole correct answer before running, then walks into the checkpoint', async () => {
    mount()
    await advance(1000)
    expect(screen.getByTestId('pose')).toHaveTextContent('walk')
    place(['git', 'init', '-b'])
    await advance(500)
    expect(screen.getByTestId('pose')).toHaveTextContent('walk')
    place(['main'])
    await advance(100)
    expect(screen.getByTestId('pose')).toHaveTextContent('run')
    expect(onResolve).not.toHaveBeenCalled()
    await advance(5400)
    expect(screen.getByTestId('pose')).toHaveTextContent('walk')
    expect(onResolve).not.toHaveBeenCalled()
    await advance(4000)
    expect(screen.getByTestId('pose')).toHaveTextContent('idle')
    expect(onResolve).toHaveBeenCalledExactlyOnceWith({ kind: 'tokens', values: expected }, false)
  })

  it('keeps walking when a correct answer leaves only a short crossing', async () => {
    mount()
    place(['git', 'init', '-b'])
    await advance(20000)
    place(['main'])
    await advance(100)
    expect(screen.getByTestId('pose')).toHaveTextContent('walk')
    await advance(10000)
    expect(onResolve).toHaveBeenCalledExactlyOnceWith({ kind: 'tokens', values: expected }, false)
  })

  it('pauses the crossing without spending building time', async () => {
    mount()
    await advance(1000)
    fireEvent.click(screen.getByRole('button', { name: 'Pause crossing' }))
    await advance(30000)
    expect(onResolve).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Resume crossing' }))
    await advance(10000)
    expect(onResolve).toHaveBeenCalledExactlyOnceWith(null, true)
  })

  it('handles ordered steps as land', async () => {
    mount('steps', ['git init', 'git add .'])
    place(['git add .', 'git init'])
    await advance(11000)
    expect(onResolve).toHaveBeenCalledExactlyOnceWith({ kind: 'tokens', values: ['git add .', 'git init'] }, true)
  })

  it('places a completed piece immediately while an unfinished prefix stays off the path', async () => {
    mount()
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Type it instead' })).not.toBeInTheDocument()
    type('gi')
    expect(onAnswer).not.toHaveBeenCalled()
    expect(document.querySelector('.drill-path-keystrokes')).toHaveTextContent('gi')
    type('t')
    expect(screen.getByRole('button', { name: 'Remove git from position 1' })).toBeInTheDocument()
    expect(onAnswer).toHaveBeenLastCalledWith({ kind: 'tokens', values: ['git'] })
    expect(document.querySelector('.drill-path-keystrokes')).toBeEmptyDOMElement()
    type(' init -b main')
    await advance(31000)
    expect(onResolve).toHaveBeenCalledExactlyOnceWith({ kind: 'tokens', values: expected }, false)
  })

  it('mixes mouse placement with immediate typing from a focused bank button', async () => {
    mount()
    place(['git'])
    const init = screen.getByRole('button', { name: 'init' })
    init.focus()
    type('init', init)
    place(['-b'])
    type('main')
    expect(onAnswer).toHaveBeenLastCalledWith({ kind: 'tokens', values: expected })
    await advance(31000)
    expect(onResolve).toHaveBeenCalledExactlyOnceWith({ kind: 'tokens', values: expected }, false)
  })

  it('corrects a mistyped prefix and removes the last block with Backspace', () => {
    mount()
    type('gti')
    expect(document.querySelector('.drill-path-keystrokes')).toHaveAttribute('data-invalid')
    fireEvent.keyDown(window, { key: 'Backspace' })
    fireEvent.keyDown(window, { key: 'Backspace' })
    type('it')
    expect(onAnswer).toHaveBeenLastCalledWith({ kind: 'tokens', values: ['git'] })
    fireEvent.keyDown(window, { key: 'Backspace' })
    expect(onAnswer).toHaveBeenLastCalledWith(null)
    expect(screen.getByRole('button', { name: 'git' })).toBeInTheDocument()
  })

  it('moves focus off an older slab after typing so a following Space cannot remove it', () => {
    mount()
    place(['git'])
    const olderBlock = screen.getByRole('button', { name: 'Remove git from position 1' })
    olderBlock.focus()
    type('init', olderBlock)
    const course = screen.getByRole('region', { name: 'Command pavement' })
    expect(course).toHaveFocus()
    expect(fireEvent.keyDown(document.activeElement!, { key: ' ' })).toBe(false)
    fireEvent.keyUp(document.activeElement!, { key: ' ' })
    expect(screen.getByRole('button', { name: 'Remove git from position 1' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Remove init from position 2' })).toBeInTheDocument()
    expect(onAnswer).toHaveBeenLastCalledWith({ kind: 'tokens', values: ['git', 'init'] })
  })

  it('waits for a delimiter when a complete piece is also a longer piece prefix', () => {
    mount('tokens', ['git', 'gitk'])
    type('git')
    expect(onAnswer).not.toHaveBeenCalled()
    fireEvent.keyDown(window, { key: 'Enter' })
    expect(onAnswer).toHaveBeenLastCalledWith({ kind: 'tokens', values: ['git'] })
    type('gitk')
    expect(onAnswer).toHaveBeenLastCalledWith({ kind: 'tokens', values: ['git', 'gitk'] })
  })

  it('uses a separate available piece for each repeated value', () => {
    mount('tokens', ['git', 'git'])
    type('gitgit')
    expect(onAnswer).toHaveBeenLastCalledWith({ kind: 'tokens', values: ['git', 'git'] })
    expect(screen.getByRole('button', { name: 'Remove git from position 1' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Remove git from position 2' })).toBeInTheDocument()
  })

  it('accepts complete multi-word steps without changing input modes', () => {
    mount('steps', ['git init', 'git add .'])
    type('git init')
    expect(onAnswer).toHaveBeenLastCalledWith({ kind: 'tokens', values: ['git init'] })
    type('git add .')
    expect(onAnswer).toHaveBeenLastCalledWith({ kind: 'tokens', values: ['git init', 'git add .'] })
  })

  it('does not consume shortcuts, Escape, native piece activation, or typing in another field', () => {
    mount()
    for (const modifier of ['ctrlKey', 'metaKey', 'altKey']) {
      fireEvent.keyDown(window, { key: 'g', [modifier]: true })
    }
    fireEvent.keyDown(window, { key: 'g', repeat: true })
    fireEvent.keyDown(window, { key: 'g', isComposing: true })
    expect(fireEvent.keyDown(window, { key: 'Escape' })).toBe(true)
    const git = screen.getByRole('button', { name: 'git' })
    git.focus()
    expect(fireEvent.keyDown(git, { key: ' ' })).toBe(true)
    expect(fireEvent.keyDown(git, { key: 'Enter' })).toBe(true)
    const input = document.createElement('input')
    document.body.append(input)
    type('git', input)
    input.remove()
    const pause = screen.getByRole('button', { name: 'Pause crossing' })
    type('git', pause)
    expect(onAnswer).not.toHaveBeenCalled()
    expect(document.querySelector('.drill-path-keystrokes')).toBeEmptyDOMElement()
  })

  it('does not place pieces while paused or after the answer has locked', () => {
    const view = render(<DrillCheckpointArena values={expected} expected={expected} variant="tokens"
      onAnswer={onAnswer} onResolve={onResolve} verdict={null} paused />)
    type('git')
    expect(onAnswer).not.toHaveBeenCalled()
    view.rerender(<DrillCheckpointArena values={expected} expected={expected} variant="tokens"
      onAnswer={onAnswer} onResolve={onResolve} verdict={null} paused={false} />)
    type('git')
    expect(onAnswer).toHaveBeenCalledTimes(1)
    view.rerender(<DrillCheckpointArena values={expected} expected={expected} variant="tokens"
      onAnswer={onAnswer} onResolve={onResolve} verdict={{ correct: false, picked: 'git', pickedGloss: null }} />)
    type('init')
    expect(onAnswer).toHaveBeenCalledTimes(1)
  })

  it('cancels an in-progress fall when the round unmounts', async () => {
    const view = mount()
    await advance(7400)
    expect(document.querySelector('.drill-checkpoint')).toHaveAttribute('data-phase', 'falling')
    view.unmount()
    await advance(5000)
    expect(onResolve).not.toHaveBeenCalled()
  })
})
