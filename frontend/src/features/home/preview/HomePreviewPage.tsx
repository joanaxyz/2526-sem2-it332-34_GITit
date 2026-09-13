/**
 * DEV-ONLY DESIGN PREVIEW - registered in the router only when
 * import.meta.env.DEV. Renders the real HomeHubView with fixture data so
 * the hub can be evaluated in a browser without auth or live data.
 *
 * /design-preview/home          -> rich mid-progress player
 * /design-preview/home?empty=1  -> brand-new user (empty states)
 */
import { useQueryClient } from '@tanstack/react-query'
import { useRef } from 'react'
import { useSearchParams } from 'react-router-dom'

import { HomeHubView } from '@/features/home/components/HomeHubView'
import {
  emptyHomeFixture,
  previewPlayerName,
  richHomeFixture,
} from '@/features/home/preview/fixtures'
import {
  emptyPerformanceFixture,
  richPerformanceFixture,
} from '@/features/performance/preview/fixtures'
import { emptyStatsFixture, richStatsFixtureFor } from '@/features/stats/preview/fixtures'
import { activityWindowFromParam } from '@/features/stats/utils/activityWindow'
import { queryKeys } from '@/shared/api/queryKeys'

/** Enough of the shop and spellbook for Profile to render its real contents. */
const PREVIEW_SHOP = {
  active_companion: 'blue',
  purchases_enabled: true,
  items: [
    { slug: 'blue', label: 'Blue', kind: 'companion' as const, price: 0, owned: true, active: true },
    { slug: 'white', label: 'White', kind: 'companion' as const, price: 450, owned: true, active: false },
    { slug: 'black', label: 'Black', kind: 'companion' as const, price: 600, owned: false, active: false },
  ],
}

const PREVIEW_SKILLS = {
  results: [
    { id: 1, slug: 'git-init', base_command: 'git init', title: 'git init', summary: 'Create Git metadata in the current directory.', chapter_number: 1, chapter_title: 'Repository Foundations', chapter_id: 1 },
    { id: 2, slug: 'git-add', base_command: 'git add', title: 'git add', summary: 'Stage working directory changes.', chapter_number: 1, chapter_title: 'Repository Foundations', chapter_id: 1 },
    { id: 3, slug: 'git-commit', base_command: 'git commit', title: 'git commit', summary: 'Record the staged snapshot.', chapter_number: 1, chapter_title: 'Repository Foundations', chapter_id: 1 },
    { id: 4, slug: 'git-log', base_command: 'git log', title: 'git log', summary: 'Inspect commit history.', chapter_number: 2, chapter_title: 'Branching Basics', chapter_id: 2 },
    { id: 5, slug: 'git-branch', base_command: 'git branch', title: 'git branch', summary: 'Inspect and create branches.', chapter_number: 2, chapter_title: 'Branching Basics', chapter_id: 2 },
    { id: 6, slug: 'git-merge', base_command: 'git merge', title: 'git merge', summary: 'Combine another branch into this one.', chapter_number: 3, chapter_title: 'Merging & Conflicts', chapter_id: 3 },
  ],
}

export function Component() {
  const [params] = useSearchParams()
  const empty = params.get('empty') === '1'
  const queryClient = useQueryClient()

  // The module band fetches its own summary rather than taking it as a prop, so
  // the preview seeds the cache before that band mounts. Without this the
  // preview can only ever render the band's "unavailable" state. Re-seeded when
  // ?empty flips, which swaps fixtures without remounting this route.
  const seededEmpty = useRef<boolean | null>(null)
  if (seededEmpty.current !== empty) {
    seededEmpty.current = empty
    queryClient.setQueryData(
      queryKeys.performanceSummary,
      empty ? emptyPerformanceFixture : richPerformanceFixture,
    )
    // Profile's companion, roster and spellbook are fetched the same way, so
    // the preview seeds them too rather than showing three error states.
    queryClient.setQueryData(
      queryKeys.shopCatalog,
      empty ? { ...PREVIEW_SHOP, active_companion: null, items: PREVIEW_SHOP.items.map((item) => ({ ...item, owned: false, active: false })) } : PREVIEW_SHOP,
    )
    queryClient.setQueryData(queryKeys.learnedSkills, empty ? { results: [] } : PREVIEW_SKILLS)
  }

  return (
    <HomeHubView
      home={empty ? emptyHomeFixture : richHomeFixture}
      stats={empty ? emptyStatsFixture : richStatsFixtureFor(activityWindowFromParam(params.get('range')))}
      playerName={empty ? 'newcomer' : previewPlayerName}
    />
  )
}
