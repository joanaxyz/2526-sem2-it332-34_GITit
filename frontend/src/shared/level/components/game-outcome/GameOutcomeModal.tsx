import type { ComponentType, ReactNode } from 'react'
import { X } from 'lucide-react'

import loseStarsImage from '@/assets/images/battle-outcome/lose-0.png'
import titlesImage from '@/assets/images/battle-outcome/titles.png'
import winStars1Image from '@/assets/images/battle-outcome/win-1.png'
import winStars2Image from '@/assets/images/battle-outcome/win-2.png'
import winStars3Image from '@/assets/images/battle-outcome/win-3.png'
import { Button } from '@/shared/components/Button'
import { Modal } from '@/shared/components/Modal'
import { cn } from '@/shared/utils/cn'

import { GameOutcomeConfetti } from './GameOutcomeConfetti'
import { GameOutcomeStatTile } from './GameOutcomeStatTile'

/** Star-arc hero art, indexed by earned stars (1-3). */
const WIN_STAR_ART = [winStars1Image, winStars2Image, winStars3Image] as const

export type GameOutcomeStat = {
  label: string
  numerator: number
  denominator?: number
  suffix?: string
  helper: string
  icon?: ComponentType<{ className?: string }>
  /** Neon icon art (battle-outcome assets); wins over `icon` when set. */
  iconSrc?: string
}

/**
 * Shared game result overlay for challenge and adventure run endings. Feature
 * wrappers own outcome state and copy; this component owns the visual chrome.
 */
export function GameOutcomeModal({
  open,
  onClose,
  title,
  tone = 'success',
  icon: Icon,
  resultLabel,
  stars,
  badges,
  headline,
  message,
  note,
  stats,
  children,
  actions,
  className,
}: {
  open: boolean
  onClose: () => void
  title: string
  tone?: 'success' | 'failure'
  icon: ComponentType<{ className?: string }>
  /** Large result wordmark, e.g. "You Won" or "Game Over". */
  resultLabel?: string
  /** Stars earned, shown as the hero crest when provided. */
  stars?: number
  badges?: ReactNode
  headline: string
  message: ReactNode
  /** Optional emphasised aside under the message. */
  note?: ReactNode
  stats?: GameOutcomeStat[]
  /** Surface-specific section rendered between the stats and the actions. */
  children?: ReactNode
  actions?: ReactNode
  className?: string
}) {
  const isFailed = tone === 'failure'
  const earnedStars = Number.isFinite(stars) ? Math.max(0, Math.min(3, Math.floor(stars ?? 0))) : null
  const displayLabel = resultLabel ?? (isFailed ? 'Game Over' : 'You Won')
  // Failure always shows the shattered arc; wins need at least one earned star
  // (the arc art has no zero-star variant, so starless wins keep the icon crest).
  const starArt = isFailed
    ? loseStarsImage
    : earnedStars && earnedStars > 0
      ? WIN_STAR_ART[earnedStars - 1]
      : null
  const statAccent = isFailed ? 'hsl(var(--destructive))' : 'hsl(var(--primary))'

  return (
    <Modal
      open={open}
      title={title}
      className={cn('game-outcome-shell w-full max-w-5xl overflow-hidden', className)}
      overlayClassName="game-outcome-backdrop"
      contentClassName="p-0"
      hideHeader
      onClose={onClose}
    >
      <div className={cn('game-outcome relative overflow-hidden', isFailed ? 'is-failure' : 'is-success')}>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="game-outcome-close"
          onClick={onClose}
          aria-label="Close modal"
        >
          <X className="size-4" />
        </Button>
        {!isFailed ? <GameOutcomeConfetti /> : null}

        <div className="game-outcome-hero relative text-center">
          {starArt ? (
            <img
              className={cn('game-outcome-star-art', !isFailed && 'game-outcome-sparkle-glow')}
              src={starArt}
              alt={isFailed ? 'No stars earned' : `${earnedStars} of 3 stars earned`}
            />
          ) : (
            <div className={cn('game-outcome-icon-crest', !isFailed && 'game-outcome-sparkle-glow')} aria-hidden="true">
              <Icon className="game-outcome-result-icon" />
            </div>
          )}

          <div
            className={cn(
              'game-outcome-title-art game-outcome-headline',
              isFailed && 'is-lost',
              starArt && 'has-star-arc',
            )}
            role="img"
            aria-label={displayLabel}
            style={{ backgroundImage: `url(${titlesImage})` }}
          />
          <h3 className="game-outcome-subline mx-auto mt-2 max-w-xl text-balance text-base font-extrabold sm:text-lg">
            {headline}
          </h3>

          <p className="game-outcome-message mx-auto mt-2 max-w-xl text-sm leading-6">{message}</p>
          {note ? <p className="mx-auto mt-2 max-w-xl text-xs font-medium leading-5 text-warning">{note}</p> : null}
          {badges ? <div className="mt-3 flex flex-wrap justify-center gap-2">{badges}</div> : null}

          {stats && stats.length ? (
            <div className="game-outcome-stat-grid mt-4 grid grid-cols-2 gap-2.5 text-left sm:grid-cols-3">
              {stats.map((stat, index) => (
                <GameOutcomeStatTile
                  key={stat.label}
                  {...stat}
                  accentColor={statAccent}
                  animationDelay={160 + index * 60}
                />
              ))}
            </div>
          ) : null}

          {children}

          {actions ? <div className="game-outcome-actions mt-4 flex flex-wrap justify-center gap-3">{actions}</div> : null}
        </div>
      </div>
    </Modal>
  )
}
