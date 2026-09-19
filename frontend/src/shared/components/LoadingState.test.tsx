import { cleanup, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { LoadingState } from './LoadingState'

describe('LoadingState', () => {
  afterEach(cleanup)

  it('loads a component in place, with a plain spinner and no companion', () => {
    const { container } = render(<LoadingState label="Loading users" variant="panel" />)

    expect(screen.getByRole('status', { name: 'Loading users' })).toBeInTheDocument()
    expect(container.querySelector('.git-it-spinner')).toBeInTheDocument()
    // The companion belongs to the full-screen LoadingScreen. A panel that ran
    // it ended up with the character boxed inside the layout.
    expect(container.querySelector('.git-it-companion-loader')).toBeNull()
    expect(document.body.querySelector('.git-it-loading-screen')).toBeNull()
  })

  it('announces the label before it paints, so a fast load never flashes', async () => {
    const { container } = render(<LoadingState label="Loading home" variant="panel" />)

    // The status and its label are live from the first frame; only the visual
    // frame waits, and the container still holds its box so nothing jumps.
    expect(screen.getByRole('status', { name: 'Loading home' })).toBeInTheDocument()
    expect(container.querySelector('.git-it-loading-state')).not.toHaveClass('is-painted')

    await waitFor(() => expect(container.querySelector('.git-it-loading-state')).toHaveClass('is-painted'))
  })

  it('sizes the spinner to the block it sits in', () => {
    const { container: panel } = render(<LoadingState label="Loading" variant="panel" />)
    expect(panel.querySelector('.git-it-spinner')).toHaveClass('git-it-spinner--md')

    const { container: compact } = render(<LoadingState label="Loading" variant="compact" />)
    expect(compact.querySelector('.git-it-spinner')).toHaveClass('git-it-spinner--xs')
  })

  it('drops the description on the densest variant', () => {
    render(<LoadingState description="Reading the story registry." label="Loading" variant="compact" />)

    expect(screen.queryByText('Reading the story registry.')).not.toBeInTheDocument()
  })
})
