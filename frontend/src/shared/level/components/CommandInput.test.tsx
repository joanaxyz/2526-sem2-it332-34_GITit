import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { CommandInput } from '@/shared/level/components/CommandInput'

const prompt = { user: 'learner', host: 'challenge', cwd: '~/repo' }
const originalClipboard = navigator.clipboard

function mockClipboard(readText: () => Promise<string>) {
  Object.defineProperty(navigator, 'clipboard', {
    configurable: true,
    value: { readText },
  })
}

describe('CommandInput clipboard paste', () => {
  afterEach(() => {
    cleanup()
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: originalClipboard,
    })
    vi.restoreAllMocks()
  })

  it('normalizes multiline clipboard text and replaces the current selection without submitting', async () => {
    const onSubmit = vi.fn()
    const readText = vi.fn().mockResolvedValue('add\nREADME.md')
    mockClipboard(readText)
    vi.spyOn(window, 'requestAnimationFrame').mockImplementation((callback) => {
      callback(0)
      return 1
    })

    render(<CommandInput prompt={prompt} onSubmit={onSubmit} />)
    const input = screen.getByRole('textbox', { name: 'Git command' }) as HTMLInputElement
    fireEvent.change(input, { target: { value: 'git replace' } })
    input.setSelectionRange(4, 11)

    fireEvent.click(screen.getByRole('button', { name: 'Paste from clipboard' }))

    await waitFor(() => expect(input).toHaveValue('git add README.md'))
    expect(input).toHaveFocus()
    expect(input).toHaveProperty('selectionStart', 17)
    expect(screen.getByRole('status')).toHaveTextContent('Pasted into command.')
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('reports blocked clipboard access and leaves the command untouched', async () => {
    const onSubmit = vi.fn()
    mockClipboard(vi.fn().mockRejectedValue(new Error('denied')))

    render(<CommandInput prompt={prompt} onSubmit={onSubmit} />)
    const input = screen.getByRole('textbox', { name: 'Git command' }) as HTMLInputElement
    fireEvent.change(input, { target: { value: 'git status' } })

    fireEvent.click(screen.getByRole('button', { name: 'Paste from clipboard' }))

    await waitFor(() => {
      expect(screen.getByRole('status')).toHaveTextContent('Clipboard access is unavailable')
    })
    expect(input).toHaveValue('git status')
    expect(input).toHaveFocus()
    expect(onSubmit).not.toHaveBeenCalled()
  })
})
