import type { RepositorySnapshot, RepositoryValue } from '@/shared/level/types'
import { ApiError } from '@/shared/api/apiError'

export type ProjectTreeNode = {
  name: string
  path: string
  type: 'file' | 'directory'
  status?: string
  source?: 'head' | 'staging' | 'working_tree'
  content?: RepositoryValue
  conflict?: boolean
  children: ProjectTreeNode[]
}

export type WorkspaceFileInput = {
  path: string
  content: string
}

export function buildProjectTree(snapshot: RepositorySnapshot): ProjectTreeNode[] {
  const root: ProjectTreeNode = { name: '', path: '', type: 'directory', children: [] }
  const conflictPaths = new Set(snapshot.conflicts ?? [])

  const addPath = (filePath: string, status: RepositoryValue, source: 'head' | 'staging' | 'working_tree') => {
    const parts = filePath.split('/')
    let current = root

    parts.forEach((part, index) => {
      const isFile = index === parts.length - 1
      const fullPath = parts.slice(0, index + 1).join('/')
      const existing = current.children.find((child) => child.name === part)

      if (existing) {
        if (isFile) {
          existing.status = statusLabel(status)
          existing.source = source
          existing.content = contentValue(status)
          existing.conflict = conflictPaths.has(filePath)
        }
        current = existing
        return
      }

      const node: ProjectTreeNode = {
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
      current.children.sort((left, right) => {
        if (left.type === right.type) return left.name.localeCompare(right.name)
        return left.type === 'directory' ? -1 : 1
      })
      current = node
    })
  }

  const visibleTree = snapshot.project_tree ?? snapshot.visible_tree
  if (visibleTree && Object.keys(visibleTree).length > 0) {
    Object.entries(visibleTree).forEach(([path, value]) => {
      addPath(path, value, sourceLabel(value))
    })
  } else {
    Object.entries(snapshot.staging).forEach(([path, status]) => addPath(path, status, 'staging'))
    Object.entries(snapshot.working_tree).forEach(([path, status]) => addPath(path, status, 'working_tree'))
  }

  return root.children
}

export function flattenProjectFiles(nodes: ProjectTreeNode[]) {
  const files: ProjectTreeNode[] = []
  nodes.forEach((node) => {
    if (node.type === 'file') files.push(node)
    files.push(...flattenProjectFiles(node.children))
  })
  return files
}

export function statusLabel(value: RepositoryValue) {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    const status = value.status
    if (typeof status === 'string') return status
  }
  return String(value ?? 'changed')
}

export function sourceLabel(value: RepositoryValue): 'head' | 'staging' | 'working_tree' {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    const source = value.source
    if (source === 'staging' || source === 'working_tree' || source === 'head') return source
  }
  return 'head'
}

export function contentValue(value: RepositoryValue): RepositoryValue {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    if ('content' in value) return value.content
    if ('after' in value) return value.after
    if ('value' in value) return value.value
  }
  return value
}

export function editorContent(value: RepositoryValue | undefined) {
  if (value === undefined || value === null) return ''
  return typeof value === 'string' ? value : JSON.stringify(value, null, 2)
}

export function lineNumbersFor(value: string, minimum = 8) {
  const lineCount = Math.max(minimum, value.split('\n').length)
  return Array.from({ length: lineCount }, (_, index) => index + 1)
}

export function workspaceFileErrorMessage(error: unknown, fallback = 'Could not update the file.') {
  if (error instanceof ApiError && error.payload && typeof error.payload === 'object') {
    const payload = error.payload as Record<string, unknown>
    const pathErrors = payload.path
    if (Array.isArray(pathErrors) && pathErrors.length > 0) return String(pathErrors[0])
    if (typeof pathErrors === 'string') return pathErrors
  }
  if (error instanceof Error && error.message) return error.message
  return fallback
}
