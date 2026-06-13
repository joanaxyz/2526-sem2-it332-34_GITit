import { useCallback } from 'react'
import type { PointerEvent as ReactPointerEvent, RefObject } from 'react'

/**
 * Pointer-drag resize handler shared by the workspace's split panes.
 *
 * Each pane resize is the same gesture: measure a container's bounds, then map
 * the pointer position to a ratio while listening on `window` (so the drag
 * survives the cursor leaving the handle) and locking the page cursor until
 * release. Only the container ref, the cursor, and the position→ratio mapping
 * differ — those are the arguments here; everything else lives once.
 */
export function useDragResize(
  containerRef: RefObject<HTMLElement | null>,
  cursor: 'row-resize' | 'col-resize',
  apply: (event: { clientX: number; clientY: number }, bounds: DOMRect) => void,
) {
  return useCallback(
    (event: ReactPointerEvent<HTMLElement>) => {
      const bounds = containerRef.current?.getBoundingClientRect()
      if (!bounds) return
      event.preventDefault()

      const handleMove = (move: PointerEvent) => apply(move, bounds)
      const handleUp = () => {
        window.removeEventListener('pointermove', handleMove)
        document.body.style.cursor = ''
        document.body.style.userSelect = ''
      }

      document.body.style.cursor = cursor
      document.body.style.userSelect = 'none'
      apply(event, bounds)
      window.addEventListener('pointermove', handleMove)
      window.addEventListener('pointerup', handleUp, { once: true })
    },
    [containerRef, cursor, apply],
  )
}
