import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { RepositorySnapshot } from '@/shared/level/types'
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
  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
  })

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

  it('keeps the full editor out of the side panel and opens clicked files', () => {
    const onOpenFile = vi.fn()

    render(
      <ProjectStructurePanel
        snapshot={{
          ...baseSnapshot,
          project_tree: {
            'README.md': { status: 'clean', source: 'head', content: 'readme-v1' },
            'src/app.py': { status: 'modified', source: 'working_tree', content: 'print("v2")' },
          },
        }}
        onOpenFile={onOpenFile}
      />,
    )

    expect(screen.queryByTestId('file-editor')).not.toBeInTheDocument()

    fireEvent.click(screen.getByText('app.py'))

    expect(onOpenFile).toHaveBeenCalledWith('src/app.py')
  })

  it('surfaces conflict files and opens the conflict resolver action', () => {
    const onOpenFile = vi.fn()

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
        onOpenFile={onOpenFile}
      />,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Open conflict resolver' }))

    expect(onOpenFile).toHaveBeenCalledWith('src/auth.js')
    expect(screen.getByText('conflicted')).toBeInTheDocument()
  })

  it('creates a root file inline without opening the editor', async () => {
    const onCreateFile = vi.fn().mockResolvedValue(undefined)
    const onOpenFile = vi.fn()

    render(<ProjectStructurePanel snapshot={baseSnapshot} onCreateFile={onCreateFile} onOpenFile={onOpenFile} />)

    fireEvent.click(screen.getByRole('button', { name: 'New file' }))
    const nameInput = screen.getByLabelText('New file name')
    fireEvent.change(nameInput, {
      target: { value: 'src/new-file.ts' },
    })
    fireEvent.keyDown(nameInput, { key: 'Enter' })

    await waitFor(() => {
      expect(onCreateFile).toHaveBeenCalledWith({
        path: 'src/new-file.ts',
        content: '',
      })
    })
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(onCreateFile).toHaveBeenCalledTimes(1)
    expect(onOpenFile).not.toHaveBeenCalled()
  })

  it('creates a file inside a directory from the folder row action', async () => {
    const onCreateFile = vi.fn().mockResolvedValue(undefined)

    render(
      <ProjectStructurePanel
        snapshot={{
          ...baseSnapshot,
          project_tree: {
            'src/app.py': { status: 'clean', source: 'head', content: 'print("hello")' },
          },
        }}
        onCreateFile={onCreateFile}
      />,
    )

    fireEvent.click(screen.getByRole('button', { name: 'New file in src' }))
    const nameInput = screen.getByLabelText('New file name')
    fireEvent.change(nameInput, { target: { value: 'utils.py' } })
    fireEvent.keyDown(nameInput, { key: 'Enter' })

    await waitFor(() => {
      expect(onCreateFile).toHaveBeenCalledWith({ path: 'src/utils.py', content: '' })
    })
  })

  it('creates a folder using a gitkeep placeholder file', async () => {
    const onCreateFile = vi.fn().mockResolvedValue(undefined)

    render(<ProjectStructurePanel snapshot={baseSnapshot} onCreateFile={onCreateFile} />)

    fireEvent.click(screen.getByRole('button', { name: 'New folder' }))
    const nameInput = screen.getByLabelText('New folder name')
    fireEvent.change(nameInput, { target: { value: 'docs' } })
    fireEvent.keyDown(nameInput, { key: 'Enter' })

    await waitFor(() => {
      expect(onCreateFile).toHaveBeenCalledWith({ path: 'docs/.gitkeep', content: '' })
    })
  })

  it('renames a file from the right-click context menu', async () => {
    const onRenameFile = vi.fn().mockResolvedValue(undefined)

    render(
      <ProjectStructurePanel
        snapshot={{
          ...baseSnapshot,
          project_tree: {
            'src/app.py': { status: 'clean', source: 'head', content: 'print("hello")' },
          },
        }}
        onRenameFile={onRenameFile}
      />,
    )

    fireEvent.contextMenu(screen.getByText('app.py'))
    fireEvent.click(screen.getByRole('menuitem', { name: /rename/i }))
    const renameInput = screen.getByLabelText('Rename src/app.py')
    fireEvent.change(renameInput, { target: { value: 'main.py' } })
    fireEvent.keyDown(renameInput, { key: 'Enter' })

    await waitFor(() => {
      expect(onRenameFile).toHaveBeenCalledWith({ path: 'src/app.py', newPath: 'src/main.py' })
    })
  })

  it('deletes a file from the right-click context menu', async () => {
    const onDeleteFile = vi.fn().mockResolvedValue(undefined)
    vi.spyOn(window, 'confirm').mockReturnValue(true)

    render(
      <ProjectStructurePanel
        snapshot={{
          ...baseSnapshot,
          project_tree: {
            'src/app.py': { status: 'clean', source: 'head', content: 'print("hello")' },
          },
        }}
        onDeleteFile={onDeleteFile}
      />,
    )

    fireEvent.contextMenu(screen.getByText('app.py'))
    fireEvent.click(screen.getByRole('menuitem', { name: /delete/i }))

    await waitFor(() => {
      expect(onDeleteFile).toHaveBeenCalledWith('src/app.py')
    })
  })

  it('shows rename and delete row actions for files', async () => {
    const onRenameFile = vi.fn().mockResolvedValue(undefined)
    const onDeleteFile = vi.fn().mockResolvedValue(undefined)
    vi.spyOn(window, 'confirm').mockReturnValue(true)

    render(
      <ProjectStructurePanel
        snapshot={{
          ...baseSnapshot,
          project_tree: {
            'src/app.py': { status: 'clean', source: 'head', content: 'print("hello")' },
          },
        }}
        onRenameFile={onRenameFile}
        onDeleteFile={onDeleteFile}
      />,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Rename src/app.py' }))
    const renameInput = screen.getByLabelText('Rename src/app.py')
    fireEvent.change(renameInput, { target: { value: 'main.py' } })
    fireEvent.keyDown(renameInput, { key: 'Enter' })

    await waitFor(() => {
      expect(onRenameFile).toHaveBeenCalledWith({ path: 'src/app.py', newPath: 'src/main.py' })
    })

    cleanup()

    render(
      <ProjectStructurePanel
        snapshot={{
          ...baseSnapshot,
          project_tree: {
            'src/app.py': { status: 'clean', source: 'head', content: 'print("hello")' },
          },
        }}
        onDeleteFile={onDeleteFile}
      />,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Delete src/app.py' }))

    await waitFor(() => {
      expect(onDeleteFile).toHaveBeenCalledWith('src/app.py')
    })
  })

  it('shows validation before creating an unnamed file', () => {
    const onCreateFile = vi.fn()

    render(<ProjectStructurePanel snapshot={baseSnapshot} onCreateFile={onCreateFile} />)

    fireEvent.click(screen.getByRole('button', { name: 'New file' }))
    const nameInput = screen.getByLabelText('New file name')
    fireEvent.change(nameInput, { target: { value: '' } })
    fireEvent.keyDown(nameInput, { key: 'Enter' })

    expect(screen.getByRole('alert')).toHaveTextContent('Name is required.')
    expect(onCreateFile).not.toHaveBeenCalled()
  })
})
