import { getSmoothStepPath } from 'reactflow'
import type { EdgeProps } from 'reactflow'

/**
 * Parent -> child connector. pathLength={1} normalises the stroke so the
 * grow-out animation (dag-edge-enter) draws from the parent to the new commit
 * at any edge length, instead of guessing a dash length in CSS.
 */
export function CommitLinkEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style,
}: EdgeProps) {
  const [path] = getSmoothStepPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
    borderRadius: 14,
  })

  return <path id={id} className="react-flow__edge-path" d={path} pathLength={1} fill="none" style={style} />
}
