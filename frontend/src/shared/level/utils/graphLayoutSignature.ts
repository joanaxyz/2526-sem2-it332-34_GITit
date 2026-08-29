import type { RepositorySnapshot } from '@/shared/level/types'

export function graphLayoutSignature(snapshot: RepositorySnapshot): string {
  if (!snapshot.commits.length) return 'empty'
  const commitIds = snapshot.commits
    .map((commit) => commit.id)
    .sort()
    .join(',')
  const edges = snapshot.commits
    .flatMap((commit) => (commit.parents ?? []).map((parent) => `${parent}->${commit.id}`))
    .sort()
    .join(',')
  return `${commitIds}|${edges}`
}
