import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import type { RepositorySnapshot } from '@/features/practice/types'
import { ProjectStructurePanel } from './ProjectStructurePanel'

const baseSnapshot: RepositorySnapshot = {
  repository_initialized: true,
  commits: [],
  branches: { main: null },
  head: { type: 'branch', name: 'main', target: null },
  staging: {},
  working_tree: {},
  conflicts: [],
}

describe('ProjectStructurePanel', () => {
  afterEach(() => cleanup())

  it('renders clean committed files from backend project_tree', () => {
    render(
      <ProjectStructurePanel
        snapshot={{
          ...baseSnapshot,
          project_tree: {
            'README.md': { status: 'clean', source: 'head', content: 'readme-v1' },
            'src/app.py': { status: 'modified', source: 'working_tree', content: 'app-v2' },
            'notes.md': { status: 'untracked', source: 'working_tree', content: 'draft' },
          },
        }}
      />
    )

    expect(screen.getByText('README.md')).toBeInTheDocument()
    expect(screen.getByText('src')).toBeInTheDocument()
    expect(screen.getByText('app.py')).toBeInTheDocument()
    expect(screen.getByText('modified')).toBeInTheDocument()
    expect(screen.getByText('untracked')).toBeInTheDocument()
  })

  it('shows the empty state for truly empty repositories', () => {
    render(<ProjectStructurePanel snapshot={baseSnapshot} />)

    expect(screen.getByText('No project files yet.')).toBeInTheDocument()
  })
})
