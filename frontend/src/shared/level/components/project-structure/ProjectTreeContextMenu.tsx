import { ExternalLink, FilePlus, FolderPlus, Pencil, Trash2 } from 'lucide-react'
import type { ReactNode } from 'react'
import { createPortal } from 'react-dom'

import type { ProjectTreeNode } from '@/shared/level/utils/projectFiles'
import { cn } from '@/shared/utils/cn'

export const CONTEXT_MENU_WIDTH = 176
export const CONTEXT_MENU_HEIGHT = 176

export type ProjectTreeContextMenuState = {
  x: number
  y: number
  node: ProjectTreeNode | null
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

export function ProjectTreeContextMenu({
  menu,
  canCreate,
  canRename,
  canDelete,
  onOpenFile,
  onStartCreate,
  onStartRename,
  onDeleteNode,
  onClose,
}: {
  menu: ProjectTreeContextMenuState | null
  canCreate: boolean
  canRename: boolean
  canDelete: boolean
  onOpenFile?: (path: string) => void
  onStartCreate: (parentPath: string, kind: 'file' | 'folder') => void
  onStartRename: (node: ProjectTreeNode) => void
  onDeleteNode: (node: ProjectTreeNode) => void
  onClose: () => void
}) {
  if (!menu) return null

  const contextNode = menu.node
  const contextIsDirectory = !contextNode || contextNode.type === 'directory'

  return createPortal(
    <div
      role="menu"
      className="project-tree-menu"
      style={{ left: menu.x, top: menu.y }}
      onMouseDown={(event) => event.stopPropagation()}
    >
      {contextIsDirectory ? (
        <>
          <MenuItem disabled={!canCreate} onClick={() => onStartCreate(contextNode?.path ?? '', 'file')}>
            <FilePlus aria-hidden="true" />
            New File
          </MenuItem>
          <MenuItem disabled={!canCreate} onClick={() => onStartCreate(contextNode?.path ?? '', 'folder')}>
            <FolderPlus aria-hidden="true" />
            New Folder
          </MenuItem>
        </>
      ) : (
        <MenuItem
          disabled={!onOpenFile}
          onClick={() => {
            if (contextNode) onOpenFile?.(contextNode.path)
            onClose()
          }}
        >
          <ExternalLink aria-hidden="true" />
          Open
        </MenuItem>
      )}
      {contextNode ? (
        <>
          <MenuItem disabled={!canRename} onClick={() => onStartRename(contextNode)}>
            <Pencil aria-hidden="true" />
            Rename
          </MenuItem>
          <MenuItem disabled={!canDelete} tone="danger" onClick={() => onDeleteNode(contextNode)}>
            <Trash2 aria-hidden="true" />
            Delete
          </MenuItem>
        </>
      ) : null}
    </div>,
    document.body,
  )
}
