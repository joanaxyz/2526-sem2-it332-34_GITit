import { cn } from '@/shared/utils/cn'

const LOADING_MARK = Array.from('GIT IT..')

const containerClass = {
  screen: 'min-h-screen bg-background p-4',
  page: 'min-h-[calc(100vh-8rem)] p-4',
  panel: 'min-h-40 p-4',
  inline: 'min-h-28 py-4',
  compact: 'min-h-0 py-1',
} as const

const frameClass = {
  screen: 'gap-4 rounded-md border border-primary/20 bg-card/85 p-7 shadow-[0_22px_80px_rgba(0,0,0,0.42),inset_0_1px_0_rgba(0,245,212,0.16)]',
  page: 'gap-4 rounded-md border border-primary/20 bg-card/85 p-7 shadow-[0_18px_70px_rgba(0,0,0,0.34),inset_0_1px_0_rgba(0,245,212,0.16)]',
  panel: 'gap-4 rounded-md border border-primary/20 bg-card/75 p-6 shadow-[inset_0_1px_0_rgba(0,245,212,0.14)]',
  inline: 'gap-3',
  compact: 'gap-2',
} as const

const markSizeClass = {
  screen: 'text-4xl',
  page: 'text-4xl',
  panel: 'text-3xl',
  inline: 'text-2xl',
  compact: 'text-lg',
} as const

type LoadingStateVariant = keyof typeof containerClass

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
      {variant !== 'inline' && variant !== 'compact' ? (
        <div aria-hidden="true" className="git-it-loading-grid absolute inset-0 opacity-55" />
      ) : null}
      <div className={cn('relative flex w-full max-w-md flex-col items-center', frameClass[variant])}>
        <div
          aria-hidden="true"
          className={cn(
            'flex items-end justify-center gap-1 font-mono font-extrabold leading-none text-primary',
            markSizeClass[variant],
          )}
        >
          {LOADING_MARK.map((letter, index) =>
            letter === ' ' ? (
              <span className="w-2" key={`space-${index}`} />
            ) : (
              <span
                className="git-it-loading-letter"
                key={`${letter}-${index}`}
                style={{ animationDelay: `${index * 80}ms` }}
              >
                {letter}
              </span>
            ),
          )}
        </div>
        <div
          aria-hidden="true"
          className={cn(
            'overflow-hidden rounded-full border border-primary/20 bg-secondary/70',
            isCompact ? 'h-1 w-28' : 'h-1.5 w-48',
          )}
        >
          <span className="git-it-loading-meter block h-full rounded-full bg-gradient-to-r from-primary via-accent to-foreground" />
        </div>
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
