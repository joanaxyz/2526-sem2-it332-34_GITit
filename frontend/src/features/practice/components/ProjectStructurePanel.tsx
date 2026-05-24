import { FileText, Folder, FolderOpen } from 'lucide-react'
import { useMemo, useState } from 'react'

import type { RepositorySnapshot, RepositoryValue } from '@/features/practice/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'
import { cn } from '@/shared/utils/cn'

type TreeNode = {
  name: string
  path: string
  type: 'file' | 'directory'
  status?: string
  source?: 'head' | 'staging' | 'working_tree'
  children: TreeNode[]
}

function buildTree(snapshot: RepositorySnapshot): TreeNode[] {
  const root: TreeNode = { name: '', path: '', type: 'directory', children: [] }

  const addPath = (filePath: string, status: RepositoryValue, source: 'head' | 'staging' | 'working_tree') => {
    const parts = filePath.split('/')
    let current = root

    parts.forEach((part, index) => {
      const isFile = index === parts.length - 1
      const fullPath = parts.slice(0, index + 1).join('/')
      const existing = current.children.find((c) => c.name === part)

      if (existing) {
        current = existing
      } else {
        const node: TreeNode = {
          name: part,
          path: fullPath,
          type: isFile ? 'file' : 'directory',
          status: isFile ? statusLabel(status) : undefined,
          source: isFile ? source : undefined,
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

function TreeItem({ node, depth = 0 }: { node: TreeNode; depth?: number }) {
  const [expanded, setExpanded] = useState(true)
  const isDir = node.type === 'directory'

  return (
    <div>
      <button
        type="button"
        onClick={() => isDir && setExpanded((v) => !v)}
        className={cn(
          'flex w-full items-center gap-1.5 rounded-sm px-1 py-0.5 text-left text-xs',
          isDir ? 'font-medium text-foreground hover:bg-secondary' : 'text-muted-foreground hover:bg-secondary/60'
        )}
        style={{ paddingLeft: `${depth * 12 + 4}px` }}
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
        {node.status && node.status !== 'clean' && (
          <span
            className={cn(
              'ml-auto shrink-0 rounded px-1 text-[10px] font-medium uppercase leading-none',
              node.source === 'staging'
                ? 'bg-primary/10 text-primary'
                : 'bg-muted text-muted-foreground'
            )}
            title={node.source === 'staging' ? 'Staged' : node.source === 'working_tree' ? 'Working tree' : 'Committed'}
          >
            {node.status}
          </span>
        )}
      </button>
      {isDir && expanded && (
        <div>
          {node.children.map((child) => (
            <TreeItem key={child.path} node={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  )
}

export function ProjectStructurePanel({ snapshot, className }: { snapshot: RepositorySnapshot; className?: string }) {
  const tree = useMemo(() => buildTree(snapshot), [snapshot])
  const hasFiles = tree.length > 0

  return (
    <Card className={cn('flex min-h-[14rem] flex-col overflow-hidden shadow-none', className)}>
      <CardHeader className="p-3">
        <CardTitle className="text-sm">Project Structure</CardTitle>
      </CardHeader>
      <CardContent className="min-h-0 flex-1 overflow-auto p-2 pt-0">
        {hasFiles ? (
          <div className="pb-2">
            {tree.map((node) => (
              <TreeItem key={node.path} node={node} />
            ))}
          </div>
        ) : (
          <p className="text-xs text-muted-foreground">No project files yet.</p>
        )}
      </CardContent>
    </Card>
  )
}
