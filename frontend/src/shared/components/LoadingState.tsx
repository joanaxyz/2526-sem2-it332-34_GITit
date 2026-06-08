import { cn } from '@/shared/utils/cn'

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

const towerSizeClass = {
  screen: 'git-it-tower--lg',
  page: 'git-it-tower--lg',
  panel: 'git-it-tower--md',
  inline: null,
  compact: null,
} as const

type LoadingStateVariant = keyof typeof containerClass

// Simplified flying wyvern/dragon silhouette, spread wings + forked tail, head up.
const DRAGON_PATH =
  'M12 3 L10.2 5.2 Q4 4 1 6.5 Q5 8 7.5 9 L10 10.5 L8.5 15.5 L12 12 ' +
  'L15.5 15.5 L14 10.5 L16.5 9 Q19 8 23 6.5 Q20 4 13.8 5.2 Z'

function Cloud() {
  return (
    <>
      <ellipse cx="10" cy="12" rx="10" ry="6" />
      <ellipse cx="20" cy="8.5" rx="9.5" ry="7" />
      <ellipse cx="29" cy="13" rx="9" ry="5" />
      <rect x="2" y="12" width="34" height="6" rx="3" />
    </>
  )
}

function FantasyTower({ variant }: { variant: LoadingStateVariant }) {
  const sizeClass = towerSizeClass[variant]
  if (!sizeClass) return null

  return (
    <div aria-hidden="true" className={cn('git-it-tower', sizeClass)}>
      <svg className="git-it-tower-svg" viewBox="0 0 160 150" role="img">
        <defs>
          <clipPath id="git-it-body-clip">
            <rect x="62" y="62" width="36" height="70" />
          </clipPath>
        </defs>

        {/* Sky — drifting clouds behind the tower */}
        <g className="git-it-cloud git-it-cloud--a">
          <Cloud />
        </g>
        <g className="git-it-cloud git-it-cloud--b">
          <Cloud />
        </g>
        <g className="git-it-cloud git-it-cloud--c">
          <Cloud />
        </g>

        {/* Anchor beam + chains the keep hangs from */}
        <g className="git-it-anchor">
          <rect className="git-it-stone" x="54" y="1" width="52" height="5" rx="1.5" />
          <line className="git-it-chain" x1="68" y1="6" x2="68" y2="15" />
          <line className="git-it-chain" x1="92" y1="6" x2="92" y2="15" />
        </g>

        {/* The keep — hung upside down so the spire points downward */}
        <g className="git-it-keep" transform="translate(0 150) scale(1 -1)">
          {/* ground glow + plinth */}
          <ellipse className="git-it-keep-ground" cx="80" cy="140" rx="46" ry="5" />
          <rect className="git-it-stone" x="50" y="136" width="60" height="6" rx="1.5" />
          <rect className="git-it-stone" x="56" y="131" width="48" height="6" rx="1.5" />

          {/* tower body + course lines */}
          <rect className="git-it-stone" x="62" y="62" width="36" height="70" rx="1.5" />
          <g className="git-it-course">
            <line x1="62" y1="76" x2="98" y2="76" />
            <line x1="62" y1="90" x2="98" y2="90" />
            <line x1="62" y1="104" x2="98" y2="104" />
            <line x1="62" y1="118" x2="98" y2="118" />
          </g>

          {/* construction scan-line — the "building" pulse */}
          <g clipPath="url(#git-it-body-clip)">
            <rect className="git-it-tower-scan" x="62" width="36" height="3" />
          </g>

          {/* battlements */}
          <rect className="git-it-stone" x="58" y="56" width="44" height="7" rx="1" />
          <g className="git-it-stone">
            <rect x="58" y="51" width="6" height="6" />
            <rect x="67" y="51" width="6" height="6" />
            <rect x="76" y="51" width="6" height="6" />
            <rect x="85" y="51" width="6" height="6" />
            <rect x="94" y="51" width="6" height="6" />
          </g>

          {/* conical roof */}
          <path className="git-it-roof" d="M80 28 L102 56 L58 56 Z" />

          {/* lit windows + arched door */}
          <circle className="git-it-window" cx="80" cy="72" r="4" style={{ animationDelay: '0s' }} />
          <path
            className="git-it-window"
            d="M74 98 L74 90 Q74 84 80 84 Q86 84 86 90 L86 98 Z"
            style={{ animationDelay: '0.7s' }}
          />
          <path className="git-it-door" d="M73 132 L73 124 Q73 116 80 116 Q87 116 87 124 L87 132 Z" />
        </g>

        {/* Dragons flying over the tower */}
        <g className="git-it-dragon git-it-dragon--a">
          <path className="git-it-dragon-body" d={DRAGON_PATH} />
        </g>
        <g className="git-it-dragon git-it-dragon--b">
          <path className="git-it-dragon-body" d={DRAGON_PATH} />
        </g>
      </svg>
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
      {variant !== 'inline' && variant !== 'compact' ? (
        <div aria-hidden="true" className="git-it-loading-grid absolute inset-0 opacity-55" />
      ) : null}
      <div className={cn('relative flex w-full max-w-md flex-col items-center', frameClass[variant])}>
        <FantasyTower variant={variant} />
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
