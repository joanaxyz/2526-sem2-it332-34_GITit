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

  it('waits for a typed command to be placed instead of grading an unfinished last word', async () => {
    mount()
    fireEvent.click(screen.getByRole('button', { name: 'Type it instead' }))
    fireEvent.change(screen.getByRole('textbox', { name: 'Type the command' }), { target: { value: 'git init -b m' } })
    await advance(500)
    expect(screen.getByRole('textbox')).toBeEnabled()
    expect(document.querySelector('[data-collapsed]')).toBeNull()
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'git init -b main' } })
    fireEvent.click(screen.getByRole('button', { name: 'Place command' }))
    await advance(31000)
    expect(onResolve).toHaveBeenCalledExactlyOnceWith({ kind: 'tokens', values: expected }, false)
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
