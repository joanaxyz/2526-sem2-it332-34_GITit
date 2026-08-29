import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { RepositorySnapshot } from '@/shared/level/types'
import { WorkspaceEditorOverlay } from './WorkspaceEditorOverlay'

const baseSnapshot: RepositorySnapshot = {
  repository_initialized: true,
  commits: [],
  branches: { main: null },
  head: { type: 'branch', name: 'main', target: null },
  staging: {},
  working_tree: {},
  conflicts: [],
}

describe('WorkspaceEditorOverlay', () => {
  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
  })

  it('opens a large editor overlay and saves edited file content', async () => {
    const onWriteFile = vi.fn().mockResolvedValue(undefined)

    render(
      <WorkspaceEditorOverlay
        open
        filePath="src/app.py"
        snapshot={{
          ...baseSnapshot,
          project_tree: {
            'src/app.py': { status: 'modified', source: 'working_tree', content: 'print("v2")' },
          },
        }}
        onClose={vi.fn()}
        onWriteFile={onWriteFile}
      />,
    )

    const dialog = screen.getByRole('dialog', { name: 'Workspace file editor' })
    expect(dialog).toHaveClass('workspace-editor-backdrop')
    expect(screen.getByText('src/app.py')).toBeInTheDocument()
    expect(within(dialog).getByText('Workspace editor')).toBeInTheDocument()

    fireEvent.change(screen.getByLabelText('File content'), {
      target: { value: 'print("fixed")\n' },
    })
    expect(screen.getByText('unsaved')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /save/i }))

    await waitFor(() => {
      expect(onWriteFile).toHaveBeenCalledWith({
        path: 'src/app.py',
        content: 'print("fixed")\n',
      })
    })
  })

  it('saves dirty editor content with the keyboard shortcut', async () => {
    const onWriteFile = vi.fn().mockResolvedValue(undefined)

    render(
      <WorkspaceEditorOverlay
        open
        filePath="src/app.py"
        snapshot={{
          ...baseSnapshot,
          project_tree: {
            'src/app.py': { status: 'modified', source: 'working_tree', content: 'print("v2")' },
          },
        }}
        onClose={vi.fn()}
        onWriteFile={onWriteFile}
      />,
    )

    const editor = screen.getByLabelText('File content')
    fireEvent.change(editor, {
      target: { value: 'print("shortcut")\n' },
    })
    fireEvent.keyDown(editor, { key: 's', ctrlKey: true })

    await waitFor(() => {
      expect(onWriteFile).toHaveBeenCalledWith({
        path: 'src/app.py',
        content: 'print("shortcut")\n',
      })
    })
  })

  it('shows conflict markers plus ours, theirs, and base details', () => {
    render(
      <WorkspaceEditorOverlay
        open
        filePath="src/auth.js"
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
          conflict_details: {
            'src/auth.js': {
              base: 'timeout=3000',
              ours: 'timeout=5000',
              theirs: 'timeout=2500',
              resolution: 'timeout=5000\nretry=enabled',
              merge_branch: 'feature/auth-timeout',
            },
          },
        }}
        onClose={vi.fn()}
        onWriteFile={vi.fn()}
      />,
    )

    const dialog = screen.getByRole('dialog', { name: 'Conflict resolver' })
    expect(within(dialog).getByLabelText('File content')).toHaveValue(
      '<<<<<<< HEAD\ntimeout=5000\n=======\ntimeout=2500\n>>>>>>> feature/auth-timeout\n',
    )
    expect(screen.getByText('Ours / HEAD')).toBeInTheDocument()
    expect(screen.getByText('Theirs / Incoming')).toBeInTheDocument()
    expect(screen.getByText('Base / Common Ancestor')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Use theirs' }))

    expect(screen.getByLabelText('File content')).toHaveValue('timeout=2500')
  })

  it('guards close and reset when edits are unsaved', () => {
    const onClose = vi.fn()
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(false)

    render(
      <WorkspaceEditorOverlay
        open
        filePath="README.md"
        snapshot={{
          ...baseSnapshot,
          project_tree: {
            'README.md': { status: 'clean', source: 'head', content: 'readme-v1' },
          },
        }}
        onClose={onClose}
        onWriteFile={vi.fn()}
      />,
    )

    fireEvent.change(screen.getByLabelText('File content'), {
      target: { value: 'changed' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Close editor' }))
    fireEvent.click(screen.getByRole('button', { name: /reset/i }))

    expect(confirm).toHaveBeenCalledTimes(2)
    expect(onClose).not.toHaveBeenCalled()
    expect(screen.getByLabelText('File content')).toHaveValue('changed')
  })
})
