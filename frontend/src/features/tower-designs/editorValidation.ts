import type { ArtifactPlacementDescriptor, TowerDesignOverview } from '@/features/tower-designs/types'

export type DesignIssue = { id: string; message: string; instanceId: string; storeyIndex: number }

/** Status of the content an interactive artifact is bound to, or null when it
 *  has no binding. Mirrors the backend `publish_errors` per-artifact checks. */
function boundContentStatus(
  overview: TowerDesignOverview,
  artifact: ArtifactPlacementDescriptor,
): string | null {
  const id = artifact.contentBinding?.id
  if (id === undefined || id === null) return null
  const bucket =
    artifact.role === 'adventure'
      ? overview.content.adventures
      : artifact.role === 'challenge'
        ? overview.content.challenges
        : artifact.role === 'tome'
          ? overview.content.tomes
          : null
  return bucket?.[String(id)]?.status ?? null
}

/**
 * Publish/share readiness, per interactive artifact. There are deliberately no
 * per-piece count rules or structural target rules. The server also only
 * requires published content for interactive artifacts. Normal artifacts are
 * never flagged.
 */
export function validateDesign(overview: TowerDesignOverview): DesignIssue[] {
  const storeyByInstance = new Map<string, number>()
  for (const piece of overview.tower_layout.pieces) {
    storeyByInstance.set(piece.instanceId, typeof piece.storeyIndex === 'number' ? piece.storeyIndex : 0)
  }

  const issues: DesignIssue[] = []
  let n = 0
  for (const artifact of overview.artifacts) {
    if (artifact.role === 'normal') continue
    const instanceId = artifact.targetInstanceId
    const storeyIndex = storeyByInstance.get(instanceId) ?? 0
    const add = (message: string) =>
      issues.push({ id: `${artifact.id}:${n++}`, message, instanceId, storeyIndex })

    const contentId = artifact.contentBinding?.id
    if (contentId === undefined || contentId === null) {
      add('Interactive artifact needs content bound.')
      continue
    }
    const status = boundContentStatus(overview, artifact)
    if (status !== null && status !== 'published') {
      add('Bound content must be published before sharing.')
    }
  }
  return issues
}
