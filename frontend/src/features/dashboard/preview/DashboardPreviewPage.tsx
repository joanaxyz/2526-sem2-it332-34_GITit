/**
 * ⚠ DEV-ONLY DESIGN PREVIEW — registered in the router only when
 * import.meta.env.DEV. Renders the real DashboardView with fixture data so
 * the redesign can be evaluated in a browser without auth or live data.
 *
 * /design-preview/dashboard          → rich mid-progress player
 * /design-preview/dashboard?empty=1  → brand-new user (empty states)
 */
import { useSearchParams } from 'react-router-dom'

import { DashboardView } from '@/features/dashboard/components/DashboardView'
import {
  emptyDashboardFixture,
  previewGitcoins,
  previewPlayerName,
  richDashboardFixture,
} from '@/features/dashboard/preview/fixtures'

export function Component() {
  const [params] = useSearchParams()
  const empty = params.get('empty') === '1'
  return (
    <DashboardView
      data={empty ? emptyDashboardFixture : richDashboardFixture}
      playerName={empty ? 'newcomer' : previewPlayerName}
      gitcoins={empty ? 0 : previewGitcoins}
    />
  )
}
