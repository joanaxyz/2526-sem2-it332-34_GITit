import type { PieceAnimationConfig, TowerPieceAssetDescriptor } from '@/shared/assets/types'

export type ResolvedPieceArt = { svg: string; animation: PieceAnimationConfig | null }

/**
 * Resolve a piece's inline SVG + animation for `PieceSvg`. The art is owned by
 * the asset and served as sanitized inline SVG on the descriptor — the backend
 * is the single source of truth, so there is no bundled fallback art and the
 * frontend never re-draws a piece. Returns null when the descriptor carries no
 * SVG yet (e.g. a fresh user upload), so the caller can show a placeholder.
 */
export function resolvePieceArt(
  descriptor: TowerPieceAssetDescriptor | null | undefined,
): ResolvedPieceArt | null {
  const svg = descriptor?.tower_piece?.svg
  if (!svg) return null
  return { svg, animation: descriptor?.tower_piece?.animation ?? null }
}
