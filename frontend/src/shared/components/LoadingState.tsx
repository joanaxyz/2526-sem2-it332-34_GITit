import { Spinner, type SpinnerSize } from '@/shared/components/Spinner'
import { LOADING_PAINT_DELAY_MS, useElapsedFlag } from '@/shared/components/loadingTiming'
import { cn } from '@/shared/utils/cn'

const containerClass = {
  panel: 'min-h-40 p-4',
  inline: 'min-h-28 py-4',
  compact: 'min-h-0 py-1',
} as const

type LoadingStateVariant = keyof typeof containerClass

const spinnerSize = {
  panel: 'md',
  inline: 'sm',
  compact: 'xs',
} satisfies Record<LoadingStateVariant, SpinnerSize>

/**
 * A component's loading state: a basic spinner, in place, inside whatever
 * chrome the surface already has.
 *
 * This is the only loader that renders in the layout flow, and it deliberately
 * has no page-sized variant: a wait that owns a whole routed page is a
 * navigation, and navigations belong to the full-screen `LoadingScreen`. Use
 * this one only when real page content is already on screen beside it - a
 * table filling in under its heading, a modal body, a sub-panel re-querying.
 */
export function LoadingState({
  label = 'Loading',
  description,
  variant = 'panel',
  className,
}: {
  label?: string
  description?: string
  variant?: LoadingStateVariant
  className?: string
}) {
  const painted = useElapsedFlag(LOADING_PAINT_DELAY_MS)
  const isCompact = variant === 'compact'

  return (
    <div
      aria-busy="true"
      aria-label={label}
      aria-live="polite"
      className={cn(
        'git-it-loading-state',
        `git-it-loading-state--${variant}`,
        painted && 'is-painted',
        'flex items-center justify-center text-center',
        containerClass[variant],
        className,
      )}
      role="status"
    >
      <div className="git-it-loading-state__frame">
        <Spinner size={spinnerSize[variant]} />
        <div className="git-it-loading-state__copy">
          <p className="git-it-loading-state__label">{label}</p>
          {description && !isCompact ? (
            <p className="git-it-loading-state__description">{description}</p>
          ) : null}
        </div>
      </div>
    </div>
  )
}
