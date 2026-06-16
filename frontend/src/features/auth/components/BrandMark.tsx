import { GitBranch } from 'lucide-react'
import { Link } from 'react-router-dom'

import { cn } from '@/shared/utils/cn'

type BrandMarkProps = {
  /** `lg` for the hero column, `sm` for the compact mobile card header. */
  size?: 'sm' | 'lg'
  className?: string
}

/**
 * Logo glyph + "GIT it!" wordmark, linking home. Rendered in the desktop hero
 * AND as the mobile card header so identity + an exit are never gated behind a
 * desktop-only panel.
 */
export function BrandMark({ size = 'lg', className }: BrandMarkProps) {
  const lg = size === 'lg'
  return (
    <Link
      to="/"
      aria-label="GIT it! home"
      className={cn('group inline-flex items-center gap-2.5', className)}
    >
      <span
        className={cn(
          'grid place-items-center rounded-md border border-primary/30 bg-primary/10 text-primary transition-all duration-200 group-hover:border-primary/60 group-hover:shadow-aurora-sm',
          lg ? 'size-10' : 'size-8',
        )}
      >
        <GitBranch className={lg ? undefined : 'size-4'} />
      </span>
      <span className={cn('font-extrabold tracking-tight', lg ? 'text-xl' : 'text-base')}>
        GIT <span className="text-primary">it!</span>
      </span>
    </Link>
  )
}
