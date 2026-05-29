import { AlertTriangle, ChevronDown, ExternalLink, FilePlus, FileText, Folder, FolderOpen, Plus } from 'lucide-react'
import type { FormEvent } from 'react'
import { useMemo, useState } from 'react'

import type { RepositorySnapshot } from '@/features/practice/types'
import {
  buildProjectTree,
  flattenProjectFiles,
  lineNumbersFor,
  workspaceFileErrorMessage,
} from '@/features/practice/utils/projectFiles'
import type { ProjectTreeNode } from '@/features/practice/utils/projectFiles'
import { Button } from '@/shared/components/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'
import { Modal } from '@/shared/components/Modal'
import { cn } from '@/shared/utils/cn'

type CreateFileInput = {
  path: string
  content: string
}

type ProjectStructurePanelProps = {
  snapshot: RepositorySnapshot
  className?: string
  selectedPath?: string | null
  createDisabled?: boolean
  isOpen?: boolean
  onToggle?: () => void
  onCreateFile?: (input: CreateFileInput) => Promise<unknown> | void
  onOpenFile?: (path: string) => void
}

function TreeItem({
  node,
  depth = 0,
  createDisabled = false,
  selectedPath,
  onAddFile,
  onOpenFile,
}: {
  node: ProjectTreeNode
  depth?: number
  createDisabled?: boolean
  selectedPath?: string | null
  onAddFile?: (directoryPath: string) => void
  onOpenFile?: (filePath: string) => void
}) {
  const [expanded, setExpanded] = useState(true)
  const isDir = node.type === 'directory'
  const isSelected = !isDir && selectedPath === node.path
  const indent = `${depth * 12 + 4}px`

  return (
    <div>
      <div
        className={cn(
          'flex w-full items-center gap-1.5 rounded-sm px-1 py-0.5 text-left text-xs',
          isDir ? 'font-medium text-foreground hover:bg-secondary' : 'text-muted-foreground hover:bg-secondary/60',
          isSelected && 'bg-primary/10 text-foreground ring-1 ring-primary/30',
        )}
        style={{ paddingLeft: indent }}
      >
        <button
          type="button"
          className="flex min-w-0 flex-1 items-center gap-1.5 text-left"
          onClick={() => {
            if (isDir) {
              setExpanded((value) => !value)
              return
            }
            onOpenFile?.(node.path)
          }}
        >
          {isDir ? (
            expanded ? (
              <FolderOpen className="size-3.5 shrink-0 text-primary" />
            ) : (
              <Folder className="size-3.5 shrink-0 text-primary" />
            )
          ) : (
            <FileText className="size-3.5 shrink-0 text-muted-foreground" />
          )}
          <span className="truncate">{node.name}</span>
        </button>
        {node.conflict ? (
          <button
            type="button"
            className="grid size-5 shrink-0 place-items-center rounded-sm bg-destructive/10 text-destructive hover:bg-destructive/15"
            title={`Open conflict resolver for ${node.path}`}
            aria-label={`Open conflict resolver for ${node.path}`}
            onClick={(event) => {
              event.stopPropagation()
              onOpenFile?.(node.path)
            }}
          >
            <AlertTriangle className="size-3" />
          </button>
        ) : null}
        {node.status && node.status !== 'clean' ? (
          <span
            className={cn(
              'shrink-0 rounded px-1 text-[10px] font-medium uppercase leading-none',
              node.source === 'staging' ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground',
            )}
            title={node.source === 'staging' ? 'Staged' : node.source === 'working_tree' ? 'Working tree' : 'Committed'}
          >
            {node.status}
          </span>
        ) : null}
        {!isDir && onOpenFile ? (
          <button
            type="button"
            className="grid size-5 shrink-0 place-items-center rounded-sm text-muted-foreground hover:bg-background hover:text-foreground"
            title={`Open ${node.path}`}
            aria-label={`Open ${node.path}`}
            onClick={(event) => {
              event.stopPropagation()
              onOpenFile(node.path)
            }}
          >
            <ExternalLink className="size-3" />
          </button>
        ) : null}
        {isDir && onAddFile ? (
          <button
            type="button"
            className="grid size-5 shrink-0 place-items-center rounded-sm text-muted-foreground hover:bg-background hover:text-foreground disabled:pointer-events-none disabled:opacity-50"
            title={`Add file in ${node.path}`}
            aria-label={`Add file in ${node.path}`}
            disabled={createDisabled}
            onClick={(event) => {
              event.stopPropagation()
              onAddFile(node.path)
            }}
          >
            <Plus className="size-3.5" />
          </button>
        ) : null}
      </div>
      {isDir && expanded ? (
        <div>
          {node.children.map((child) => (
            <TreeItem
              key={child.path}
              node={child}
              depth={depth + 1}
              createDisabled={createDisabled}
              selectedPath={selectedPath}
              onAddFile={onAddFile}
              onOpenFile={onOpenFile}
            />
          ))}
        </div>
      ) : null}
    </div>
  )
}

export function ProjectStructurePanel({
  snapshot,
  className,
  selectedPath,
  createDisabled = false,
  isOpen = true,
  onToggle,
  onCreateFile,
  onOpenFile,
}: ProjectStructurePanelProps) {
  const tree = useMemo(() => buildProjectTree(snapshot), [snapshot])
  const files = useMemo(() => flattenProjectFiles(tree), [tree])
  const filePaths = useMemo(() => new Set(files.map((file) => file.path)), [files])
  const hasFiles = tree.length > 0
  const [modalOpen, setModalOpen] = useState(false)
  const [path, setPath] = useState('')
  const [content, setContent] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const canCreateFile = Boolean(onCreateFile) && !createDisabled && !submitting
  const firstConflictPath = (snapshot.conflicts ?? []).find((conflictPath) => filePaths.has(conflictPath))
  const lineNumbers = lineNumbersFor(content)

  function openCreateFileModal(directoryPath = '') {
    const prefix = directoryPath ? `${directoryPath}/` : ''
    setPath(prefix)
    setContent('')
    setError('')
    setModalOpen(true)
  }

  function closeCreateFileModal() {
    if (submitting) return
    setModalOpen(false)
    setError('')
  }

  async function handleCreateFile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const nextPath = path.trim()
    if (!nextPath) {
      setError('File path is required.')
      return
    }
    if (nextPath.endsWith('/')) {
      setError('File path must include a file name.')
      return
    }
    if (!onCreateFile) return

    setSubmitting(true)
    setError('')
    try {
      await onCreateFile({ path: nextPath, content })
      setModalOpen(false)
      setPath('')
      setContent('')
      onOpenFile?.(nextPath)
    } catch (createError) {
      setError(workspaceFileErrorMessage(createError, 'Could not create the file.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Card
      className={cn('flex flex-col overflow-hidden shadow-none', isOpen && 'min-h-[18rem]', className)}
      style={{ borderTop: '1.5px solid rgba(0,245,212,0.42)' }}
    >
      <CardHeader
        className="flex-row items-center justify-between gap-2 px-4 py-3"
        style={{ background: 'rgba(0,245,212,0.025)' }}
      >
        <CardTitle className="text-sm font-bold tracking-wide text-primary">Project Files</CardTitle>
        <div className="flex items-center gap-1">
          {firstConflictPath && onOpenFile ? (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="size-7 rounded-sm text-destructive hover:text-destructive"
              title="Open conflict resolver"
              aria-label="Open conflict resolver"
              onClick={() => onOpenFile(firstConflictPath)}
            >
              <AlertTriangle className="size-4" />
            </Button>
          ) : null}
          {onCreateFile ? (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="size-7 rounded-sm"
              title="Add file"
              aria-label="Add file"
              disabled={!canCreateFile}
              onClick={() => openCreateFileModal()}
            >
              <FilePlus className="size-4" />
            </Button>
          ) : null}
          {onToggle ? (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="size-7 rounded-sm"
              title={isOpen ? 'Collapse Project Files' : 'Expand Project Files'}
              aria-label={isOpen ? 'Collapse Project Files' : 'Expand Project Files'}
              aria-expanded={isOpen}
              onClick={onToggle}
            >
              <ChevronDown className={cn('size-4 transition-transform duration-200', !isOpen && 'rotate-180')} />
            </Button>
          ) : null}
        </div>
      </CardHeader>
      {isOpen ? <CardContent className="min-h-0 flex-1 p-2 pt-0">
        <div className="h-full min-h-0 overflow-auto rounded-md border border-border/70 bg-background/35 p-1 app-scrollbar">
          {hasFiles ? (
            <div className="pb-1">
              {tree.map((node) => (
                <TreeItem
                  key={node.path}
                  node={node}
                  createDisabled={!canCreateFile}
                  selectedPath={selectedPath}
                  onAddFile={onCreateFile ? openCreateFileModal : undefined}
                  onOpenFile={onOpenFile}
                />
              ))}
            </div>
          ) : (
            <p className="px-2 py-1 text-xs text-muted-foreground">No project files yet.</p>
          )}
        </div>
      </CardContent> : null}
      <Modal
        open={modalOpen}
        title="Add file"
        className="w-full max-w-2xl"
        contentClassName="p-0"
        onClose={closeCreateFileModal}
      >
        <form className="space-y-4 p-5" onSubmit={handleCreateFile}>
          <label className="block space-y-2 text-sm font-medium text-foreground">
            <span>Path</span>
            <input
              autoFocus
              value={path}
              disabled={submitting}
              onChange={(event) => setPath(event.target.value)}
              className="h-10 w-full rounded-md border border-border bg-background px-3 font-mono text-sm text-foreground outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20 disabled:opacity-60"
              placeholder="src/example.js"
            />
          </label>
          <label className="block space-y-2 text-sm font-medium text-foreground">
            <span>Content</span>
            <div className="grid h-56 grid-cols-[3rem_minmax(0,1fr)] overflow-hidden rounded-md border border-border bg-[#111827] font-mono text-xs shadow-inner">
              <div
                aria-hidden="true"
                className="select-none border-r border-white/10 bg-black/20 py-3 text-right leading-5 text-slate-500"
              >
                {lineNumbers.map((lineNumber) => (
                  <div key={lineNumber} className="px-3">
                    {lineNumber}
                  </div>
                ))}
              </div>
              <textarea
                value={content}
                aria-label="Content"
                disabled={submitting}
                spellCheck={false}
                onChange={(event) => setContent(event.target.value)}
                className="h-full w-full resize-none bg-transparent px-3 py-3 leading-5 text-slate-100 caret-primary outline-none placeholder:text-slate-500 disabled:opacity-60"
                placeholder="Write file contents here"
              />
            </div>
          </label>
          {error ? (
            <p role="alert" className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {error}
            </p>
          ) : null}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" disabled={submitting} onClick={closeCreateFileModal}>
              Cancel
            </Button>
            <Button type="submit" disabled={submitting || createDisabled}>
              {submitting ? 'Creating' : 'Create file'}
            </Button>
          </div>
        </form>
      </Modal>
    </Card>
  )
}
