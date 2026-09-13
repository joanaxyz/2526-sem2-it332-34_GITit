import { useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'

import {
  DEFAULT_ACTIVITY_WINDOW,
  activityWindowFromParam,
  type ActivityWindow,
} from '@/features/stats/utils/activityWindow'

/**
 * The activity band's span, held in the URL (`?range=`).
 *
 * The control that sets it and the query that fetches it sit on opposite sides
 * of the screen's component tree, so neither owns the state: both read this.
 * Keeping it in the URL also means a chosen span survives a reload and travels
 * in a shared link. The default span is written as the absence of the
 * parameter, so the canonical Home URL stays clean.
 */
export function useActivityWindow(): [ActivityWindow, (next: ActivityWindow) => void] {
  const [searchParams, setSearchParams] = useSearchParams()
  const activityWindow = activityWindowFromParam(searchParams.get('range'))

  const selectActivityWindow = useCallback(
    (next: ActivityWindow) => {
      setSearchParams(
        (current) => {
          const nextParams = new URLSearchParams(current)
          if (next === DEFAULT_ACTIVITY_WINDOW) nextParams.delete('range')
          else nextParams.set('range', next)
          return nextParams
        },
        { replace: true },
      )
    },
    [setSearchParams],
  )

  return [activityWindow, selectActivityWindow]
}
