import { useId, useMemo, type CSSProperties } from 'react'

import type { PieceAnimationConfig } from '@/shared/assets/types'
import { cn } from '@/shared/utils/cn'
import {
  DEFAULT_PRESET_DURATION_MS,
  DEFAULT_PRESET_EASING,
  PIECE_PRESET_CLASS,
} from './animationPresets'
import { namespaceSvgIds } from './svgNamespace'

/**
 * Renders a tower piece from inline SVG data + a safe animation preset — the
 * data-driven replacement for the hardcoded `*Art` components. The SVG is
 * inlined (so it can be styled/animated, unlike the old flat `<img>`) with its
 * ids namespaced per instance so repeated pieces don't collide. The preset adds
 * a `.piece-anim--*` class that the CSS uses to move the SVG's `data-role` parts
 * when an interactive ancestor is hovered/selected.
 *
 * SECURITY: only ever pass SVG that was sanitized upstream. Official seed art is
 * trusted; user-uploaded SVG must be sanitized before it reaches the descriptor
 * (the backend's `TowerPieceAsset.svg_sanitized` gate).
 */
export function PieceSvg({
  svg,
  animation,
  className,
  viewBox,
  variant,
}: {
  svg: string
  animation?: PieceAnimationConfig | null
  className?: string
  viewBox?: string | null
  variant?: string
}) {
  const uid = useId().replace(/[:]/g, '')
  const html = useMemo(() => {
    const namespaced = namespaceSvgIds(svg, uid)
    if (!viewBox) return namespaced
    return namespaced.replace(/\sviewBox=(["'])(.*?)\1/i, ` viewBox="${viewBox}"`)
  }, [svg, uid, viewBox])
  const preset = animation?.preset ?? 'none'
  const style = {
    '--piece-anim-duration': `${animation?.durationMs ?? DEFAULT_PRESET_DURATION_MS}ms`,
    '--piece-anim-ease': animation?.easing ?? DEFAULT_PRESET_EASING,
  } as CSSProperties

  return (
    <span
      className={cn('piece-svg', PIECE_PRESET_CLASS[preset], className)}
      style={style}
      data-piece-variant={variant}
      aria-hidden="true"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
