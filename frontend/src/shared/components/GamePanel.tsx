import * as React from 'react'

import { cn } from '@/shared/utils/cn'

/**
 * Glassy neon HUD panel with a top light-bar, scanline texture and engraved
 * corner brackets. The shared gamified surface for the Home hub.
 */
export function GamePanel({
  className,
  children,
  corners = true,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & { corners?: boolean }) {
  return (
    <div className={cn('game-panel', className)} {...props}>
      {corners && (
        <>
          <span className="game-corner game-corner--tl" />
          <span className="game-corner game-corner--tr" />
          <span className="game-corner game-corner--bl" />
          <span className="game-corner game-corner--br" />
        </>
      )}
      {children}
    </div>
  )
}
