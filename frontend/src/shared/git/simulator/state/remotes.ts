import type { RepositoryCommit } from '@/shared/level/types'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'
import { clone, commitById, isRecord, normalizeCommits } from '@/shared/git/simulator/state/core'

export function applyRemoteFixtureBranches(state: MutableRepositoryState) {
  const fixture = isRecord(state.remote_fixtures) ? state.remote_fixtures : {}
  state.remote_branches ??= {}
  const branchTargets: Record<string, string | null> = {}
  if (isRecord(fixture.branches)) {
    Object.assign(branchTargets, fixture.branches)
  }
  for (const [key, value] of Object.entries(fixture)) {
    if (['commits', 'branches', 'remote_head', 'head', 'default_branch'].includes(key)) continue
    if (key.includes('/') && value) branchTargets[key] = String(value)
  }
  const remoteHead = fixture.remote_head ?? fixture.head
  const defaultBranch = String(fixture.default_branch ?? 'origin/main')
  if (remoteHead) branchTargets[defaultBranch] ??= String(remoteHead)
  for (const [branch, target] of Object.entries(branchTargets)) {
    state.remote_branches[branch] = target
  }
}

export function materializeRemoteCommits(state: MutableRepositoryState) {
  state.commits ??= []
  const existing = new Set(state.commits.map((commit) => commit.id))
  const fixture = isRecord(state.remote_fixtures) ? state.remote_fixtures : {}
  const fixtureCommits = Array.isArray(fixture.commits) ? fixture.commits : []
  for (const authored of fixtureCommits) {
    if (!isRecord(authored) || !authored.id) continue
    const commitId = String(authored.id)
    const existingCommit = commitById(state, commitId)
    if (existingCommit) Object.assign(existingCommit, clone(authored))
    else {
      state.commits.push(clone(authored) as RepositoryCommit)
      existing.add(commitId)
    }
  }
  normalizeCommits(state)
  const remoteIds = [...new Set(Object.values(state.remote_branches ?? {}).filter(Boolean) as string[])].sort()
  let previous: string | null = null
  for (const commitId of remoteIds) {
    if (!existing.has(commitId)) {
      state.commits.push({
        id: commitId,
        message: `Remote commit ${commitId}`,
        parents: previous ? [previous] : [],
        tree: {},
        changes: {},
        files: {},
        is_merge: false,
      })
      existing.add(commitId)
    }
    previous = commitId
  }
  normalizeCommits(state)
}
