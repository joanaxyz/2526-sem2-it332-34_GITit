/**
 * ⚠ DEV-ONLY DESIGN PREVIEW — registered in the router only when
 * import.meta.env.DEV. Renders the real StatsView with fixture data so the
 * redesign can be evaluated in a browser without auth or live data.
 *
 * /design-preview/stats          → rich mid-progress player
 * /design-preview/stats?empty=1  → brand-new user (empty states)
 */
import { useSearchParams } from 'react-router-dom'

import { StatsView } from '@/features/stats/components/StatsView'
import { emptyStatsFixture, richStatsFixture } from '@/features/stats/preview/fixtures'

export function Component() {
  const [params] = useSearchParams()
  const empty = params.get('empty') === '1'
  return <StatsView data={empty ? emptyStatsFixture : richStatsFixture} />
}
