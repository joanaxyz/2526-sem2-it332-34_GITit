import { useEffect, useRef } from 'react'
import { useReactFlow, useStore } from 'reactflow'
import type { Edge, Node } from 'reactflow'

import { readPreference } from '@/shared/utils/persistentState'

import { MAX_DAG_ZOOM, MIN_DAG_ZOOM } from './constants'

export function FitViewOnTopologyChange({
  fitSignature,
  topologySignature,
  fitViewPadding,
  zoomStorageKey,
}: {
  /** Includes presentation inputs such as layout direction. */
  fitSignature: string
  /** Commit/edge signature mirrored by React Flow's internal nodes. */
  topologySignature: string
  fitViewPadding: number
  zoomStorageKey?: string
}) {
  const { fitView, getEdges, getNodes } = useReactFlow()
  const viewportSizeSignature = useStore(
    (state) => `${Math.round(state.width)}x${Math.round(state.height)}`,
  )
  const previousSignature = useRef<string | null>(null)
  const currentSignature = `${fitSignature}:${viewportSizeSignature}:${fitViewPadding}`

  useEffect(() => {
    if (previousSignature.current === currentSignature) return
    let frameId = 0
    let attempts = 0
    let consecutiveReadyFrames = 0
    let cancelled = false

    const fitCurrentTopology = () => {
      if (cancelled) return
      attempts += 1

      // React Flow applies controlled nodes after this child renders. Do not
      // consume the signature while its internal store still has the previous
      // topology, otherwise the new tail/branch can land outside the viewport.
      if (flowTopologySignature(getNodes(), getEdges()) === topologySignature) {
        consecutiveReadyFrames += 1
      } else {
        consecutiveReadyFrames = 0
      }
      if (consecutiveReadyFrames < 2 && attempts < 8) {
        frameId = window.requestAnimationFrame(fitCurrentTopology)
        return
      }
      if (consecutiveReadyFrames === 0) return
      previousSignature.current = currentSignature

      // Pinning fitView's min/max zoom to the saved level makes it re-center the
      // graph at the learner's chosen zoom instead of refitting to the contents.
      const savedZoom = zoomStorageKey ? readPreference<number | null>(zoomStorageKey, null) : null
      if (savedZoom != null && Number.isFinite(savedZoom)) {
        const zoom = Math.min(Math.max(savedZoom, MIN_DAG_ZOOM), MAX_DAG_ZOOM)
        void fitView({ padding: fitViewPadding, duration: 0, minZoom: zoom, maxZoom: zoom })
      } else {
        void fitView({ padding: fitViewPadding, duration: 0 })
      }
    }

    frameId = window.requestAnimationFrame(fitCurrentTopology)
    return () => {
      cancelled = true
      window.cancelAnimationFrame(frameId)
    }
  }, [currentSignature, fitView, fitViewPadding, getEdges, getNodes, topologySignature, zoomStorageKey])

  return null
}

function flowTopologySignature(nodes: Node[], edges: Edge[]): string {
  if (nodes.length === 1 && nodes[0]?.id === '__empty__') return 'empty'
  const nodeIds = nodes.map((node) => node.id).sort().join(',')
  const connections = edges.map((edge) => `${edge.source}->${edge.target}`).sort().join(',')
  return `${nodeIds}|${connections}`
}
