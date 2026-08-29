import type { ReactNode } from 'react'

import { cn } from '@/shared/utils/cn'

export function GameplayBattlePanel({
  className,
  children,
}: {
  className?: string
  children: ReactNode
}) {
  return (
    <div className={cn('gameplay-battle-panel', className)}>
      {children}
    </div>
  )
}
