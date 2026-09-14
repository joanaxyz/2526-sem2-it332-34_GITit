import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { createElement } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { RepositorySnapshot } from '@/shared/level/types'
import { graphLayoutSignature } from '@/shared/level/utils/graphLayoutSignature'
import { LiveDagPanel } from './LiveDagPanel'

// Records the `nodes` array handed to ReactFlow on every render. A new array
// makes ReactFlow rebuild its node internals, which forgets each node's
// measured size and paints the graph hidden for a frame - the hover flicker.
const { renderedNodes } = vi.hoisted(() => ({ renderedNodes: [] as unknown[] }))

vi.mock('reactflow', async (importOriginal) => {
  const actual = await importOriginal<typeof import('reactflow')>()
  return {
    ...actual,
    default: (props: Parameters<typeof actual.default>[0]) => {
      renderedNodes.push(props.nodes)
      return createElement(actual.default, props)
    },
  }
})

const snapshot: RepositorySnapshot = {
  repository_initialized: true,
  commits: [
    {
      id: 'c1',
      message: 'Base',
      parents: [],
      tree: {
        'README.md': 'readme-v1',
        'src/form.js': 'form-validation-v1',
      },
      changes: {
        'README.md': { change_type: 'added', before: null, after: 'readme-v1' },
      },
    },
    {
      id: 'c2',
      message: 'Update form validation',
      parents: ['c1'],
      tree: {
        'README.md': 'readme-v1',
        'src/form.js': 'form-validation-v2',
      },
      changes: {
        'src/form.js': {
          change_type: 'modified',
          before: 'form-validation-v1',
          after: 'form-validation-v2',
        },
      },
    },
  ],
  branches: { main: 'c2' },
  head: { type: 'branch' as const, name: 'main', target: 'c2' },
  staging: { 'src/form.js': 'form-validation-v2' },
  working_tree: { 'debug.log': 'debug-v1' },
  conflicts: [],
  remotes: { origin: 'https://example.test/repo.git' },
  remote_branches: { 'origin/main': 'c1' },
  upstream_tracking: { main: 'origin/main' },
  stash_stack: [{ working_tree: { 'notes.md': 'draft' }, staging: {}, conflicts: [] }],
  reflog: [],
  partial_hunks: {},
  operation_metadata: {},
}

describe('LiveDagPanel', () => {
  afterEach(() => {
    cleanup()
    renderedNodes.length = 0
  })

  it('keeps the same layout signature when only branch pointers move', () => {
    const movedPointerSnapshot: RepositorySnapshot = {
      ...snapshot,
      branches: { main: 'c1', feature: 'c2' },
      head: { type: 'branch', name: 'feature', target: 'c2' },
    }

    expect(graphLayoutSignature(snapshot)).toBe(graphLayoutSignature(movedPointerSnapshot))
  })

  it('renders a simplified commit summary in the diagram overlay when a node is active', () => {
    render(<LiveDagPanel snapshot={snapshot} />)

    const commitButton = screen.getByTitle(/commit c2/i)
    fireEvent.focus(commitButton)

    const overlay = screen.getByTestId('commit-details-overlay')
    expect(overlay).toBeInTheDocument()
    expect(screen.getByText('Message: Update form validation')).toBeInTheDocument()
    expect(within(overlay).getByText('main')).toBeInTheDocument()
  })

  it('keeps the ReactFlow nodes array stable while hovering a commit', () => {
    render(<LiveDagPanel snapshot={snapshot} />)
    const nodesBeforeHover = renderedNodes.at(-1)

    const commitNode = screen.getByTitle(/commit c2/i).parentElement as HTMLElement
    // React derives onMouseEnter from mouseover, so hover has to be fired that way.
    fireEvent.mouseOver(commitNode)

    expect(screen.getByTestId('commit-details-overlay')).toBeInTheDocument()
    expect(renderedNodes.at(-1)).toBe(nodesBeforeHover)

    fireEvent.mouseOut(commitNode)
    expect(screen.queryByTestId('commit-details-overlay')).not.toBeInTheDocument()
    expect(renderedNodes.at(-1)).toBe(nodesBeforeHover)
  })

  it('renders HEAD as a fixed seal and branch refs as banners', () => {
    render(<LiveDagPanel snapshot={snapshot} />)

    const head = screen.getByTitle(/commit c2/i)
    expect(head).toHaveClass('dag-commit-seal', 'is-head')
    expect(head.querySelector('.dag-commit-seal__ornament')).toBeInTheDocument()
    expect(head.querySelector('.dag-head-marker')).toHaveTextContent('HEAD')
    expect(screen.getByText('main')).toHaveClass('dag-ref-banner', 'is-active')
  })

  it('keeps repository metadata inside the diagram panel', () => {
    render(<LiveDagPanel title="Target DAG" snapshot={snapshot} showRepositoryDetails />)

    expect(screen.getByText('Target DAG')).toBeInTheDocument()
    expect(screen.getByText('Staged:')).toBeInTheDocument()
    expect(screen.getByText('Working tree:')).toBeInTheDocument()
    expect(screen.getByText('Remote branches:')).toBeInTheDocument()
    expect(screen.getByTitle(/Staged: src\/form\.js/)).toBeInTheDocument()
  })

  it('can render commits in a horizontal flow', () => {
    render(<LiveDagPanel snapshot={snapshot} layoutDirection="horizontal" />)

    const commitButton = screen.getByTitle(/commit c2/i)
    const commitNode = commitButton.parentElement

    expect(commitNode?.querySelector('.react-flow__handle-left')).toBeInTheDocument()
    expect(commitNode?.querySelector('.react-flow__handle-right')).toBeInTheDocument()
    expect(commitNode?.querySelector('.react-flow__handle-top')).not.toBeInTheDocument()
    expect(commitNode?.querySelector('.react-flow__handle-bottom')).not.toBeInTheDocument()
  })
})
