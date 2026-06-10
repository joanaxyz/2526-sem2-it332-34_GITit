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

function TowerBuildLoader({ variant }: { variant: LoadingStateVariant }) {
  const isSmall = variant === 'inline' || variant === 'compact'

  return (
    <div
      aria-hidden="true"
      className={cn(
        'git-it-build-loader',
        isSmall && 'git-it-build-loader--small',
        variant === 'compact' && 'git-it-build-loader--compact',
      )}
    >
      <div className="git-it-build-tower">
        <span className="git-it-build-roof-spire" />

        <div className="git-it-build-roof" />

        <div className="git-it-build-storey git-it-build-storey--top">
          <span className="git-it-build-window" />
          <span className="git-it-build-window" />
          <span className="git-it-build-window" />
        </div>

        <div className="git-it-build-storey git-it-build-storey--mid">
          <span className="git-it-build-brick git-it-build-brick--a" />
          <span className="git-it-build-brick git-it-build-brick--b" />
          <span className="git-it-build-door" />
          <span className="git-it-build-brick git-it-build-brick--c" />
        </div>

        <div className="git-it-build-storey git-it-build-storey--base">
          <span className="git-it-build-block git-it-build-block--1" />
          <span className="git-it-build-block git-it-build-block--2" />
          <span className="git-it-build-block git-it-build-block--3" />
          <span className="git-it-build-block git-it-build-block--4" />
        </div>

        <span className="git-it-build-spark git-it-build-spark--a" />
        <span className="git-it-build-spark git-it-build-spark--b" />
        <span className="git-it-build-spark git-it-build-spark--c" />
      </div>
    </div>
  )
}

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
  const isCompact = variant === 'compact'

  return (
    <div
      aria-label={label}
      aria-live="polite"
      className={cn(
        'relative isolate flex items-center justify-center overflow-hidden text-center',
        containerClass[variant],
        className,
      )}
      role="status"
    >
      <div className={cn('relative flex w-full max-w-md flex-col items-center', frameClass[variant])}>
        <TowerBuildLoader variant={variant} />

        <div className={cn('grid gap-1', isCompact ? 'text-xs' : 'text-sm')}>
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