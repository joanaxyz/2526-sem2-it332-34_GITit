import type { ReactNode } from 'react'

import type { SpriteDef } from '@/shared/cosmetics/types'
import { cn } from '@/shared/utils/cn'

/**
 * A still thumbnail: the first frame of a code-registry `SpriteDef`, cropped out
 * of its sheet with the same background-position trick the SpriteAnimator paints
 * with — no animation, no extra requests. The DB-free counterpart to the old
 * AssetPortrait (which read backend descriptor sprites).
 */
export function SpritePortrait({
  sprite,
  label,
  className,
  fallback = null,
}: {
  sprite: SpriteDef | undefined
  label?: string
  className?: string
  fallback?: ReactNode
}) {
  if (!sprite?.src) return <>{fallback}</>

  const columns = Math.max(1, sprite.columns || 1)
  const rows = Math.max(1, sprite.rows || 1)
  const isStaticPortrait = columns === 1 && rows === 1

  return (
    <span
      role={label ? 'img' : undefined}
      aria-label={label || undefined}
      aria-hidden={label ? undefined : true}
      className={cn('asset-portrait', className)}
      style={{
        backgroundImage: `url(${sprite.src})`,
        backgroundRepeat: 'no-repeat',
        backgroundSize: isStaticPortrait ? 'contain' : `${columns * 100}% ${rows * 100}%`,
        backgroundPosition: isStaticPortrait ? 'center bottom' : '0% 0%',
        imageRendering: isStaticPortrait ? 'auto' : 'pixelated',
      }}
    />
  )
}
