import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { getScaffoldMessage } from './messages'
import { ScaffoldToast } from './ScaffoldToast'

afterEach(cleanup)

function renderToast(overrides: Partial<Parameters<typeof ScaffoldToast>[0]> = {}) {
  const props = {
    message: getScaffoldMessage('T1', 'easy'),
    trigger: 'T1' as const,
    difficulty: 'easy' as const,
    onProceedToCommandPreview: vi.fn(),
    onContinue: vi.fn(),
    ...overrides,
  }
  render(<ScaffoldToast {...props} />)
  return props
}

describe('ScaffoldToast', () => {
  it('renders both action buttons', () => {
    renderToast()
    expect(screen.getByTestId('scaffold-proceed')).toBeInTheDocument()
    expect(screen.getByTestId('scaffold-continue')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /proceed to command preview/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /continue/i })).toBeInTheDocument()
  })

  it('renders the scaffold message as plain text (no anchor tags)', () => {
    const { message } = renderToast({ trigger: 'T2', difficulty: 'easy' })
    const toast = screen.getByTestId('scaffold-toast')
    expect(toast.querySelector('a')).toBeNull()
    expect(toast.textContent).toContain(message)
  })

  it('calls onContinue when Continue is clicked', () => {
    const onContinue = vi.fn()
    renderToast({ onContinue })
    fireEvent.click(screen.getByTestId('scaffold-continue'))
    expect(onContinue).toHaveBeenCalledOnce()
  })

  it('calls onProceedToCommandPreview when Proceed is clicked', () => {
    const onProceedToCommandPreview = vi.fn()
    renderToast({ onProceedToCommandPreview })
    fireEvent.click(screen.getByTestId('scaffold-proceed'))
    expect(onProceedToCommandPreview).toHaveBeenCalledOnce()
  })

  it('renders T3 message for hard difficulty', () => {
    const message = getScaffoldMessage('T3', 'hard')
    renderToast({ trigger: 'T3', difficulty: 'hard', message })
    expect(screen.getByTestId('scaffold-toast').textContent).toContain(
      'Your repository state remains unresolved',
    )
  })

  it('does not render any markdown links in the message body', () => {
    const { message } = renderToast({ trigger: 'T2', difficulty: 'medium' })
    // The message text must not contain rendered anchor elements
    const anchors = screen.queryAllByRole('link')
    expect(anchors).toHaveLength(0)
    // And the raw message should not contain markdown link syntax that got parsed
    expect(message).not.toMatch(/\[.*?\]\(.*?\)/)
  })
})
