import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { CopyButton } from './CopyButton'

describe('CopyButton', () => {
  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
  })

  it('copies the value and flips to a copied state', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    vi.stubGlobal('navigator', { clipboard: { writeText } })

    render(<CopyButton value="git@github.com:team/portal.git" label="remote URL" />)

    const button = screen.getByRole('button', { name: 'Copy remote URL' })
    fireEvent.click(button)

    expect(writeText).toHaveBeenCalledWith('git@github.com:team/portal.git')
    await waitFor(() => expect(screen.getByRole('button', { name: 'Copied' })).toBeInTheDocument())
  })

  it('falls back to execCommand when the clipboard API is unavailable', async () => {
    vi.stubGlobal('navigator', {})
    const execCommand = vi.fn().mockReturnValue(true)
    // jsdom does not implement execCommand; attach it for the fallback path.
    Object.defineProperty(document, 'execCommand', { value: execCommand, configurable: true })

    render(<CopyButton value="c1a2b3c" />)

    fireEvent.click(screen.getByRole('button', { name: 'Copy' }))

    expect(execCommand).toHaveBeenCalledWith('copy')
    await waitFor(() => expect(screen.getByRole('button', { name: 'Copied' })).toBeInTheDocument())
  })
})
