import type { ReactNode } from 'react'

import { cn } from '@/shared/utils/cn'

export function GameplayBattlePanel({
  variant,
  className,
  children,
}: {
  variant: 'adventure' | 'challenge'
  className?: string
  children: ReactNode
}) {
  return (
    <div
      className={cn(
        'gameplay-battle-panel',
        `gameplay-battle-panel--${variant}`,
        className,
      )}
    >
      {children}
    </div>
  )
}
