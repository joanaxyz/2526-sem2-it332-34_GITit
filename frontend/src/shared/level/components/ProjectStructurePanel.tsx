import {
  AlertTriangle,
  ChevronDown,
  ExternalLink,
  FilePlus,
  FolderOpen,
  FolderPlus,
  Pencil,
  Trash2,
} from 'lucide-react'
import type { MouseEvent, ReactNode } from 'react'
import { useEffect, useMemo, useState } from 'react'
import { createPortal } from 'react-dom'

import type { RepositorySnapshot } from '@/shared/level/types'
import {
  buildProjectTree,
  flattenProjectFiles,
  workspaceFileErrorMessage,
} from '@/shared/level/utils/projectFiles'
import type { ProjectTreeNode } from '@/shared/level/utils/projectFiles'
import { Button } from '@/shared/components/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'
import {
  ProjectTreeCreateDraftRow,
  ProjectTreeItem,
} from '@/shared/level/components/project-structure/ProjectTreeItem'
import type { ProjectTreeDraft } from '@/shared/level/components/project-structure/ProjectTreeItem'
import { cn } from '@/shared/utils/cn'

type CreateFileInput = {
  path: string
  content: string
}

type RenameFileInput = {
  path: string
  newPath: string
}

type ProjectStructurePanelProps = {
  snapshot: RepositorySnapshot
  /** Repo folder shown as the tree's synthetic root (the level's slug). */
  rootName?: string
  className?: string
  selectedPath?: string | null
  createDisabled?: boolean
  isOpen?: boolean
  onToggle?: () => void
  onCreateFile?: (input: CreateFileInput) => Promise<unknown> | void
  onRenameFile?: (input: RenameFileInput) => Promise<unknown> | void
  onDeleteFile?: (path: string) => Promise<unknown> | void
  onOpenFile?: (path: string) => void
}

type ContextMenuState = {
  x: number
  y: number
  node: ProjectTreeNode | null
}

function parentPathFor(path: string) {
  return path.split('/').slice(0, -1).join('/')
}

function cleanPathPart(value: string) {
  return value.trim().replaceAll('\\', '/').replace(/^\/+/, '').replace(/\/+$/, '')
}

function joinProjectPath(parentPath: string, value: string) {
  const clean = cleanPathPart(value)
  return parentPath ? `${parentPath}/${clean}` : clean
}

function placeholderPathForFolder(folderPath: string) {
  return `${folderPath}/.gitkeep`
}

function draftError(error: unknown, fallback: string) {
  return workspaceFileErrorMessage(error, fallback)
}

function MenuItem({
  children,
  tone = 'default',
  disabled,
  onClick,
}: {
  children: ReactNode
  tone?: 'default' | 'danger'
  disabled?: boolean
  onClick: () => void
}) {
  return (
    <button
      type="button"
      role="menuitem"
      disabled={disabled}
      className={cn('project-tree-menu__item', tone === 'danger' && 'is-danger')}
      onClick={onClick}
    >
      {children}
    </button>
  )
}

const CONTEXT_MENU_WIDTH = 176
const CONTEXT_MENU_HEIGHT = 176

export function ProjectStructurePanel({
  snapshot,
  rootName,
  className,
  selectedPath,
  createDisabled = false,
  isOpen = true,
  onToggle,
  onCreateFile,
  onRenameFile,
  onDeleteFile,
  onOpenFile,
}: ProjectStructurePanelProps) {
  const tree = useMemo(() => buildProjectTree(snapshot), [snapshot])
  const files = useMemo(() => flattenProjectFiles(tree), [tree])
  const filePaths = useMemo(() => new Set(files.map((file) => file.path)), [files])
  const hasFiles = tree.length > 0
  const [draft, setDraft] = useState<ProjectTreeDraft | null>(null)
  const [menu, setMenu] = useState<ContextMenuState | null>(null)
  const [panelError, setPanelError] = useState('')
  const actionDisabled = createDisabled || Boolean(draft?.submitting)
  const canCreate = Boolean(onCreateFile) && !actionDisabled
  const canRename = Boolean(onRenameFile) && !actionDisabled
  const canDelete = Boolean(onDeleteFile) && !actionDisabled
  const firstConflictPath = (snapshot.conflicts ?? []).find((conflictPath) => filePaths.has(conflictPath))

  useEffect(() => {
    if (!menu) return

    function closeMenu() {
      setMenu(null)
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') closeMenu()
    }

    window.addEventListener('click', closeMenu)
    window.addEventListener('keydown', handleKeyDown)
    return () => {
      window.removeEventListener('click', closeMenu)
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [menu])

  function startCreate(parentPath = '', kind: 'file' | 'folder') {
    if (!onCreateFile || actionDisabled) return
    setMenu(null)
    setPanelError('')
    setDraft({
      mode: 'create',
      kind,
      parentPath,
      value: kind === 'file' ? 'untitled.txt' : 'new-folder',
      error: '',
      submitting: false,
    })
  }

  function startRename(node: ProjectTreeNode) {
    if (!onRenameFile || actionDisabled) return
    setMenu(null)
    setPanelError('')
    setDraft({
      mode: 'rename',
      nodePath: node.path,
      value: node.name,
      error: '',
      submitting: false,
    })
  }

  async function commitDraft() {
    if (!draft || draft.submitting) return

    const nextName = cleanPathPart(draft.value)
    if (!nextName) {
      setDraft({ ...draft, error: 'Name is required.' })
      return
    }

    setDraft({ ...draft, value: nextName, error: '', submitting: true })
    try {
      if (draft.mode === 'create') {
        if (!onCreateFile) return
        const targetPath = joinProjectPath(draft.parentPath, nextName)
        const filePath = draft.kind === 'folder' ? placeholderPathForFolder(targetPath) : targetPath
        await onCreateFile({ path: filePath, content: '' })
      } else {
        if (!onRenameFile) return
        const nextPath = joinProjectPath(parentPathFor(draft.nodePath), nextName)
        await onRenameFile({ path: draft.nodePath, newPath: nextPath })
      }
      setDraft(null)
    } catch (error) {
      setDraft((current) => (
        current
          ? {
              ...current,
              submitting: false,
              error: draftError(error, draft.mode === 'create' ? 'Could not create this item.' : 'Could not rename this item.'),
            }
          : current
      ))
    }
  }

  function cancelDraft() {
    if (draft?.submitting) return
    setDraft(null)
  }

  function openContextMenu(node: ProjectTreeNode | null, event: MouseEvent<HTMLElement>) {
    event.preventDefault()
    event.stopPropagation()
    const viewportWidth = window.innerWidth || document.documentElement.clientWidth
    const viewportHeight = window.innerHeight || document.documentElement.clientHeight
    setMenu({
      node,
      x: Math.max(8, Math.min(event.clientX, viewportWidth - CONTEXT_MENU_WIDTH - 8)),
      y: Math.max(8, Math.min(event.clientY, viewportHeight - CONTEXT_MENU_HEIGHT - 8)),
    })
  }

  async function deleteNode(node: ProjectTreeNode) {
    if (!onDeleteFile || actionDisabled) return
    setMenu(null)
    setPanelError('')
    const targetLabel = node.type === 'directory' ? `${node.path}/` : node.path
    if (!window.confirm(`Delete ${targetLabel}?`)) return

    try {
      await onDeleteFile(node.path)
      if (draft?.mode === 'rename' && (draft.nodePath === node.path || draft.nodePath.startsWith(`${node.path}/`))) {
        setDraft(null)
      }
    } catch (error) {
      setPanelError(draftError(error, 'Could not delete this item.'))
    }
  }

  const rootCreateDraft = draft?.mode === 'create' && draft.parentPath === '' ? draft : null
  const contextNode = menu?.node ?? null
  const contextIsDirectory = !contextNode || contextNode.type === 'directory'

  return (
    <Card
      className={cn('flex flex-col overflow-hidden shadow-none', isOpen && 'min-h-[18rem]', className)}
      style={{ borderTop: '1.5px solid rgba(var(--theme-primary-rgb),0.42)' }}
    >
      <CardHeader
        className="flex-row items-center justify-between gap-2 px-4 py-3"
        style={{ background: 'rgba(var(--theme-primary-rgb),0.025)' }}
      >
        <CardTitle className="panel-eyebrow">Project Files</CardTitle>
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
            <>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="size-7 rounded-sm"
                title="New file"
                aria-label="New file"
                disabled={!canCreate}
                onClick={() => startCreate('', 'file')}
              >
                <FilePlus className="size-4" />
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="size-7 rounded-sm"
                title="New folder"
                aria-label="New folder"
                disabled={!canCreate}
                onClick={() => startCreate('', 'folder')}
              >
                <FolderPlus className="size-4" />
              </Button>
            </>
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
      {isOpen ? (
        <CardContent className="min-h-0 flex-1 p-2 pt-1">
          <div className="h-full min-h-0 overflow-auto app-scrollbar">
            <div className="pb-1">
              <div
                className="project-tree-node flex w-full items-center gap-1.5 rounded-sm px-1 py-0.5 text-left text-xs font-medium text-foreground"
                onContextMenu={(event) => {
                  event.preventDefault()
                  openContextMenu(null, event)
                }}
              >
                <ChevronDown className="size-3 shrink-0 text-muted-foreground" />
                <FolderOpen className="size-3.5 shrink-0 text-primary" />
                <span className="min-w-0 flex-1 truncate">{rootName || 'repo'}</span>
              </div>
              <div className="tree-children">
                {rootCreateDraft ? (
                  <ProjectTreeCreateDraftRow
                    draft={rootCreateDraft}
                    onDraftChange={(value) => setDraft((current) => current ? { ...current, value, error: '' } : current)}
                    onCommitDraft={commitDraft}
                    onCancelDraft={cancelDraft}
                  />
                ) : null}
                {hasFiles ? (
                  tree.map((node) => (
                    <ProjectTreeItem
                      key={node.path}
                      node={node}
                      createDisabled={actionDisabled}
                      selectedPath={selectedPath}
                      draft={draft}
                      onStartCreate={startCreate}
                      onDraftChange={(value) => setDraft((current) => current ? { ...current, value, error: '' } : current)}
                      onCommitDraft={commitDraft}
                      onCancelDraft={cancelDraft}
                      onOpenContextMenu={openContextMenu}
                      onStartRename={startRename}
                      onDeleteNode={deleteNode}
                      renameDisabled={!canRename}
                      deleteDisabled={!canDelete}
                      onOpenFile={onOpenFile}
                    />
                  ))
                ) : rootCreateDraft ? null : (
                  <p className="px-2 py-1 text-xs text-muted-foreground">No project files yet.</p>
                )}
              </div>
              {panelError ? (
                <p role="alert" className="project-tree-panel-error">
                  {panelError}
                </p>
              ) : null}
            </div>
          </div>
        </CardContent>
      ) : null}
      {menu ? createPortal(
        <div
          role="menu"
          className="project-tree-menu"
          style={{ left: menu.x, top: menu.y }}
          onMouseDown={(event) => event.stopPropagation()}
        >
          {contextIsDirectory ? (
            <>
              <MenuItem disabled={!canCreate} onClick={() => startCreate(contextNode?.path ?? '', 'file')}>
                <FilePlus aria-hidden="true" />
                New File
              </MenuItem>
              <MenuItem disabled={!canCreate} onClick={() => startCreate(contextNode?.path ?? '', 'folder')}>
                <FolderPlus aria-hidden="true" />
                New Folder
              </MenuItem>
            </>
          ) : (
            <MenuItem
              disabled={!onOpenFile}
              onClick={() => {
                if (contextNode) onOpenFile?.(contextNode.path)
                setMenu(null)
              }}
            >
              <ExternalLink aria-hidden="true" />
              Open
            </MenuItem>
          )}
          {contextNode ? (
            <>
              <MenuItem disabled={!canRename} onClick={() => startRename(contextNode)}>
                <Pencil aria-hidden="true" />
                Rename
              </MenuItem>
              <MenuItem disabled={!canDelete} tone="danger" onClick={() => void deleteNode(contextNode)}>
                <Trash2 aria-hidden="true" />
                Delete
              </MenuItem>
            </>
          ) : null}
        </div>,
        document.body,
      ) : null}
    </Card>
  )
}
