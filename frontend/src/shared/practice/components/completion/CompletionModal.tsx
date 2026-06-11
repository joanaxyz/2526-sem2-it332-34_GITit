import type { ComponentType, ReactNode } from 'react'

import { Modal } from '@/shared/components/Modal'
import { cn } from '@/shared/utils/cn'

import { CompletionConfetti } from './CompletionConfetti'
import { CompletionStatTile } from './CompletionStatTile'
import { TILE_ACCENTS } from './tileAccents'

export type CompletionStat = {
  label: string
  numerator: number
  denominator?: number
  suffix?: string
  helper: string
  icon?: ComponentType<{ className?: string }>
}

/**
 * Shared celebration / outcome modal for the challenge and adventure practice
 * surfaces. It owns the chrome that should stay identical across both — the
 * confetti, the glowing status crest, the headline/message block, and the
 * animated stat grid — while leaving every caller-specific bit (badges, extra
 * sections, footer actions) as slots so each surface keeps its own flavour.
 *
 * Stat accents and entrance delays are assigned by position here so callers only
 * describe *what* a stat is, never how it animates.
 */
export function CompletionModal({
  open,
  onClose,
  title,
  tone = 'success',
  icon: Icon,
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
  badges?: ReactNode
  headline: string
  message: ReactNode
  /** Optional emphasised aside under the message (e.g. a looped-variant warning). */
  note?: ReactNode
  stats?: CompletionStat[]
  /** Surface-specific section rendered between the stats and the actions. */
  children?: ReactNode
  actions?: ReactNode
  className?: string
}) {
  const isFailed = tone === 'failure'

  return (
    <Modal
      open={open}
      title={title}
      className={cn(
        'w-full max-w-2xl overflow-hidden bg-card',
        isFailed
          ? 'border-destructive/30 shadow-[0_28px_110px_rgba(248,113,113,0.16)]'
          : 'border-primary/30 shadow-[0_28px_110px_rgba(0,245,212,0.18)]',
        className,
      )}
      contentClassName="p-0"
      onClose={onClose}
    >
      <div className="relative overflow-hidden">
        {!isFailed ? <CompletionConfetti /> : null}

        <div className="relative px-5 pb-5 pt-5 text-center">
          <div
            className={cn(
              'mx-auto grid size-12 place-items-center rounded-full border',
              !isFailed && 'completion-sparkle-glow',
              isFailed
                ? 'border-destructive/30 bg-destructive/10 shadow-[0_0_42px_rgba(248,113,113,0.16)]'
                : 'border-primary/40 bg-primary/10 shadow-[0_0_32px_rgba(0,245,212,0.35),0_0_60px_rgba(0,180,216,0.18)]',
            )}
          >
            <Icon className={cn('size-6', isFailed ? 'text-destructive' : 'text-primary')} />
          </div>

          {badges ? <div className="mt-3 flex flex-wrap justify-center gap-2">{badges}</div> : null}

          <h3 className="completion-headline mx-auto mt-3 max-w-xl text-balance text-xl font-extrabold tracking-tight sm:text-2xl">
            {headline}
          </h3>
          <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-muted-foreground">{message}</p>
          {note ? <p className="mx-auto mt-2 max-w-xl text-xs font-medium leading-5 text-warning">{note}</p> : null}

          {stats && stats.length ? (
            <div className="mt-4 grid grid-cols-2 gap-2.5 text-left sm:grid-cols-3 max-[420px]:grid-cols-1">
              {stats.map((stat, index) => (
                <CompletionStatTile
                  key={stat.label}
                  {...stat}
                  accentColor={TILE_ACCENTS[index % TILE_ACCENTS.length]}
                  animationDelay={160 + index * 60}
                />
              ))}
            </div>
          ) : null}

          {children}

          {actions ? <div className="mt-5 flex flex-wrap justify-center gap-3">{actions}</div> : null}
        </div>
      </div>
    </Modal>
  )
}
