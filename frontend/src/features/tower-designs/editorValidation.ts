import type { ArtifactPlacementDescriptor, TowerDesignOverview } from '@/features/tower-designs/types'
import type { TowerArtifactRole } from '@/shared/assets/types'

export type InteractableRole = Exclude<TowerArtifactRole, 'normal'>

/** Live, per-section readout of the interactable-content rules the editor and the
 *  server both enforce: a section holds one interactable, unless it holds the
 *  three-challenge chain. Mirrors backend `publish_errors` so authors see the
 *  same verdict before they hit Publish. */
export type SectionStatus = {
  instanceId: string
  storeyIndex: number
  role: InteractableRole | null
  count: number
  required: number
  complete: boolean
  issues: string[]
}

export type DesignIssue = { id: string; message: string; instanceId: string; storeyIndex: number }

const REQUIRED_BY_ROLE: Record<InteractableRole, number> = { adventure: 1, challenge: 3, tome: 1 }

function isInteractable(role: TowerArtifactRole): role is InteractableRole {
  return role !== 'normal'
}

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

export function buildSectionStatuses(overview: TowerDesignOverview): Map<string, SectionStatus> {
  const byInstance = new Map<string, ArtifactPlacementDescriptor[]>()
  for (const artifact of overview.artifacts) {
    const list = byInstance.get(artifact.targetInstanceId) ?? []
    list.push(artifact)
    byInstance.set(artifact.targetInstanceId, list)
  }

  const statuses = new Map<string, SectionStatus>()
  for (const piece of overview.tower_layout.pieces) {
    if (piece.pieceType !== 'section') continue
    const interactables = (byInstance.get(piece.instanceId) ?? []).filter((a) => isInteractable(a.role))
    const role = (interactables[0]?.role as InteractableRole | undefined) ?? null
    const count = interactables.length
    const required = role ? REQUIRED_BY_ROLE[role] : 0
    const issues: string[] = []

    if (role === 'challenge' && count !== 3) {
      issues.push(`Needs exactly three challenges — has ${count}.`)
    }
    if (interactables.some((a) => a.contentBinding?.id === undefined || a.contentBinding?.id === null)) {
      issues.push('An interactive artifact has no content bound.')
    }
    if (
      interactables.some((a) => {
        const status = boundContentStatus(overview, a)
        return status !== null && status !== 'published'
      })
    ) {
      issues.push('Bound content must be published before sharing.')
    }

    statuses.set(piece.instanceId, {
      instanceId: piece.instanceId,
      storeyIndex: typeof piece.storeyIndex === 'number' ? piece.storeyIndex : 0,
      role,
      count,
      required,
      complete: issues.length === 0,
      issues,
    })
  }
  return statuses
}

export function validateDesign(overview: TowerDesignOverview): DesignIssue[] {
  const issues: DesignIssue[] = []
  let n = 0
  for (const status of buildSectionStatuses(overview).values()) {
    for (const message of status.issues) {
      issues.push({ id: `${status.instanceId}:${n++}`, message, instanceId: status.instanceId, storeyIndex: status.storeyIndex })
    }
  }
  return issues
}
