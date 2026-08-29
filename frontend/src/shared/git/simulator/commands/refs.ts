import { commitById, headCommit, isRecord } from '@/shared/git/simulator/state'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'

export function resolveRef(state: MutableRepositoryState, ref?: string | null): string | null {
  if (!ref || ref === 'HEAD') return headCommit(state)
  if (ref in (state.branches ?? {})) return state.branches?.[ref] ?? null
  if (ref in (state.remote_branches ?? {})) return state.remote_branches?.[ref] ?? null
  if (ref in (state.tags ?? {})) {
    const tag = state.tags?.[ref]
    return isRecord(tag) ? String(tag.target ?? '') : String(tag)
  }
  if (commitById(state, ref)) return ref
  return null
}

export function resolveRevision(state: MutableRepositoryState, revision: string) {
  if (revision === 'HEAD') return headCommit(state)
  if (revision.startsWith('HEAD~')) {
    const depth = Number(revision.slice(5))
    if (!Number.isInteger(depth)) return null
    let current = headCommit(state)
    for (let index = 0; index < depth; index += 1) {
      const commit = commitById(state, current)
      current = commit?.parents?.[0] ?? null
      if (!current) return null
    }
    return current
  }
  if (revision.startsWith('HEAD@{') && revision.endsWith('}')) {
    const index = Number(revision.slice(6, -1))
    const entry = state.reflog?.[index]
    return typeof entry?.target === 'string' ? entry.target : null
  }
  return resolveRef(state, revision)
}

export function commonAncestor(state: MutableRepositoryState, left?: string | null, right?: string | null) {
  const rightHistory = new Set(history(state, right))
  return history(state, left).find((commitId) => rightHistory.has(commitId)) ?? null
}

export function isAncestor(state: MutableRepositoryState, ancestor?: string | null, descendant?: string | null) {
  return Boolean(ancestor && history(state, descendant).includes(ancestor))
}

export function history(state: MutableRepositoryState, commitId?: string | null) {
  const commits = new Map((state.commits ?? []).map((commit) => [commit.id, commit]))
  const stack = commitId ? [commitId] : []
  const seen: string[] = []
  while (stack.length) {
    const current = stack.pop()!
    if (seen.includes(current) || !commits.has(current)) continue
    seen.push(current)
    stack.push(...(commits.get(current)?.parents ?? []))
  }
  return seen
}

export function commitsSince(state: MutableRepositoryState, commitId?: string | null, stopAt?: string | null) {
  const result: string[] = []
  let current = commitId
  while (current && current !== stopAt) {
    result.push(current)
    current = commitById(state, current)?.parents?.[0] ?? null
  }
  return result
}
