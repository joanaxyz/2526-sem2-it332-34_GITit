import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { TerminalLine } from '@/shared/level/types'
import { TerminalPanel } from './TerminalPanel'

const lines: TerminalLine[] = [
  { id: 'input-1', kind: 'input', text: 'git status' },
  { id: 'output-1', kind: 'output', text: 'nothing to commit' },
  { id: 'input-2', kind: 'input', text: 'clear' },
  { id: 'input-3', kind: 'input', text: 'ls' },
  { id: 'output-3', kind: 'output', text: 'README.md  src/' },
]

describe('TerminalPanel', () => {
  afterEach(() => cleanup())

  it('hides everything up to the latest clear, like a real terminal screen', () => {
    render(<TerminalPanel lines={lines} prompt="learner" onCommand={vi.fn()} />)

    expect(screen.queryByText('git status')).not.toBeInTheDocument()
    expect(screen.queryByText('nothing to commit')).not.toBeInTheDocument()
    expect(screen.getByText('README.md src/', { normalizer: (text) => text.replace(/\s+/g, ' ') })).toBeInTheDocument()
  })

  it('shows the working directory in the live prompt only when inside a folder', () => {
    const { rerender } = render(<TerminalPanel lines={[]} prompt="learner" onCommand={vi.fn()} />)
    expect(screen.queryByText('~/src/utils')).not.toBeInTheDocument()

    rerender(<TerminalPanel lines={[]} prompt="learner" cwd="src/utils" onCommand={vi.fn()} />)
    expect(screen.getByText('~/src/utils')).toBeInTheDocument()
    expect(screen.getByLabelText('Git command in ~/src/utils')).toBeInTheDocument()
  })

  it('keeps the prompt immediately after the output, with Paste in the title bar', () => {
    render(<TerminalPanel lines={lines} prompt="learner" onCommand={vi.fn()} />)

    const log = screen.getByRole('log')
    expect(log).toContainElement(screen.getByLabelText('Git command'))
    expect(log).not.toContainElement(screen.getByRole('button', { name: 'Paste from clipboard' }))
    expect(screen.queryByRole('button', { name: 'Run command' })).not.toBeInTheDocument()
    expect(document.querySelector('.terminal-panel--docked')).toBeNull()
    expect(document.querySelector('.terminal-input-dock')).toBeNull()
  })
})

describe('TerminalPanel scrollback', () => {
  afterEach(() => cleanup())

  function line(index: number): TerminalLine {
    return { id: `output-${index}`, kind: 'output', text: `line ${index}` }
  }

  /** jsdom has no layout: give the history fixed scroll metrics. */
  function setScrollMetrics(element: HTMLElement, { scrollHeight, clientHeight }: { scrollHeight: number; clientHeight: number }) {
    Object.defineProperty(element, 'scrollHeight', { configurable: true, value: scrollHeight })
    Object.defineProperty(element, 'clientHeight', { configurable: true, value: clientHeight })
  }

  it('puts the live prompt after the last output line in the same scrolling surface', () => {
    render(<TerminalPanel lines={lines} prompt="learner" onCommand={vi.fn()} />)

    const log = screen.getByRole('log')
    const input = screen.getByLabelText('Git command')
    const lastOutput = screen.getByText('README.md src/', { normalizer: (text) => text.replace(/\s+/g, ' ') })

    expect(log).toHaveAttribute('aria-live', 'polite')
    expect(log).toContainElement(input)
    expect(lastOutput.nextElementSibling).toContainElement(input)
  })

  it('starts an empty terminal with the prompt as its first line', () => {
    render(<TerminalPanel lines={[]} prompt="learner" onCommand={vi.fn()} />)

    expect(screen.getByRole('log').querySelector('.terminal-line')).toBeNull()
    expect(screen.getByRole('log').firstElementChild).toContainElement(screen.getByLabelText('Git command'))
    expect(screen.getByLabelText('Git command')).not.toHaveAttribute('placeholder')
  })

  it('focuses the input when the history is clicked', () => {
    render(<TerminalPanel lines={lines} prompt="learner" onCommand={vi.fn()} />)
    const input = screen.getByLabelText('Git command')
    input.blur()

    screen.getByRole('log').click()

    expect(input).toHaveFocus()
  })

  it('follows new output, pauses while the reader is scrolled up, and resumes at the bottom', () => {
    const { rerender } = render(<TerminalPanel lines={[line(1)]} prompt="learner" onCommand={vi.fn()} />)
    const log = screen.getByRole('log')
    setScrollMetrics(log, { scrollHeight: 1000, clientHeight: 200 })

    rerender(<TerminalPanel lines={[line(1), line(2)]} prompt="learner" onCommand={vi.fn()} />)
    expect(log.scrollTop).toBe(1000)

    // The reader scrolls up to earlier output: new lines must not yank them down.
    log.scrollTop = 100
    log.dispatchEvent(new Event('scroll'))
    rerender(<TerminalPanel lines={[line(1), line(2), line(3)]} prompt="learner" onCommand={vi.fn()} />)
    expect(log.scrollTop).toBe(100)

    // Back at the bottom, following resumes.
    log.scrollTop = 800
    log.dispatchEvent(new Event('scroll'))
    setScrollMetrics(log, { scrollHeight: 1200, clientHeight: 200 })
    rerender(<TerminalPanel lines={[line(1), line(2), line(3), line(4)]} prompt="learner" onCommand={vi.fn()} />)
    expect(log.scrollTop).toBe(1200)
  })

  it('keeps long output in the scrollback', () => {
    const long: TerminalLine = { id: 'long', kind: 'output', text: 'x'.repeat(600) }
    render(<TerminalPanel lines={[long]} prompt="learner" onCommand={vi.fn()} />)

    const log = screen.getByRole('log')
    expect(log.querySelector('.terminal-line')).toHaveTextContent('x'.repeat(600))
  })
})
