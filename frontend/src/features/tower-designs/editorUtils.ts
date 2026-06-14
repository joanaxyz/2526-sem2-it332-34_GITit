import type { TowerPieceType } from '@/shared/assets/types'
import type { ContentKind } from '@/features/authoring/types'

/** The backend instanceId is `tower-<designId>-piece-<pieceId>`. */
export function pieceIdFromInstance(instanceId: string): number | null {
  const match = /-piece-(\d+)$/.exec(instanceId)
  return match ? Number(match[1]) : null
}

/** Which content kind a section piece can be bound to (others are non-bindable). */
export const BINDABLE_KIND: Partial<Record<TowerPieceType, ContentKind>> = {
  adventure_section: 'adventure',
  challenge_section: 'challenge',
  tome: 'tome',
}

export const PIECE_TYPE_LABEL: Record<TowerPieceType, string> = {
  spire: 'Spire / Roof',
  landing: 'Landing',
  door: 'Door',
  adventure_section: 'Adventure Section',
  challenge_section: 'Challenge Section',
  tome: 'Tome',
}

export const PALETTE_GROUPS: TowerPieceType[] = [
  'spire',
  'adventure_section',
  'challenge_section',
  'tome',
  'landing',
  'door',
]
