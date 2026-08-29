import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { TerminalPrompt } from '@/shared/level/terminalPrompt'
import { CommandInput } from './CommandInput'

const prompt: TerminalPrompt = { user: 'blue', host: 'arcane-spire', cwd: '~/repo' }

function Harness({ disabled }: { disabled: boolean }) {
  return (
    <>
      <button type="button">Elsewhere</button>
      <CommandInput prompt={prompt} disabled={disabled} onSubmit={vi.fn()} />
    </>
  )
}

describe('CommandInput focus behavior', () => {
  afterEach(() => {
    cleanup()
  })

  it('autofocuses the prompt input on mount', () => {
    render(<CommandInput prompt={prompt} onSubmit={vi.fn()} />)

    expect(screen.getByLabelText('Git command')).toHaveFocus()
  })

  it('does not steal focus back from another element across a disabled false->true->false cycle', () => {
    const { rerender } = render(<Harness disabled={false} />)

    // Simulate the learner tabbing away from the prompt (e.g. to inspect the
    // DAG panel or terminal output) before a command finishes processing.
    const elsewhere = screen.getByRole('button', { name: 'Elsewhere' })
    elsewhere.focus()
    expect(elsewhere).toHaveFocus()

    // Command submission disables the input while it processes.
    rerender(<Harness disabled={true} />)
    expect(elsewhere).toHaveFocus()

    // Processing finishes and the input re-enables; focus must stay put
    // instead of being yanked back into the prompt.
    rerender(<Harness disabled={false} />)
    expect(elsewhere).toHaveFocus()
  })
})
