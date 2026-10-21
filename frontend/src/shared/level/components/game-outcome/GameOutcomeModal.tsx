import type { ComponentType, ReactNode } from 'react'
import { X } from 'lucide-react'

import titlesImage from '@/assets/images/battle-outcome/titles.webp'
import { Modal } from '@/shared/components/Modal'
import { cn } from '@/shared/utils/cn'
import { useLazyImage } from '@/shared/utils/useLazyImage'
import { normalizeStarScore } from '@/shared/level/utils/starScore'

import { GameOutcomeConfetti } from './GameOutcomeConfetti'
import { GameOutcomeStatTile } from './GameOutcomeStatTile'

// A single outcome shows exactly one star image (the loss art, or one of
// three win tiers), so each is imported lazily instead of bundling every variant
// upfront. `titlesImage` above is shown on every outcome, so it stays a
// normal static import.
const STAR_ART_LOADERS: Record<string, () => Promise<{ default: string }>> = {
  lose: () => import('@/assets/images/battle-outcome/lose-0.webp'),
  'win-1': () => import('@/assets/images/battle-outcome/win-1.webp'),
  'win-2': () => import('@/assets/images/battle-outcome/win-2.webp'),
  'win-3': () => import('@/assets/images/battle-outcome/win-3.webp'),
}

export type GameOutcomeStat = {
  label: string
  numerator: number
  denominator?: number
  suffix?: string
  helper: string
  /** Per-tile accent color; falls back to the tone's accent (neon blue / window amber). */
  accentColor?: string
  /** Shows a "Target met" chip in the tile header. */
  targetMet?: boolean
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
  showStars = true,
  level,
  badges,
  headline,
  message,
  note,
  stats,
  children,
  actions,
  headerActions,
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
  /** Assessments record a first outcome without awarding a star grade. */
  showStars?: boolean
  /** Names the level the outcome belongs to, e.g. "Level 3" and its title. */
  level?: { label: string; title: string }
  badges?: ReactNode
  headline: string
  message: ReactNode
  /** Optional emphasised aside under the message. */
  note?: ReactNode
  stats?: GameOutcomeStat[]
  /** Surface-specific section rendered between the stats and the actions. */
  children?: ReactNode
  actions?: ReactNode
  /** Icon-button actions rendered in the top-right header cluster (alongside the close button). */
  headerActions?: ReactNode
  className?: string
}) {
  const isFailed = tone === 'failure'
  const earnedStars = Number.isFinite(stars) ? normalizeStarScore(stars) : null
  const displayLabel = resultLabel ?? (isFailed ? 'Game Over' : 'You Won')
  // Graded failures show unlit stars; assessments keep the icon crest.
  const starArtKey = !showStars ? null : isFailed ? 'lose' : earnedStars && earnedStars > 0 ? `win-${earnedStars}` : null
  const starArt = useLazyImage(starArtKey, STAR_ART_LOADERS)
  const defaultAccent = isFailed ? 'hsl(var(--warning))' : 'hsl(var(--primary))'

  return (
    <Modal
      open={open}
      title={title}
      className={cn('game-outcome-shell', className)}
      overlayClassName="game-outcome-backdrop"
      contentClassName="p-0"
      hideHeader
      onClose={onClose}
    >
      <div className={cn('game-outcome relative overflow-hidden', isFailed ? 'is-failure' : 'is-success')}>
        <div className="game-outcome-header-actions">
          {headerActions ? (
            <>
              {headerActions}
              <span className="game-outcome-header-divider" aria-hidden="true" />
            </>
          ) : null}
          <button
            type="button"
            className="game-outcome-header-btn"
            onClick={onClose}
            aria-label="Close modal"
          >
            <X className="size-3.5" />
          </button>
        </div>
        {!isFailed ? <GameOutcomeConfetti /> : null}

        <div className="game-outcome-hero relative text-center">
          {starArt ? (
            <img
              className={cn('game-outcome-star-art', isFailed ? 'is-lost' : 'game-outcome-sparkle-glow')}
              src={starArt}
              width={1774}
              height={887}
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
            )}
            role="img"
            aria-label={displayLabel}
            style={{ backgroundImage: `url(${titlesImage})` }}
          />
          <h3 className="game-outcome-subline">
            <span className="game-outcome-subline-rule" aria-hidden="true" />
            <span className="text-balance">{headline}</span>
            <span className="game-outcome-subline-rule is-end" aria-hidden="true" />
          </h3>

          {level ? (
            <p className="game-outcome-level">
              <span className="game-outcome-level-label">{level.label}</span>
              <span className="game-outcome-level-title">{level.title}</span>
            </p>
          ) : null}

          {badges ? <div className="game-outcome-badges">{badges}</div> : null}
          <p className="game-outcome-message">{message}</p>
          {note ? <p className="game-outcome-note">{note}</p> : null}

          {stats && stats.length ? (
            <div className="game-outcome-stat-grid">
              {stats.map((stat, index) => (
                <GameOutcomeStatTile
                  key={stat.label}
                  {...stat}
                  accentColor={stat.accentColor ?? defaultAccent}
                  animationDelay={160 + index * 60}
                />
              ))}
            </div>
          ) : null}

          {children}

          {actions ? <div className="game-outcome-actions">{actions}</div> : null}
        </div>
      </div>
    </Modal>
  )
}
