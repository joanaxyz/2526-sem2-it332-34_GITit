/**
 * ⚠ DEV-ONLY DESIGN PREVIEW — registered in the router only when
 * import.meta.env.DEV. Renders the real HomeHubView with fixture data so
 * the hub can be evaluated in a browser without auth or live data.
 *
 * /design-preview/home          → rich mid-progress player
 * /design-preview/home?empty=1  → brand-new user (empty states)
 */
import { useSearchParams } from 'react-router-dom'

import { HomeHubView } from '@/features/home/components/HomeHubView'
import {
  emptyHomeFixture,
  previewGitcoins,
  previewPlayerName,
  richHomeFixture,
} from '@/features/home/preview/fixtures'
import { emptyStatsFixture, richStatsFixture } from '@/features/stats/preview/fixtures'

export function Component() {
  const [params] = useSearchParams()
  const empty = params.get('empty') === '1'
  return (
    <HomeHubView
      home={empty ? emptyHomeFixture : richHomeFixture}
      stats={empty ? emptyStatsFixture : richStatsFixture}
      playerName={empty ? 'newcomer' : previewPlayerName}
      gitcoins={empty ? 0 : previewGitcoins}
    />
  )
}
