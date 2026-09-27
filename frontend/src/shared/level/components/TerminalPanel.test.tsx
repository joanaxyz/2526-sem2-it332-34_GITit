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
})
