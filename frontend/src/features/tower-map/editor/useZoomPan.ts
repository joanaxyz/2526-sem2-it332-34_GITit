import { useCallback, useRef, useState, type CSSProperties } from 'react'

import { clamp } from '@/features/tower-map/towerLayoutRandom'

export type ZoomPan = {
  scale: number
  tx: number
  ty: number
  /** Inline transform for the panned/zoomed content layer. */
  style: CSSProperties
  /** Wheel handler (zoom toward the cursor). Attach to the viewport. */
  onWheel: (event: React.WheelEvent) => void
  /** Pointer-down on the viewport background starts a pan drag. */
  onPanStart: (event: React.PointerEvent) => void
  zoomIn: () => void
  zoomOut: () => void
  reset: () => void
}

const MIN = 0.45
const MAX = 2.6
const STEP = 0.0016

/**
 * Lightweight wheel-zoom + drag-pan for the tower editor canvas. No dependency:
 * a transform on the content layer plus a translate. Panning starts only when
 * the pointer goes down on the viewport background (slots stop propagation), so
 * dragging a piece/artifact never fights the pan.
 */
export function useZoomPan(): ZoomPan {
  const [scale, setScale] = useState(1)
  const [tx, setTx] = useState(0)
  const [ty, setTy] = useState(0)
  const drag = useRef<{ x: number; y: number; tx: number; ty: number } | null>(null)

  const onWheel = useCallback((event: React.WheelEvent) => {
    event.preventDefault()
    setScale((current) => clamp(current * (1 - event.deltaY * STEP), MIN, MAX))
  }, [])

  const onPanStart = useCallback(
    (event: React.PointerEvent) => {
      if (event.button !== 0 && event.button !== 1) return
      // Only the background pans — grabbing a piece or artifact must not.
      if ((event.target as HTMLElement).closest('.editor-piece, .editor-slot, .editor-artifact')) return
      drag.current = { x: event.clientX, y: event.clientY, tx, ty }
      const move = (ev: PointerEvent) => {
        if (!drag.current) return
        setTx(drag.current.tx + (ev.clientX - drag.current.x))
        setTy(drag.current.ty + (ev.clientY - drag.current.y))
      }
      const up = () => {
        drag.current = null
        window.removeEventListener('pointermove', move)
        window.removeEventListener('pointerup', up)
      }
      window.addEventListener('pointermove', move)
      window.addEventListener('pointerup', up)
    },
    [tx, ty],
  )

  const zoomIn = useCallback(() => setScale((s) => clamp(s * 1.2, MIN, MAX)), [])
  const zoomOut = useCallback(() => setScale((s) => clamp(s / 1.2, MIN, MAX)), [])
  const reset = useCallback(() => {
    setScale(1)
    setTx(0)
    setTy(0)
  }, [])

  return {
    scale,
    tx,
    ty,
    style: {
      transform: `translate(${tx}px, ${ty}px) scale(${scale})`,
      transformOrigin: 'center top',
    },
    onWheel,
    onPanStart,
    zoomIn,
    zoomOut,
    reset,
  }
}
