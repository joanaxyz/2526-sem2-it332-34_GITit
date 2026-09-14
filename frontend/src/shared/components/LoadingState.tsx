import { useEffect, useMemo, useState } from 'react'

import { getCompanion } from '@/shared/cosmetics/companions/registry'
import { companionFromDef } from '@/shared/cosmetics/companionRuntime'
import { useAuthStore } from '@/shared/auth/useAuth'
import { useEquippedCompanion } from '@/shared/player-loadout/useEquippedCompanion'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import { cn } from '@/shared/utils/cn'

const containerClass = {
  screen: 'min-h-screen bg-background p-4',
  page: 'min-h-[calc(100vh-8rem)] p-4',
  panel: 'min-h-40 p-4',
  inline: 'min-h-28 py-4',
  compact: 'min-h-0 py-1',
} as const

type LoadingStateVariant = keyof typeof containerClass

const loaderScale = {
  screen: 1.4,
  page: 1.12,
  panel: 0.7,
  inline: 0.5,
  compact: 0.38,
} satisfies Record<LoadingStateVariant, number>

/** Commit nodes on the rail. Five reads as a graph; more reads as a barber pole. */
const RAIL_NODES = [0, 1, 2, 3, 4]

/**
 * A load short enough to be imperceptible should not flash a whole screen of
 * loader on the way past. Nothing paints until the wait is real; the container
 * still holds its box so the layout never jumps.
 */
const PAINT_DELAY_MS = 160

/**
 * Past this the wait has stopped looking like a wait and starts looking broken.
 * Long enough that a normal slow request never trips it.
 */
const SLOW_AFTER_MS = 9000

function useElapsedFlag(afterMs: number) {
  const [elapsed, setElapsed] = useState(false)
  useEffect(() => {
    const timer = window.setTimeout(() => setElapsed(true), afterMs)
    return () => window.clearTimeout(timer)
  }, [afterMs])
  return elapsed
}

/**
 * The commit rail: the load rendered in the vocabulary the learner already
 * reads all day. A write head sweeps the rail and each commit lights as it
 * passes, so the screen says "the repository is being assembled" instead of
 * "something is spinning". It carries the whole loading state on its own,
 * which is what makes a companion-less loader still feel alive.
 */
function CommitRail() {
  return (
    <div aria-hidden="true" className="git-it-commit-rail">
      <span className="git-it-commit-rail__sweep" />
      {RAIL_NODES.map((index) => (
        <span
          className="git-it-commit-rail__node"
          key={index}
          style={{ '--node-index': index } as React.CSSProperties}
        />
      ))}
    </div>
  )
}

function CompanionRunLoader({
  companionSlug,
  variant,
}: {
  companionSlug: string
  variant: LoadingStateVariant
}) {
  const companionDef = getCompanion(companionSlug)
  const companion = useMemo(() => companionFromDef(companionDef), [companionDef])

  if (!companion) return null

  return (
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
  )
}

export function LoadingState({
  label = 'Loading',
  description,
  variant = 'panel',
  className,
  companionSlug,
  showCompanion = true,
}: {
  label?: string
  description?: string
  variant?: LoadingStateVariant
  className?: string
  /** Overrides the equipped companion. Only pass it when the surface knows a
   * companion the player has not equipped (a preview, another player's run). */
  companionSlug?: string | null
  showCompanion?: boolean
}) {
  const isCompact = variant === 'compact'
  const isRoomy = variant === 'screen' || variant === 'page'
  // The player's own companion runs the loader; an explicit slug wins so a
  // preview surface can still pin a specific one.
  const equipped = useEquippedCompanion()
  const playerName = useAuthStore((state) => state.user?.username)
  const slug = companionSlug ?? equipped.slug
  const painted = useElapsedFlag(PAINT_DELAY_MS)
  const slow = useElapsedFlag(SLOW_AFTER_MS)
  // A player who owns no companion is on their first run: the default one
  // stands in, and the wait doubles as the one welcome they get. Only on the
  // roomy variants - an admin table cell is not a first-run moment - and never
  // when an explicit slug means this loader is showing somebody else's pick.
  const welcome = isRoomy && !companionSlug && equipped.isUnequipped
  const greeting = playerName ? `Welcome, ${playerName}` : 'Welcome to GIT it!'

  return (
    <div
      aria-label={label}
      aria-live="polite"
      className={cn(
        'git-it-loading-state',
        `git-it-loading-state--${variant}`,
        painted && 'is-painted',
        'relative isolate flex items-center justify-center overflow-hidden text-center',
        containerClass[variant],
        className,
      )}
      role="status"
    >
      <div className="git-it-loading-state__frame">
        <div
          className={cn(
            'git-it-companion-loader',
            `git-it-companion-loader--${variant}`,
            showCompanion && 'has-companion',
          )}
        >
          <div className="git-it-companion-loader__stage">
            {showCompanion ? <CompanionRunLoader companionSlug={slug} variant={variant} /> : null}
          </div>
          <CommitRail />
        </div>

        <div className="git-it-loading-state__copy">
          {welcome ? <p className="git-it-loading-state__welcome">{greeting}</p> : null}
          <p className="git-it-loading-state__label">{label}</p>
          {description && !isCompact ? (
            <p className="git-it-loading-state__description">{description}</p>
          ) : null}
          {slow && isRoomy ? (
            <p className="git-it-loading-state__slow">Still working. The server is taking longer than usual.</p>
          ) : null}
        </div>
      </div>
    </div>
  )
}
