import { Suspense, lazy, useCallback, useMemo, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'

import { deriveAchievements, latestAchievement } from '@/features/home/achievements'
import { AchievementsTab } from '@/features/home/components/AchievementsTab'
import { HeroBanner } from '@/features/home/components/HeroBanner'
import { HubTabs } from '@/features/home/components/HubTabs'
import { DEFAULT_HUB_TAB, HUB_TABS, type HubTabId } from '@/features/home/hubTabs'
import { ShowcaseTab } from '@/features/home/components/ShowcaseTab'
import type { HomeSummary } from '@/features/home/types'
import type { StatsSummary } from '@/features/stats/types'
import { LoadingState } from '@/shared/components/LoadingState'

// Stats charts pull in recharts; lazy-load so the hub's default tab doesn't
// pay for it in the entry chunk.
const StatsTab = lazy(() =>
  import('@/features/home/components/StatsTab').then((m) => ({ default: m.StatsTab })),
)

function isHubTabId(value: string | null): value is HubTabId {
  return HUB_TABS.some((t) => t.id === value)
}

/**
 * Game-launcher home hub: environment hero banner up top, then the
 * ‹ Stats · Achievements · Hero Showcase › sub-tab deck. The active tab is
 * mirrored into ?tab= so /stats-era links can deep-link straight to a tab.
 */
export function HomeHubView({
  home,
  stats,
  playerName,
  gitcoins,
}: {
  home: HomeSummary
  stats: StatsSummary
  playerName: string
  gitcoins: number | null
}) {
  const [searchParams, setSearchParams] = useSearchParams()
  const tabParam = searchParams.get('tab')
  const active: HubTabId = isHubTabId(tabParam) ? tabParam : DEFAULT_HUB_TAB
  const deckRef = useRef<HTMLDivElement>(null)

  const achievements = useMemo(() => deriveAchievements(home, stats), [home, stats])
  const latest = useMemo(() => latestAchievement(achievements), [achievements])

  const selectTab = useCallback(
    (id: HubTabId) => {
      setSearchParams(id === DEFAULT_HUB_TAB ? {} : { tab: id }, { replace: true })
    },
    [setSearchParams],
  )

  const viewStats = useCallback(() => {
    selectTab('stats')
    deckRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [selectTab])

  return (
    <div className="-mt-6 flex flex-col">
      <HeroBanner summary={home} playerName={playerName} latest={latest} onViewStats={viewStats} />

      <div ref={deckRef} className="scroll-mt-20 pb-2 pt-4">
        <HubTabs active={active} onSelect={selectTab} />
      </div>

      <div className="mt-5">
        <div
          role="tabpanel"
          id="hub-panel-stats"
          aria-labelledby="hub-tab-stats"
          hidden={active !== 'stats'}
        >
          {active === 'stats' && (
            <Suspense fallback={<LoadingState variant="panel" label="Loading stats" />}>
              <StatsTab home={home} stats={stats} />
            </Suspense>
          )}
        </div>
        <div
          role="tabpanel"
          id="hub-panel-achievements"
          aria-labelledby="hub-tab-achievements"
          hidden={active !== 'achievements'}
        >
          {active === 'achievements' && <AchievementsTab achievements={achievements} />}
        </div>
        <div
          role="tabpanel"
          id="hub-panel-showcase"
          aria-labelledby="hub-tab-showcase"
          hidden={active !== 'showcase'}
        >
          {active === 'showcase' && (
            <ShowcaseTab home={home} playerName={playerName} gitcoins={gitcoins} />
          )}
        </div>
      </div>
    </div>
  )
}
