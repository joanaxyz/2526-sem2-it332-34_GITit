import type { RepositorySnapshot, RepositoryValue } from '@/shared/level/types'

/**
 * Read-only `.git/` view derived from repository state. It shows the files a
 * learner can reason about (HEAD, config, refs, in-progress markers) with the
 * contents real Git would write; the object database and index are left out.
 */
export type GitDirectoryNode = {
  name: string
  path: string
  type: 'file' | 'directory'
  content?: string
  children: GitDirectoryNode[]
}

type RepositoryFolderSource = Pick<RepositorySnapshot, 'operation_metadata'>

/**
 * Folder the repository lives in: the `git clone <url> <dir>` / `git init <dir>`
 * destination once one was named, else `fallback` (the level's project folder).
 * The simulator keeps one repository at the project root, so that folder is
 * the root the learner is standing in.
 */
export function repositoryFolderName(state: RepositoryFolderSource, fallback: string) {
  const metadata = state.operation_metadata ?? {}
  for (const value of [metadata.last_clone_directory, metadata.last_init_directory]) {
    const name = typeof value === 'string' ? value.replace(/\/+$/, '').split('/').at(-1) : ''
    if (name && name !== '.') return name
  }
  return fallback
}

export function buildGitDirectory(snapshot: RepositorySnapshot): GitDirectoryNode | null {
  if (!snapshot.repository_initialized) return null
  const root: GitDirectoryNode = { name: '.git', path: '.git', type: 'directory', children: [] }
  const add = (path: string, content: string) => addFile(root, path, content)

  add('HEAD', headContent(snapshot))
  add('config', configContent(snapshot))
  if (snapshot.merge_parent) add('MERGE_HEAD', `${snapshot.merge_parent}\n`)
  if (snapshot.operation_metadata?.last_clone_shallow === true) {
    const boundaries = snapshot.commits.filter((commit) => !commit.parents?.length).map((commit) => commit.id)
    if (boundaries.length) add('shallow', `${boundaries.join('\n')}\n`)
  }

  Object.entries(snapshot.branches ?? {}).forEach(([branch, target]) => {
    if (target) add(`refs/heads/${branch}`, `${target}\n`)
  })
  Object.entries(snapshot.remote_branches ?? {}).forEach(([ref, target]) => {
    if (target && ref.includes('/')) add(`refs/remotes/${ref}`, `${target}\n`)
  })
  const cloneBranch = snapshot.operation_metadata?.last_clone_branch
  if (snapshot.operation_metadata?.last_clone_url && typeof cloneBranch === 'string' && snapshot.remotes?.origin) {
    add('refs/remotes/origin/HEAD', `ref: refs/remotes/origin/${cloneBranch}\n`)
  }
  Object.entries(snapshot.tags ?? {}).forEach(([tag, value]) => {
    const target = tagTarget(value)
    if (target) add(`refs/tags/${tag}`, `${target}\n`)
  })
  // Git always creates these, even before the first commit.
  ensureDirectory(root, 'refs/heads')
  ensureDirectory(root, 'refs/tags')

  sortTree(root)
  return root
}

function headContent(snapshot: RepositorySnapshot) {
  if (snapshot.head?.type === 'detached') return `${snapshot.head.target ?? ''}\n`
  return `ref: refs/heads/${snapshot.head?.name ?? 'main'}\n`
}

function configContent(snapshot: RepositorySnapshot) {
  const lines = ['[core]', '\trepositoryformatversion = 0', '\tfilemode = true', '\tbare = false']
  Object.entries(snapshot.remotes ?? {}).forEach(([remote, url]) => {
    lines.push(`[remote "${remote}"]`, `\turl = ${url}`, `\tfetch = +refs/heads/*:refs/remotes/${remote}/*`)
  })
  Object.entries(snapshot.upstream_tracking ?? {}).forEach(([branch, upstream]) => {
    const [remote, ...rest] = String(upstream).split('/')
    if (!remote || !rest.length) return
    lines.push(`[branch "${branch}"]`, `\tremote = ${remote}`, `\tmerge = refs/heads/${rest.join('/')}`)
  })
  return `${lines.join('\n')}\n`
}

function tagTarget(value: RepositoryValue) {
  if (typeof value === 'string') return value
  if (value && typeof value === 'object' && !Array.isArray(value) && typeof value.target === 'string') {
    return value.target
  }
  return null
}

function ensureDirectory(root: GitDirectoryNode, relativePath: string) {
  let current = root
  for (const part of relativePath.split('/')) {
    let next = current.children.find((child) => child.name === part && child.type === 'directory')
    if (!next) {
      next = { name: part, path: `${current.path}/${part}`, type: 'directory', children: [] }
      current.children.push(next)
    }
    current = next
  }
  return current
}

function addFile(root: GitDirectoryNode, relativePath: string, content: string) {
  const parts = relativePath.split('/')
  const name = parts.pop() ?? relativePath
  const parent = parts.length ? ensureDirectory(root, parts.join('/')) : root
  parent.children.push({ name, path: `${parent.path}/${name}`, type: 'file', content, children: [] })
}

function sortTree(node: GitDirectoryNode) {
  node.children.sort((left, right) => {
    if (left.type !== right.type) return left.type === 'directory' ? -1 : 1
    return left.name.localeCompare(right.name)
  })
  node.children.forEach(sortTree)
}
