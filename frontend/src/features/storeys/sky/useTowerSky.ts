import { useMemo } from 'react'

import { computeSky, type SkyState } from './skyPhases'

export { computeSky } from './skyPhases'
export type { SkyState, SkyVars } from './skyPhases'

/**
 * Memoised wrapper around {@link computeSky}. Use this for the initial render /
 * the clock label; the per-frame auto-cycle in StoreyMapPage calls `computeSky`
 * directly and writes the vars to the sky element to avoid re-rendering React.
 */
export function useTowerSky(timeOfDay: number): SkyState {
  return useMemo(() => computeSky(timeOfDay), [timeOfDay])
}
