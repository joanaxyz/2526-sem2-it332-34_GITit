import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { TierStoryModal } from './TierStoryModal'

afterEach(cleanup)

const story = {
  title: 'Initialize invoice-tracker',
  intro: 'A client hired you to build a simple invoice tracker.',
  task: 'Create and initialize a new Git repository named invoice-tracker.',
}

describe('TierStoryModal', () => {
  it('shows the title, intro and task from the run, without an empty context section', () => {
    render(<TierStoryModal open {...story} onClose={vi.fn()} />)

    expect(screen.getByRole('dialog', { name: story.title })).toBeInTheDocument()
    expect(screen.getByText(story.intro)).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Your task' })).toBeInTheDocument()
    expect(screen.getByText(story.task)).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Real-world context' })).not.toBeInTheDocument()
  })

  it('shows real-world context only when it is given', () => {
    render(<TierStoryModal open {...story} realWorldContext="Every team versions its code." onClose={vi.fn()} />)

    expect(screen.getByRole('heading', { name: 'Real-world context' })).toBeInTheDocument()
    expect(screen.getByText('Every team versions its code.')).toBeInTheDocument()
  })

  it('falls back to a short notice when the run carries no story text', () => {
    render(<TierStoryModal open title="Level" intro="" task="" onClose={vi.fn()} />)

    expect(screen.getByText('No story is available for this level.')).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Your task' })).not.toBeInTheDocument()
  })

  it('closes from the primary action and from Ctrl+Enter', () => {
    const onClose = vi.fn()
    render(<TierStoryModal open {...story} onClose={onClose} />)

    fireEvent.click(screen.getByRole('button', { name: /start coding/i }))
    expect(onClose).toHaveBeenCalledTimes(1)

    fireEvent.keyDown(document, { key: 'Enter', ctrlKey: true })
    expect(onClose).toHaveBeenCalledTimes(2)

    fireEvent.keyDown(document, { key: 'Enter' })
    expect(onClose).toHaveBeenCalledTimes(2)
  })

  it('renders nothing while closed', () => {
    render(<TierStoryModal open={false} {...story} onClose={vi.fn()} />)

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })
})
