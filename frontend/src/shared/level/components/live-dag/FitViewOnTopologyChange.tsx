import { useEffect, useRef } from 'react'
import { useReactFlow } from 'reactflow'

import { readPreference } from '@/shared/utils/persistentState'

import { MAX_DAG_ZOOM, MIN_DAG_ZOOM } from './constants'

export function FitViewOnTopologyChange({
  layoutSignature,
  fitViewPadding,
  zoomStorageKey,
}: {
  layoutSignature: string
  fitViewPadding: number
  zoomStorageKey?: string
}) {
  const { fitView } = useReactFlow()
  const previousSignature = useRef<string | null>(null)

  useEffect(() => {
    if (previousSignature.current === layoutSignature) return
    previousSignature.current = layoutSignature
    const frameId = window.requestAnimationFrame(() => {
      // Pinning fitView's min/max zoom to the saved level makes it re-center the
      // graph at the learner's chosen zoom instead of refitting to the contents.
      const savedZoom = zoomStorageKey ? readPreference<number | null>(zoomStorageKey, null) : null
      if (savedZoom != null && Number.isFinite(savedZoom)) {
        const zoom = Math.min(Math.max(savedZoom, MIN_DAG_ZOOM), MAX_DAG_ZOOM)
        void fitView({ padding: fitViewPadding, duration: 0, minZoom: zoom, maxZoom: zoom })
      } else {
        void fitView({ padding: fitViewPadding, duration: 0 })
      }
    })
    return () => window.cancelAnimationFrame(frameId)
  }, [fitView, fitViewPadding, layoutSignature, zoomStorageKey])

  return null
}
