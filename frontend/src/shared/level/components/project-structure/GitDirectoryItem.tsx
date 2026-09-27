import { ChevronDown, ChevronRight, FileText, Folder, FolderOpen, Lock } from 'lucide-react'
import { useState } from 'react'

import type { GitDirectoryNode } from '@/shared/level/utils/gitDirectory'
import { cn } from '@/shared/utils/cn'

/**
 * Git's own folder, shown read-only like an IDE does: collapsed by default,
 * no create/rename/delete, and a file click reveals what Git stored there.
 */
export function GitDirectoryItem({ node, depth = 0 }: { node: GitDirectoryNode; depth?: number }) {
  const [expanded, setExpanded] = useState(false)
  const isDir = node.type === 'directory'
  const isRoot = depth === 0
  const contentId = `git-dir-${node.path.replaceAll('/', '-')}`

  return (
    <div className={cn(isRoot && 'project-tree-git')}>
      <div
        className="project-tree-node flex w-full items-center gap-1.5 rounded-sm px-1 py-0.5 text-left text-xs hover:bg-secondary/60"
        title={isRoot ? 'Git’s internal data, created by git init or git clone. Read-only.' : undefined}
        onContextMenu={(event) => {
          event.preventDefault()
          event.stopPropagation()
        }}
      >
        <button
          type="button"
          className="project-tree-node-label flex min-w-0 flex-1 items-center gap-1.5 text-left"
          aria-expanded={expanded}
          aria-controls={isDir ? undefined : contentId}
          aria-label={isDir ? undefined : `Show ${node.path}`}
          onClick={() => setExpanded((value) => !value)}
        >
          {isDir ? (
            expanded ? (
              <ChevronDown className="size-3 shrink-0 text-muted-foreground" />
            ) : (
              <ChevronRight className="size-3 shrink-0 text-muted-foreground" />
            )
          ) : null}
          {isDir ? (
            expanded ? (
              <FolderOpen className="size-3.5 shrink-0 text-muted-foreground" />
            ) : (
              <Folder className="size-3.5 shrink-0 text-muted-foreground" />
            )
          ) : (
            <FileText className="size-3.5 shrink-0 text-muted-foreground" />
          )}
          <span className="truncate">{node.name}</span>
        </button>
        {isRoot ? <Lock className="size-3 shrink-0 text-muted-foreground" aria-label="Read-only" /> : null}
      </div>
      {expanded && isDir ? (
        <div className="tree-children">
          {node.children.map((child) => (
            <GitDirectoryItem key={child.path} node={child} depth={depth + 1} />
          ))}
          {isRoot ? (
            <p className="project-tree-git__note">objects/, index and hooks/ not shown</p>
          ) : null}
        </div>
      ) : null}
      {expanded && !isDir ? (
        <pre id={contentId} className="project-tree-git__content">
          {node.content}
        </pre>
      ) : null}
    </div>
  )
}
