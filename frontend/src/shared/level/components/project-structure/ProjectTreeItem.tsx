import {
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  FilePlus,
  FileText,
  Folder,
  FolderOpen,
  FolderPlus,
  Pencil,
  Trash2,
} from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import type { KeyboardEvent, MouseEvent } from 'react'

import type { ProjectTreeNode } from '@/shared/level/utils/projectFiles'
import { cn } from '@/shared/utils/cn'

export type ProjectTreeDraft =
  | {
      mode: 'create'
      kind: 'file' | 'folder'
      parentPath: string
      value: string
      error: string
      submitting: boolean
    }
  | {
      mode: 'rename'
      nodePath: string
      value: string
      error: string
      submitting: boolean
    }

type ProjectTreeItemProps = {
  node: ProjectTreeNode
  depth?: number
  createDisabled?: boolean
  selectedPath?: string | null
  draft?: ProjectTreeDraft | null
  onStartCreate?: (directoryPath: string, kind: 'file' | 'folder') => void
  onDraftChange?: (value: string) => void
  onCommitDraft?: () => void
  onCancelDraft?: () => void
  onOpenContextMenu?: (node: ProjectTreeNode, event: MouseEvent<HTMLElement>) => void
  onStartRename?: (node: ProjectTreeNode) => void
  onDeleteNode?: (node: ProjectTreeNode) => void | Promise<void>
  renameDisabled?: boolean
  deleteDisabled?: boolean
  onOpenFile?: (filePath: string) => void
}

function InlineTreeInput({
  value,
  label,
  error,
  submitting,
  onChange,
  onCommit,
  onCancel,
}: {
  value: string
  label: string
  error: string
  submitting: boolean
  onChange?: (value: string) => void
  onCommit?: () => void
  onCancel?: () => void
}) {
  const inputRef = useRef<HTMLInputElement | null>(null)

  useEffect(() => {
    inputRef.current?.focus()
    inputRef.current?.select()
  }, [])

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'Enter') {
      event.preventDefault()
      onCommit?.()
    } else if (event.key === 'Escape') {
      event.preventDefault()
      onCancel?.()
    }
  }

  return (
    <span className="project-tree-inline">
      <input
        ref={inputRef}
        aria-label={label}
        value={value}
        disabled={submitting}
        spellCheck={false}
        className="project-tree-inline__input"
        onChange={(event) => onChange?.(event.target.value)}
        onKeyDown={handleKeyDown}
      />
      {error ? (
        <span role="alert" className="project-tree-inline__error">
          {error}
        </span>
      ) : null}
    </span>
  )
}

function TreeNodeIcon({ isDir, expanded }: { isDir: boolean; expanded: boolean }) {
  if (isDir) {
    return expanded ? (
      <FolderOpen className="size-3.5 shrink-0 text-primary" />
    ) : (
      <Folder className="size-3.5 shrink-0 text-primary" />
    )
  }
  return <FileText className="size-3.5 shrink-0 text-muted-foreground" />
}

export function ProjectTreeCreateDraftRow({
  draft,
  onDraftChange,
  onCommitDraft,
  onCancelDraft,
}: {
  draft: Extract<ProjectTreeDraft, { mode: 'create' }>
  onDraftChange?: (value: string) => void
  onCommitDraft?: () => void
  onCancelDraft?: () => void
}) {
  return (
    <div className="project-tree-draft-row">
      {draft.kind === 'folder' ? (
        <Folder className="size-3.5 shrink-0 text-primary" />
      ) : (
        <FileText className="size-3.5 shrink-0 text-muted-foreground" />
      )}
      <InlineTreeInput
        value={draft.value}
        label={`New ${draft.kind} name`}
        error={draft.error}
        submitting={draft.submitting}
        onChange={onDraftChange}
        onCommit={onCommitDraft}
        onCancel={onCancelDraft}
      />
    </div>
  )
}

export function ProjectTreeItem({
  node,
  depth = 0,
  createDisabled = false,
  selectedPath,
  draft,
  onStartCreate,
  onDraftChange,
  onCommitDraft,
  onCancelDraft,
  onOpenContextMenu,
  onStartRename,
  onDeleteNode,
  renameDisabled = false,
  deleteDisabled = false,
  onOpenFile,
}: ProjectTreeItemProps) {
  const [expanded, setExpanded] = useState(true)
  const isDir = node.type === 'directory'
  const isSelected = !isDir && selectedPath === node.path
  const isRenaming = draft?.mode === 'rename' && draft.nodePath === node.path
  const childCreateDraft = isDir && draft?.mode === 'create' && draft.parentPath === node.path ? draft : null
  // Hierarchy depth is drawn by the .tree-children guide rails, not padding.
  const indent = '4px'

  return (
    <div>
      <div
        className={cn(
          'project-tree-node flex w-full items-center gap-1.5 rounded-sm px-1 py-0.5 text-left text-xs',
          isDir ? 'font-medium text-foreground hover:bg-secondary' : 'text-muted-foreground hover:bg-secondary/60',
          isSelected && 'bg-primary/10 text-foreground ring-1 ring-primary/30',
        )}
        style={{ paddingLeft: indent }}
        onContextMenu={(event) => {
          event.preventDefault()
          onOpenContextMenu?.(node, event)
        }}
      >
        {isRenaming ? (
          <div className="flex min-w-0 flex-1 items-center gap-1.5 text-left">
            {isDir ? (
              expanded ? (
                <ChevronDown className="size-3 shrink-0 text-muted-foreground" />
              ) : (
                <ChevronRight className="size-3 shrink-0 text-muted-foreground" />
              )
            ) : null}
            <TreeNodeIcon isDir={isDir} expanded={expanded} />
            <InlineTreeInput
              value={draft.value}
              label={`Rename ${node.path}`}
              error={draft.error}
              submitting={draft.submitting}
              onChange={onDraftChange}
              onCommit={onCommitDraft}
              onCancel={onCancelDraft}
            />
          </div>
        ) : (
          <button
            type="button"
            className="project-tree-node-label flex min-w-0 flex-1 items-center gap-1.5 text-left"
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
                <ChevronDown className="size-3 shrink-0 text-muted-foreground" />
              ) : (
                <ChevronRight className="size-3 shrink-0 text-muted-foreground" />
              )
            ) : null}
            <TreeNodeIcon isDir={isDir} expanded={expanded} />
            <span className="truncate">{node.name}</span>
          </button>
        )}

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
              'shrink-0 rounded px-1 text-[11px] font-medium uppercase leading-none',
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
            className="project-tree-action grid size-5 shrink-0 place-items-center rounded-sm text-muted-foreground hover:bg-background hover:text-foreground"
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
        {isDir && onStartCreate ? (
          <>
            <button
              type="button"
              className="project-tree-action grid size-5 shrink-0 place-items-center rounded-sm text-muted-foreground hover:bg-background hover:text-foreground disabled:pointer-events-none disabled:opacity-50"
              title={`New file in ${node.path}`}
              aria-label={`New file in ${node.path}`}
              disabled={createDisabled}
              onClick={(event) => {
                event.stopPropagation()
                setExpanded(true)
                onStartCreate(node.path, 'file')
              }}
            >
              <FilePlus className="size-3.5" />
            </button>
            <button
              type="button"
              className="project-tree-action grid size-5 shrink-0 place-items-center rounded-sm text-muted-foreground hover:bg-background hover:text-foreground disabled:pointer-events-none disabled:opacity-50"
              title={`New folder in ${node.path}`}
              aria-label={`New folder in ${node.path}`}
              disabled={createDisabled}
              onClick={(event) => {
                event.stopPropagation()
                setExpanded(true)
                onStartCreate(node.path, 'folder')
              }}
            >
              <FolderPlus className="size-3.5" />
            </button>
          </>
        ) : null}
        {!isRenaming && onStartRename ? (
          <button
            type="button"
            className="project-tree-action grid size-5 shrink-0 place-items-center rounded-sm text-muted-foreground hover:bg-background hover:text-foreground disabled:pointer-events-none disabled:opacity-50"
            title={`Rename ${node.path}`}
            aria-label={`Rename ${node.path}`}
            disabled={renameDisabled}
            onClick={(event) => {
              event.stopPropagation()
              onStartRename(node)
            }}
          >
            <Pencil className="size-3" />
          </button>
        ) : null}
        {!isRenaming && onDeleteNode ? (
          <button
            type="button"
            className="project-tree-action project-tree-action--danger grid size-5 shrink-0 place-items-center rounded-sm text-muted-foreground hover:bg-destructive/10 hover:text-destructive disabled:pointer-events-none disabled:opacity-50"
            title={`Delete ${node.path}`}
            aria-label={`Delete ${node.path}`}
            disabled={deleteDisabled}
            onClick={(event) => {
              event.stopPropagation()
              void onDeleteNode(node)
            }}
          >
            <Trash2 className="size-3" />
          </button>
        ) : null}
      </div>
      {isDir && expanded ? (
        <div className="tree-children">
          {childCreateDraft ? (
            <ProjectTreeCreateDraftRow
              draft={childCreateDraft}
              onDraftChange={onDraftChange}
              onCommitDraft={onCommitDraft}
              onCancelDraft={onCancelDraft}
            />
          ) : null}
          {node.children.map((child) => (
            <ProjectTreeItem
              key={child.path}
              node={child}
              depth={depth + 1}
              createDisabled={createDisabled}
              selectedPath={selectedPath}
              draft={draft}
              onStartCreate={onStartCreate}
              onDraftChange={onDraftChange}
              onCommitDraft={onCommitDraft}
              onCancelDraft={onCancelDraft}
              onOpenContextMenu={onOpenContextMenu}
              onStartRename={onStartRename}
              onDeleteNode={onDeleteNode}
              renameDisabled={renameDisabled}
              deleteDisabled={deleteDisabled}
              onOpenFile={onOpenFile}
            />
          ))}
        </div>
      ) : null}
    </div>
  )
}
