import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

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
    expect(screen.getAllByText('modified').length).toBeGreaterThan(0)
    expect(screen.getByText('untracked')).toBeInTheDocument()
  })

  it('shows the empty state for truly empty repositories', () => {
    render(<ProjectStructurePanel snapshot={baseSnapshot} />)

    expect(screen.getByText('No project files yet.')).toBeInTheDocument()
  })

  it('keeps a minimum usable height while allowing tree content to scroll', () => {
    const projectTree = Object.fromEntries(
      Array.from({ length: 30 }, (_, index) => [
        `src/generated/file-${index}.ts`,
        { status: 'clean', source: 'head', content: `file-${index}` },
      ]),
    )

    const { container } = render(
      <ProjectStructurePanel
        snapshot={{
          ...baseSnapshot,
          project_tree: projectTree,
        }}
      />,
    )

    expect(container.firstElementChild).toHaveClass('min-h-[18rem]')
    expect(container.querySelector('.overflow-auto')).toBeInTheDocument()
    expect(screen.getByText('file-0.ts')).toBeInTheDocument()
    expect(screen.getByText('file-29.ts')).toBeInTheDocument()
  })

  it('opens a clicked file in the editor and saves edits', async () => {
    const onWriteFile = vi.fn().mockResolvedValue(undefined)

    render(
      <ProjectStructurePanel
        snapshot={{
          ...baseSnapshot,
          project_tree: {
            'README.md': { status: 'clean', source: 'head', content: 'readme-v1' },
            'src/app.py': { status: 'modified', source: 'working_tree', content: 'print("v2")' },
          },
        }}
        onWriteFile={onWriteFile}
      />,
    )

    fireEvent.click(screen.getByText('app.py'))

    const editor = screen.getByTestId('file-editor')
    expect(within(editor).getByText('src/app.py')).toBeInTheDocument()
    expect(within(editor).getByLabelText('File content')).toHaveValue('print("v2")')

    fireEvent.change(within(editor).getByLabelText('File content'), {
      target: { value: 'print("fixed")\n' },
    })
    expect(within(editor).getByText('unsaved')).toBeInTheDocument()

    fireEvent.click(within(editor).getByRole('button', { name: 'Save file' }))

    await waitFor(() => {
      expect(onWriteFile).toHaveBeenCalledWith({
        path: 'src/app.py',
        content: 'print("fixed")\n',
      })
    })
  })

  it('surfaces conflict files when a merge conflict is present', async () => {
    render(
      <ProjectStructurePanel
        snapshot={{
          ...baseSnapshot,
          conflicts: ['src/auth.js'],
          project_tree: {
            'src/auth.js': {
              status: 'conflicted',
              source: 'working_tree',
              content: '<<<<<<< HEAD\ntimeout=5000\n=======\ntimeout=2500\n>>>>>>> feature/auth-timeout\n',
            },
          },
        }}
      />,
    )

    await waitFor(() => {
      expect(screen.getByLabelText('File content')).toHaveValue(
        '<<<<<<< HEAD\ntimeout=5000\n=======\ntimeout=2500\n>>>>>>> feature/auth-timeout\n',
      )
    })
    expect(within(screen.getByTestId('file-editor')).getByText('conflict')).toBeInTheDocument()
  })

  it('opens a root add-file modal with a numbered code editor and submits the file', async () => {
    const onCreateFile = vi.fn().mockResolvedValue(undefined)

    render(<ProjectStructurePanel snapshot={baseSnapshot} onCreateFile={onCreateFile} />)

    fireEvent.click(screen.getByRole('button', { name: 'Add file' }))
    const dialog = screen.getByRole('dialog', { name: 'Add file' })

    fireEvent.change(within(dialog).getByLabelText('Path'), {
      target: { value: 'src/new-file.ts' },
    })
    fireEvent.change(within(dialog).getByLabelText('Content'), {
      target: { value: 'const answer = 42\nexport default answer\n' },
    })

    expect(within(dialog).getByText('1')).toBeInTheDocument()
    expect(within(dialog).getByText('8')).toBeInTheDocument()

    fireEvent.click(within(dialog).getByRole('button', { name: 'Create file' }))

    await waitFor(() => {
      expect(onCreateFile).toHaveBeenCalledWith({
        path: 'src/new-file.ts',
        content: 'const answer = 42\nexport default answer\n',
      })
    })
    await waitFor(() => {
      expect(screen.queryByRole('dialog', { name: 'Add file' })).not.toBeInTheDocument()
    })
  })

  it('prefills the selected folder when adding a file from a directory', () => {
    render(
      <ProjectStructurePanel
        snapshot={{
          ...baseSnapshot,
          project_tree: {
            'src/app.py': { status: 'clean', source: 'head', content: 'print("hello")' },
          },
        }}
        onCreateFile={vi.fn()}
      />,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Add file in src' }))

    expect(within(screen.getByRole('dialog', { name: 'Add file' })).getByLabelText('Path')).toHaveValue('src/')
  })

  it('shows validation before submitting an incomplete folder path', () => {
    const onCreateFile = vi.fn()

    render(<ProjectStructurePanel snapshot={baseSnapshot} onCreateFile={onCreateFile} />)

    fireEvent.click(screen.getByRole('button', { name: 'Add file' }))
    fireEvent.change(within(screen.getByRole('dialog', { name: 'Add file' })).getByLabelText('Path'), {
      target: { value: 'src/' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Create file' }))

    expect(screen.getByRole('alert')).toHaveTextContent('File path must include a file name.')
    expect(onCreateFile).not.toHaveBeenCalled()
  })
})
