import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { OrientationStep } from './types'
import { OrientationStepView } from './OrientationStepView'

function renderStep(step: OrientationStep) {
  const onStepComplete = vi.fn()
  const onContinueToNext = vi.fn()
  render(
    <OrientationStepView
      step={step}
      layout="storyboard"
      completed={false}
      onStepComplete={onStepComplete}
      hasNextStep
      onContinueToNext={onContinueToNext}
    />,
  )
  return { onStepComplete, onContinueToNext }
}

describe('OrientationStepView', () => {
  afterEach(cleanup)

  it('requires both comparison models to be inspected before continuing', () => {
    const { onStepComplete, onContinueToNext } = renderStep({
      id: 'compare',
      kind: 'compare_toggle',
      title: 'Compare models',
      prompt: 'Inspect both models.',
      options: [
        { id: 'centralized', label: 'Centralized', detail: 'One authoritative server.' },
        { id: 'distributed', label: 'Distributed', detail: 'Every clone has history.' },
      ],
    })

    const continueButton = screen.getByRole('button', { name: /complete comparison/i })
    expect(continueButton).toBeDisabled()

    fireEvent.click(screen.getByRole('button', { name: /Centralized/i }))
    expect(continueButton).toBeDisabled()

    fireEvent.click(screen.getByRole('button', { name: /Distributed/i }))
    expect(continueButton).toBeEnabled()
    fireEvent.click(continueButton)

    expect(onStepComplete).toHaveBeenCalledOnce()
    expect(onContinueToNext).toHaveBeenCalledOnce()
  })

  it('supports undo while assembling a command and completes only on an exact match', () => {
    const { onStepComplete } = renderStep({
      id: 'builder',
      kind: 'command_builder',
      title: 'Build a commit command',
      prompt: 'Build: git commit -m "message"',
      target: 'git commit -m "message"',
    })

    const completeButton = screen.getByRole('button', { name: /complete command/i })
    fireEvent.click(screen.getByRole('button', { name: 'git' }))
    fireEvent.click(screen.getByRole('button', { name: 'status' }))
    expect(completeButton).toBeDisabled()

    fireEvent.click(screen.getByRole('button', { name: 'Remove last token' }))
    fireEvent.click(screen.getByRole('button', { name: 'commit' }))
    fireEvent.click(screen.getByRole('button', { name: '-m' }))
    fireEvent.click(screen.getByRole('button', { name: '"message"' }))

    expect(screen.getByText('Command assembled correctly.')).toBeInTheDocument()
    expect(completeButton).toBeEnabled()
    fireEvent.click(completeButton)
    expect(onStepComplete).toHaveBeenCalledOnce()
  })

  it('gives recoverable feedback after a wrong error classification', () => {
    const { onStepComplete } = renderStep({
      id: 'error',
      kind: 'error_parse',
      title: 'Read an error',
      prompt: 'What failed?',
      error_text: 'fatal: not a git repository',
      answer: 'repository',
    })

    fireEvent.click(screen.getByRole('button', { name: 'flag' }))
    expect(screen.getByText(/Not quite/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /complete error check/i })).toBeDisabled()

    fireEvent.click(screen.getByRole('button', { name: 'repository' }))
    expect(screen.getByText(/Correct/i)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /complete error check/i }))
    expect(onStepComplete).toHaveBeenCalledOnce()
  })
})
