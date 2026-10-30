import type { RepositorySnapshot } from '@/shared/level/types'

/**
 * What the repository graph draws: initialization, commits and their parents,
 * local and remote refs, and HEAD. Working-tree and staging changes are left
 * out because the graph does not show them.
 */
export function repositoryGraphSignature(snapshot: RepositorySnapshot) {
  return JSON.stringify([
    snapshot.repository_initialized ?? null,
    (snapshot.commits ?? []).map((commit) => [commit.id, commit.parents]),
    snapshot.branches ?? {},
    snapshot.remote_branches ?? {},
    snapshot.head ?? null,
  ])
}
