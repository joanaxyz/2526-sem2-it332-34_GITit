import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { WorkspaceObjective } from '@/shared/level/workspace/types'

import { ObjectivesCard } from './ObjectivesCard'

afterEach(cleanup)

const objectives: WorkspaceObjective[] = [
  { id: 'a', text: 'Initialize a new repository', status: 'done' },
  { id: 'b', text: 'Do not stage files or create a commit', status: 'failed' },
  { id: 'c', text: 'Name the first branch trunk', status: 'pending' },
]

describe('ObjectivesCard', () => {
  it('renders every objective with a status that does not rely on color alone', () => {
    render(<ObjectivesCard objectives={objectives} requiredValues={[]} />)

    const rows = within(screen.getByRole('list', { name: 'Objectives' })).getAllByRole('listitem')
    expect(rows).toHaveLength(3)
    expect(rows[0]).toHaveClass('is-done')
    expect(rows[0]).toHaveTextContent('Initialize a new repositoryDone')
    expect(rows[1]).toHaveClass('is-failed')
    expect(rows[1]).toHaveTextContent('Failed')
    expect(rows[2]).toHaveClass('is-pending')
    expect(rows[2]).toHaveTextContent('Not done yet')
  })

  it('shows an explicit empty state when the level lists no objective', () => {
    render(<ObjectivesCard objectives={[]} requiredValues={[]} />)

    expect(screen.queryByRole('list', { name: 'Objectives' })).not.toBeInTheDocument()
    expect(screen.getByText('No objective is listed for this level.')).toBeInTheDocument()
  })

  it('lists required values with copy actions', () => {
    render(
      <ObjectivesCard
        objectives={objectives.slice(0, 1)}
        requiredValues={[{ label: 'Repository URL', value: 'https://example.test/docs-portal.git' }]}
      />,
    )

    const values = screen.getByRole('list', { name: 'Values the objective requires' })
    expect(values).toHaveTextContent('Repository URL')
    expect(values).toHaveTextContent('https://example.test/docs-portal.git')
    expect(within(values).getByRole('button')).toBeInTheDocument()
  })

  it('keeps the Story button disabled until a story handler is wired', () => {
    const { rerender } = render(<ObjectivesCard objectives={objectives} requiredValues={[]} />)
    expect(screen.getByRole('button', { name: 'Story' })).toBeDisabled()

    const onOpenStory = vi.fn()
    rerender(<ObjectivesCard objectives={objectives} requiredValues={[]} onOpenStory={onOpenStory} />)
    fireEvent.click(screen.getByRole('button', { name: 'Story' }))
    expect(onOpenStory).toHaveBeenCalledOnce()
  })
})
