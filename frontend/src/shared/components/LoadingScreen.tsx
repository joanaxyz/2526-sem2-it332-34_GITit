import { useMemo } from 'react'
import { createPortal } from 'react-dom'

import { getCompanion } from '@/shared/cosmetics/companions/registry'
import { companionFromDef } from '@/shared/cosmetics/companionRuntime'
import {
  LOADING_PAINT_DELAY_MS,
  LOADING_SLOW_AFTER_MS,
  useElapsedFlag,
  useLockBodyScroll,
} from '@/shared/components/loadingTiming'
import { useAuthStore } from '@/shared/auth/useAuth'
import { useEquippedCompanion } from '@/shared/player-loadout/useEquippedCompanion'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import { cn } from '@/shared/utils/cn'

/** Commit nodes on the rail. Five reads as a graph; more reads as a barber pole. */
const RAIL_NODES = [0, 1, 2, 3, 4]

const COMPANION_SCALE = 1.4

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

function CompanionRunLoader({ companionSlug }: { companionSlug: string }) {
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
      scale={COMPANION_SCALE}
    />
  )
}

/**
 * The one loading screen. It is always the full viewport and always on top:
 * it portals to `document.body` and paints fixed, so it can never end up
 * boxed inside the nav shell or a workspace column the way an in-flow loader
 * does. Reserve it for waits where the destination does not exist yet -
 * restoring a session, hydrating the app, entering or preparing a run - and
 * use `LoadingState` for anything that loads inside a shell already on screen.
 */
export function LoadingScreen({
  label = 'Loading',
  description,
  className,
  companionSlug,
  showCompanion = true,
}: {
  label?: string
  description?: string
  className?: string
  /** Overrides the equipped companion. Only pass it when the surface knows a
   * companion the player has not equipped (a preview, another player's run). */
  companionSlug?: string | null
  showCompanion?: boolean
}) {
  // The player's own companion runs the loader; an explicit slug wins so a
  // preview surface can still pin a specific one.
  const equipped = useEquippedCompanion()
  const playerName = useAuthStore((state) => state.user?.username)
  const slug = companionSlug ?? equipped.slug
  const painted = useElapsedFlag(LOADING_PAINT_DELAY_MS)
  const slow = useElapsedFlag(LOADING_SLOW_AFTER_MS)
  // A player who owns no companion is on their first run: the default one
  // stands in, and the wait doubles as the one welcome they get. Never when an
  // explicit slug means this loader is showing somebody else's pick.
  const welcome = !companionSlug && equipped.isUnequipped
  const greeting = playerName ? `Welcome, ${playerName}` : 'Welcome to GIT it!'

  // Nothing behind the screen is ready to be touched, so the page underneath
  // must not scroll away beneath it.
  useLockBodyScroll()

  return createPortal(
    <div
      aria-busy="true"
      aria-label={label}
      aria-live="polite"
      className={cn(
        'git-it-loading-screen',
        painted && 'is-painted',
        'relative isolate flex items-center justify-center overflow-hidden text-center',
        className,
      )}
      role="status"
    >
      <div className="git-it-loading-screen__frame">
        <div className={cn('git-it-companion-loader', showCompanion && 'has-companion')}>
          <div className="git-it-companion-loader__stage">
            {showCompanion ? <CompanionRunLoader companionSlug={slug} /> : null}
          </div>
          <CommitRail />
        </div>

        <div className="git-it-loading-screen__copy">
          {welcome ? <p className="git-it-loading-screen__welcome">{greeting}</p> : null}
          <p className="git-it-loading-screen__label">{label}</p>
          {description ? <p className="git-it-loading-screen__description">{description}</p> : null}
          {slow ? (
            <p className="git-it-loading-screen__slow">
              Still working. The server is taking longer than usual.
            </p>
          ) : null}
        </div>
      </div>
    </div>,
    document.body,
  )
}
