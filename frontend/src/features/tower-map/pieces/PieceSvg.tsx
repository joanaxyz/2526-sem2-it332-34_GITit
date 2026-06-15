import { useId, useMemo } from 'react'

import { cn } from '@/shared/utils/cn'
import { namespaceSvgIds } from './svgNamespace'

/**
 * Renders sanitized inline SVG data with per-instance id namespacing. Asset
 * animation is not implemented here; sprites/actions supplied by the asset data
 * are rendered by the artifact/sprite renderer.
 */
export function PieceSvg({
  svg,
  className,
  viewBox,
  variant,
}: {
  svg: string
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

  return (
    <span
      className={cn('piece-svg', className)}
      data-piece-variant={variant}
      aria-hidden="true"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
