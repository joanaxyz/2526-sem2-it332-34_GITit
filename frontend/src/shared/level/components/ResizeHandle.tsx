import type {
  KeyboardEvent as ReactKeyboardEvent,
  PointerEvent as ReactPointerEvent,
} from 'react'
import { GripHorizontal, GripVertical } from 'lucide-react'

import { cn } from '@/shared/utils/cn'

/** Draggable and keyboard-operable separator between two resizable workspace panes. */
export function ResizeHandle({
  label,
  orientation,
  className,
  onPointerDown,
  onKeyboardResize,
  onReset,
}: {
  label: string
  orientation: 'horizontal' | 'vertical'
  className?: string
  onPointerDown: (event: ReactPointerEvent<HTMLDivElement>) => void
  onKeyboardResize?: (delta: number) => void
  onReset?: () => void
}) {
  const isVertical = orientation === 'vertical'
  const Icon = isVertical ? GripVertical : GripHorizontal

  function handleKeyDown(event: ReactKeyboardEvent<HTMLDivElement>) {
    if (event.key === 'Home' || event.key === 'End') {
      if (!onReset) return
      event.preventDefault()
      onReset()
      return
    }

    if (!onKeyboardResize) return
    const delta = isVertical
      ? event.key === 'ArrowLeft'
        ? -1
        : event.key === 'ArrowRight'
          ? 1
          : 0
      : event.key === 'ArrowUp'
        ? 1
        : event.key === 'ArrowDown'
          ? -1
          : 0

    if (!delta) return
    event.preventDefault()
    onKeyboardResize(delta)
  }

  return (
    <div
      aria-label={label}
      aria-orientation={orientation}
      className={cn('resize-handle', isVertical ? 'resize-handle--vertical' : 'resize-handle--horizontal', className)}
      role="separator"
      tabIndex={0}
      title={`${label}. Use arrow keys to adjust; double-click to reset.`}
      onDoubleClick={onReset}
      onKeyDown={handleKeyDown}
      onPointerDown={onPointerDown}
    >
      <span className="resize-handle__line" />
      <span className="resize-handle__grip">
        <Icon className="size-3" />
      </span>
    </div>
  )
}
