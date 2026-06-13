import type { PointerEvent as ReactPointerEvent } from 'react'
import { GripHorizontal, GripVertical } from 'lucide-react'

import { cn } from '@/shared/utils/cn'

/** Draggable separator between two resizable workspace panes. */
export function ResizeHandle({
  label,
  orientation,
  className,
  onPointerDown,
}: {
  label: string
  orientation: 'horizontal' | 'vertical'
  className?: string
  onPointerDown: (event: ReactPointerEvent<HTMLDivElement>) => void
}) {
  const isVertical = orientation === 'vertical'
  const Icon = isVertical ? GripVertical : GripHorizontal

  return (
    <div
      aria-label={label}
      aria-orientation={orientation}
      className={cn(
        'group relative z-10 flex shrink-0 items-center justify-center',
        isVertical ? 'h-full cursor-col-resize px-1' : 'w-full cursor-row-resize py-1',
        className,
      )}
      role="separator"
      onPointerDown={onPointerDown}
    >
      <span
        className={cn(
          'rounded-full bg-border/70 transition-colors group-hover:bg-primary/70 group-active:bg-primary',
          isVertical ? 'h-full w-px' : 'h-px w-full',
        )}
      />
      <span className="absolute grid size-5 place-items-center rounded-full border border-border bg-background/95 text-muted-foreground shadow-sm transition-colors group-hover:border-primary/60 group-hover:text-primary group-active:text-primary">
        <Icon className="size-3" />
      </span>
    </div>
  )
}
