import type { CSSProperties } from 'react'

import { cn } from '@/shared/utils/cn'

const containerClass = {
  screen: 'min-h-screen bg-background p-4',
  page: 'min-h-[calc(100vh-8rem)] p-4',
  panel: 'min-h-40 p-4',
  inline: 'min-h-28 py-4',
  compact: 'min-h-0 py-1',
} as const

type GlyphLoadingVariant = keyof typeof containerClass

export function GlyphLoadingState({
  label = 'Loading',
  description,
  variant = 'panel',
  className,
}: {
  label?: string
  description?: string
  variant?: GlyphLoadingVariant
  className?: string
}) {
  const chars = Array.from(label)
  const isCompact = variant === 'compact'
  const isSmall = variant === 'inline' || variant === 'compact'
  const statusLabel = description ? `${label}. ${description}` : label

  return (
    <div
      aria-label={statusLabel}
      aria-live="polite"
      className={cn(
        'relative isolate flex items-center justify-center overflow-hidden text-center',
        containerClass[variant],
        className,
      )}
      role="status"
    >
      <div className="relative flex w-full max-w-md flex-col items-center gap-3">
        <div
          aria-hidden="true"
          className={cn(
            'git-it-glyph-loader',
            isSmall && 'git-it-glyph-loader--small',
            isCompact && 'git-it-glyph-loader--compact',
          )}
        >
          <span className="git-it-glyph-loader__ring" />
          <span className="git-it-glyph-loader__orbit" />

          <div className="git-it-glyph-loader__path">
            <span className="git-it-glyph-loader__node git-it-glyph-loader__node--a" />
            <span className="git-it-glyph-loader__node git-it-glyph-loader__node--b" />
            <span className="git-it-glyph-loader__node git-it-glyph-loader__node--c" />
          </div>

          <p className="git-it-glyph-loader__text">
            {chars.map((char, index) => (
              <span
                className={cn('git-it-glyph-loader__char', char === ' ' && 'is-space')}
                key={`${char}-${index}`}
                style={{ '--glyph-char-delay': `${index * 0.045}s` } as CSSProperties}
              >
                {char}
              </span>
            ))}
            <span className="git-it-glyph-loader__cursor" />
          </p>

          <span className="git-it-glyph-loader__spark git-it-glyph-loader__spark--a" />
          <span className="git-it-glyph-loader__spark git-it-glyph-loader__spark--b" />
          <span className="git-it-glyph-loader__spark git-it-glyph-loader__spark--c" />
        </div>

        {description ? (
          <p className={cn('mx-auto max-w-xs text-sm leading-5 text-muted-foreground', isCompact && 'hidden')}>
            {description}
          </p>
        ) : null}
      </div>
    </div>
  )
}