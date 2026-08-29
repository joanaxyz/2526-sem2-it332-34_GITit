import * as React from 'react'

import { cn } from '@/shared/utils/cn'

type GamePanelProps = {
  /** Render as section, div, or button (for interactive panel cards). */
  as?: 'div' | 'section' | 'button'
  /** Small caps label above the title. */
  eyebrow?: React.ReactNode
  /** Display title inside the panel header. */
  title?: React.ReactNode
  /** Optional trailing control in the header row. */
  action?: React.ReactNode
} & Omit<React.HTMLAttributes<HTMLElement>, 'title'> &
  Pick<React.ButtonHTMLAttributes<HTMLButtonElement>, 'type' | 'disabled'>

/**
 * Shared gamified HUD container: glassy dark fill on a rounded slab with one
 * thin cyan hairline (the story-map border). Used across Home, Story Map, Shop,
 * and Challenge surfaces.
 */
export function GamePanel({
  as: Component = 'div',
  className,
  children,
  eyebrow,
  title,
  action,
  ...props
}: GamePanelProps) {
  const hasHeader = Boolean(eyebrow || title || action)

  return (
    <Component className={cn('game-panel', className)} {...props}>
      {hasHeader ? (
        <header className="game-panel-head">
          <div className="min-w-0">
            {eyebrow ? <p className="game-panel-eyebrow">{eyebrow}</p> : null}
            {title ? <h2 className="game-panel-title">{title}</h2> : null}
          </div>
          {action ? <div className="game-panel-action">{action}</div> : null}
        </header>
      ) : null}
      {children}
    </Component>
  )
}
