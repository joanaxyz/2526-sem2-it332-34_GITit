import type { TowerArtifactRole, TowerPieceType } from '@/shared/assets/types'

export function pieceIdFromInstance(instanceId: string): number | null {
  const match = /-piece-(\d+)$/.exec(instanceId)
  return match ? Number(match[1]) : null
}

export const PIECE_TYPE_LABEL: Record<TowerPieceType, string> = {
  crown: 'Crown',
  section: 'Section',
  landing: 'Landing',
}

export const ARTIFACT_ROLE_LABEL: Record<TowerArtifactRole, string> = {
  normal: 'Normal artifact',
  adventure: 'Adventure artifact',
  challenge: 'Challenge artifact',
  tome: 'Tome artifact',
}

export const INTERACTABLE_ROLES: TowerArtifactRole[] = ['adventure', 'challenge', 'tome']
