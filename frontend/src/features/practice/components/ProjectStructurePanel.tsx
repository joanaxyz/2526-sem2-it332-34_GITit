import { AlertTriangle, FilePlus, FileText, Folder, FolderOpen, Plus, RotateCcw, Save } from 'lucide-react'
import type { FormEvent } from 'react'
import { useMemo, useState } from 'react'

import type { RepositorySnapshot, RepositoryValue } from '@/features/practice/types'
import { ApiError } from '@/shared/api/apiError'
import { Button } from '@/shared/components/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'
import { Modal } from '@/shared/components/Modal'
import { cn } from '@/shared/utils/cn'

type TreeNode = {
  name: string
  path: string
  type: 'file' | 'directory'
  status?: string
  source?: 'head' | 'staging' | 'working_tree'
  content?: RepositoryValue
  conflict?: boolean
  children: TreeNode[]
}

type CreateFileInput = {
  path: string
  content: string
}

type WorkspaceFileInput = {
  path: string
  content: string
}

type ProjectStructurePanelProps = {
  snapshot: RepositorySnapshot
  className?: string
  createDisabled?: boolean
  writeDisabled?: boolean
  onCreateFile?: (input: CreateFileInput) => Promise<unknown> | void
  onWriteFile?: (input: WorkspaceFileInput) => Promise<unknown> | void
}

function buildTree(snapshot: RepositorySnapshot): TreeNode[] {
  const root: TreeNode = { name: '', path: '', type: 'directory', children: [] }
  const conflictPaths = new Set(snapshot.conflicts ?? [])

  const addPath = (filePath: string, status: RepositoryValue, source: 'head' | 'staging' | 'working_tree') => {
    const parts = filePath.split('/')
    let current = root

    parts.forEach((part, index) => {
      const isFile = index === parts.length - 1
      const fullPath = parts.slice(0, index + 1).join('/')
      const existing = current.children.find((c) => c.name === part)

      if (existing) {
        if (isFile) {
          existing.status = statusLabel(status)
          existing.source = source
          existing.content = contentValue(status)
          existing.conflict = conflictPaths.has(filePath)
        }
        current = existing
      } else {
        const node: TreeNode = {
          name: part,
          path: fullPath,
          type: isFile ? 'file' : 'directory',
          status: isFile ? statusLabel(status) : undefined,
          source: isFile ? source : undefined,
          content: isFile ? contentValue(status) : undefined,
          conflict: isFile ? conflictPaths.has(filePath) : false,
          children: [],
        }
        current.children.push(node)
        current.children.sort((a, b) => {
          if (a.type === b.type) return a.name.localeCompare(b.name)
          return a.type === 'directory' ? -1 : 1
        })
        current = node
      }
    })
  }

  const visibleTree = snapshot.project_tree ?? snapshot.visible_tree
  if (visibleTree && Object.keys(visibleTree).length > 0) {
    Object.entries(visibleTree).forEach(([path, value]) => {
      const source = sourceLabel(value)
      addPath(path, value, source)
    })
  } else {
    Object.entries(snapshot.staging).forEach(([path, status]) => addPath(path, status, 'staging'))
    Object.entries(snapshot.working_tree).forEach(([path, status]) => addPath(path, status, 'working_tree'))
  }

  return root.children
}

function flattenFiles(nodes: TreeNode[]) {
  const files: TreeNode[] = []
  nodes.forEach((node) => {
    if (node.type === 'file') files.push(node)
    files.push(...flattenFiles(node.children))
  })
  return files
}

function statusLabel(value: RepositoryValue) {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    const status = value.status
    if (typeof status === 'string') return status
  }
  return String(value ?? 'changed')
}

function sourceLabel(value: RepositoryValue): 'head' | 'staging' | 'working_tree' {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    const source = value.source
    if (source === 'staging' || source === 'working_tree' || source === 'head') return source
  }
  return 'head'
}

function contentValue(value: RepositoryValue): RepositoryValue {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    if ('content' in value) return value.content
    if ('after' in value) return value.after
    if ('value' in value) return value.value
  }
  return value
}

function editorContent(value: RepositoryValue | undefined) {
  if (value === undefined || value === null) return ''
  return typeof value === 'string' ? value : JSON.stringify(value, null, 2)
}

function workspaceFileErrorMessage(error: unknown) {
  if (error instanceof ApiError && error.payload && typeof error.payload === 'object') {
    const payload = error.payload as Record<string, unknown>
    const pathErrors = payload.path
    if (Array.isArray(pathErrors) && pathErrors.length > 0) return String(pathErrors[0])
    if (typeof pathErrors === 'string') return pathErrors
  }
  if (error instanceof Error && error.message) return error.message
  return 'Could not create the file.'
}

function TreeItem({
  node,
  depth = 0,
  createDisabled = false,
  selectedPath,
  onAddFile,
  onSelectFile,
}: {
  node: TreeNode
  depth?: number
  createDisabled?: boolean
  selectedPath?: string | null
  onAddFile?: (directoryPath: string) => void
  onSelectFile?: (filePath: string) => void
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
          isSelected && 'bg-primary/10 text-foreground ring-1 ring-primary/30'
        )}
        style={{ paddingLeft: indent }}
      >
        <button
          type="button"
          className="flex min-w-0 flex-1 items-center gap-1.5 text-left"
          onClick={() => {
            if (isDir) {
              setExpanded((v) => !v)
              return
            }
            onSelectFile?.(node.path)
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
          <span className="grid size-4 shrink-0 place-items-center rounded-sm bg-destructive/10 text-destructive" title="Conflict">
            <AlertTriangle className="size-3" />
          </span>
        ) : null}
        {node.status && node.status !== 'clean' && (
          <span
            className={cn(
              'shrink-0 rounded px-1 text-[10px] font-medium uppercase leading-none',
              node.source === 'staging'
                ? 'bg-primary/10 text-primary'
                : 'bg-muted text-muted-foreground'
            )}
            title={node.source === 'staging' ? 'Staged' : node.source === 'working_tree' ? 'Working tree' : 'Committed'}
          >
            {node.status}
          </span>
        )}
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
      {isDir && expanded && (
        <div>
          {node.children.map((child) => (
            <TreeItem
              key={child.path}
              node={child}
              depth={depth + 1}
              createDisabled={createDisabled}
              selectedPath={selectedPath}
              onAddFile={onAddFile}
              onSelectFile={onSelectFile}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function lineNumbersFor(value: string, minimum = 8) {
  const lineCount = Math.max(minimum, value.split('\n').length)
  return Array.from({ length: lineCount }, (_, index) => index + 1)
}

function FileEditorSection({
  selectedPath,
  selectedFile,
  selectedContent,
  writeDisabled,
  onWriteFile,
}: {
  selectedPath: string | null
  selectedFile?: TreeNode
  selectedContent: string
  writeDisabled: boolean
  onWriteFile?: (input: WorkspaceFileInput) => Promise<unknown> | void
}) {
  const [draftContent, setDraftContent] = useState(selectedContent)
  const [editorError, setEditorError] = useState('')
  const [editorSubmitting, setEditorSubmitting] = useState(false)
  const hasEditor = Boolean(selectedFile)
  const editorDirty = hasEditor && draftContent !== selectedContent
  const canWriteFile = Boolean(onWriteFile) && !writeDisabled && !editorSubmitting && hasEditor
  const editorLineNumbers = lineNumbersFor(draftContent, 10)

  async function handleWriteFile() {
    if (!onWriteFile || !selectedPath || !editorDirty) return

    setEditorSubmitting(true)
    setEditorError('')
    try {
      await onWriteFile({ path: selectedPath, content: draftContent })
    } catch (writeError) {
      setEditorError(workspaceFileErrorMessage(writeError))
    } finally {
      setEditorSubmitting(false)
    }
  }

  return (
    <section
      className="flex min-h-0 flex-col overflow-hidden rounded-md border border-border/70 bg-background/50"
      data-testid="file-editor"
    >
      <div className="flex min-h-9 items-center justify-between gap-2 border-b border-border/70 px-2">
        <div className="flex min-w-0 items-center gap-1.5">
          <FileText className="size-3.5 shrink-0 text-muted-foreground" />
          <span className="truncate font-mono text-[11px] text-foreground">
            {selectedPath ?? 'No file selected'}
          </span>
        </div>
        <div className="flex shrink-0 items-center gap-1">
          {selectedFile?.conflict ? (
            <span className="rounded bg-destructive/10 px-1.5 py-0.5 text-[10px] font-semibold uppercase leading-none text-destructive">
              conflict
            </span>
          ) : null}
          {selectedFile?.status && selectedFile.status !== 'clean' ? (
            <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] font-semibold uppercase leading-none text-muted-foreground">
              {selectedFile.status}
            </span>
          ) : null}
          {editorDirty ? (
            <span className="rounded bg-primary/10 px-1.5 py-0.5 text-[10px] font-semibold uppercase leading-none text-primary">
              unsaved
            </span>
          ) : null}
          <button
            type="button"
            className="grid size-7 place-items-center rounded-sm text-muted-foreground hover:bg-secondary hover:text-foreground disabled:pointer-events-none disabled:opacity-40"
            title="Reset edits"
            aria-label="Reset edits"
            disabled={!editorDirty || editorSubmitting}
            onClick={() => setDraftContent(selectedContent)}
          >
            <RotateCcw className="size-3.5" />
          </button>
          <button
            type="button"
            className="grid size-7 place-items-center rounded-sm bg-primary text-primary-foreground hover:opacity-90 disabled:pointer-events-none disabled:opacity-40"
            title="Save file"
            aria-label="Save file"
            disabled={!canWriteFile || !editorDirty}
            onClick={handleWriteFile}
          >
            <Save className="size-3.5" />
          </button>
        </div>
      </div>
      <div className="grid min-h-0 flex-1 grid-cols-[2.5rem_minmax(0,1fr)] overflow-hidden bg-[#111827] font-mono text-xs">
        <div
          aria-hidden="true"
          className="select-none border-r border-white/10 bg-black/20 py-2 text-right leading-5 text-slate-500"
        >
          {editorLineNumbers.map((lineNumber) => (
            <div key={lineNumber} className="px-2">
              {lineNumber}
            </div>
          ))}
        </div>
        <textarea
          value={draftContent}
          aria-label="File content"
          readOnly={!canWriteFile}
          spellCheck={false}
          onChange={(event) => setDraftContent(event.target.value)}
          className="h-full min-h-0 w-full resize-none overflow-auto bg-transparent px-3 py-2 leading-5 text-slate-100 caret-primary outline-none placeholder:text-slate-500 read-only:cursor-default read-only:text-slate-300"
          placeholder={hasEditor ? '' : 'No file selected'}
        />
      </div>
      {editorError ? (
        <p role="alert" className="border-t border-destructive/30 bg-destructive/10 px-2 py-1 text-xs text-destructive">
          {editorError}
        </p>
      ) : null}
    </section>
  )
}

export function ProjectStructurePanel({
  snapshot,
  className,
  createDisabled = false,
  writeDisabled = false,
  onCreateFile,
  onWriteFile,
}: ProjectStructurePanelProps) {
  const tree = useMemo(() => buildTree(snapshot), [snapshot])
  const files = useMemo(() => flattenFiles(tree), [tree])
  const fileByPath = useMemo(() => new Map(files.map((file) => [file.path, file])), [files])
  const hasFiles = tree.length > 0
  const [modalOpen, setModalOpen] = useState(false)
  const [path, setPath] = useState('')
  const [content, setContent] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [selectedPath, setSelectedPath] = useState<string | null>(null)
  const canCreateFile = Boolean(onCreateFile) && !createDisabled && !submitting
  const preferredPath = (snapshot.conflicts ?? []).find((conflictPath) => fileByPath.has(conflictPath)) ?? files[0]?.path ?? null
  const activePath = selectedPath && fileByPath.has(selectedPath) ? selectedPath : preferredPath
  const selectedFile = activePath ? fileByPath.get(activePath) : undefined
  const selectedContent = editorContent(selectedFile?.content)
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
    } catch (createError) {
      setError(workspaceFileErrorMessage(createError))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Card className={cn('flex min-h-[18rem] flex-col overflow-hidden shadow-none', className)}>
      <CardHeader className="flex-row items-center justify-between gap-2 p-3">
        <CardTitle className="text-sm">Project Files</CardTitle>
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
      </CardHeader>
      <CardContent className="grid min-h-0 flex-1 grid-rows-[minmax(6rem,0.42fr)_minmax(12rem,0.58fr)] gap-2 p-2 pt-0">
        <div className="min-h-0 overflow-auto rounded-md border border-border/70 bg-background/35 p-1 app-scrollbar">
          {hasFiles ? (
            <div className="pb-1">
              {tree.map((node) => (
                <TreeItem
                  key={node.path}
                  node={node}
                  createDisabled={!canCreateFile}
                  selectedPath={activePath}
                  onAddFile={onCreateFile ? openCreateFileModal : undefined}
                  onSelectFile={setSelectedPath}
                />
              ))}
            </div>
          ) : (
            <p className="px-2 py-1 text-xs text-muted-foreground">No project files yet.</p>
          )}
        </div>

        <FileEditorSection
          key={`${activePath ?? 'none'}:${selectedContent}`}
          selectedPath={activePath}
          selectedFile={selectedFile}
          selectedContent={selectedContent}
          writeDisabled={writeDisabled}
          onWriteFile={onWriteFile}
        />
      </CardContent>
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
