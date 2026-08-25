import { useMemo } from 'react'

import { DEFAULT_COMPANION_SLUG, getCompanion } from '@/shared/cosmetics/companions/registry'
import { companionFromDef } from '@/shared/cosmetics/companionRuntime'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import { cn } from '@/shared/utils/cn'

const containerClass = {
  screen: 'min-h-screen bg-background p-4',
  page: 'min-h-[calc(100vh-8rem)] p-4',
  panel: 'min-h-40 p-4',
  inline: 'min-h-28 py-4',
  compact: 'min-h-0 py-1',
} as const

const frameClass = {
  screen: 'gap-5 p-0',
  page: 'gap-5 p-0',
  panel: 'gap-4 p-0',
  inline: 'gap-3 p-0',
  compact: 'gap-2 p-0',
} as const

type LoadingStateVariant = keyof typeof containerClass

const loaderScale = {
  screen: 1.4,
  page: 1.12,
  panel: 0.7,
  inline: 0.5,
  compact: 0.38,
} satisfies Record<LoadingStateVariant, number>

function CompanionRunLoader({
  companionSlug,
  variant,
}: {
  companionSlug?: string | null
  variant: LoadingStateVariant
}) {
  const isSmall = variant === 'inline' || variant === 'compact'
  const companionDef = getCompanion(companionSlug ?? DEFAULT_COMPANION_SLUG)
  const companion = useMemo(() => companionFromDef(companionDef), [companionDef])

  if (!companion) return null

  return (
    <div
      aria-hidden="true"
      className={cn(
        'git-it-companion-loader',
        `git-it-companion-loader--${variant}`,
        isSmall && 'git-it-companion-loader--small',
        variant === 'compact' && 'git-it-companion-loader--compact',
      )}
    >
      <div className="git-it-companion-loader__stage">
        <SpriteAnimator
          animation={companion.sprites.run}
          anchorToPixelBounds
          aria-label={`${companionDef.label} running`}
          className="git-it-companion-loader__sprite"
          layoutAnimation={companion.sprites.idle}
          pixelAnchorAnimation={companion.sprites.run}
          pixelAnchorFallback={{ bottomOffset: companion.metrics.footOffset }}
          pixelated
          scale={loaderScale[variant]}
        />
      </div>
    </div>
  )
}

export function LoadingState({
  label = 'Loading',
  description,
  variant = 'panel',
  className,
  companionSlug,
}: {
  label?: string
  description?: string
  variant?: LoadingStateVariant
  className?: string
  companionSlug?: string | null
}) {
  const isCompact = variant === 'compact'

  return (
    <div
      aria-label={label}
      aria-live="polite"
      className={cn(
        'git-it-loading-state',
        `git-it-loading-state--${variant}`,
        'relative isolate flex items-center justify-center overflow-hidden text-center',
        containerClass[variant],
        className,
      )}
      role="status"
    >
      <div className={cn('relative flex w-full max-w-md flex-col items-center', frameClass[variant])}>
        <CompanionRunLoader companionSlug={companionSlug} variant={variant} />

        <div className={cn('git-it-loading-state__copy grid gap-1', isCompact ? 'text-xs' : 'text-sm')}>
          <p className="font-semibold text-foreground">{label}</p>
          {description ? (
            <p className={cn('mx-auto max-w-xs leading-5 text-muted-foreground', isCompact && 'hidden')}>
              {description}
            </p>
          ) : null}
        </div>
      </div>
    </div>
  )
}
