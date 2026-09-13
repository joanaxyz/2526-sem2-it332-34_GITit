import { useMemo } from 'react'

import type { HomeView } from '@/features/home/components/home-hub/homeViews'
import type { HomeSummary } from '@/features/home/types'
import type { StatsSummary } from '@/features/stats/types'
import { useActivityWindow } from '@/features/stats/hooks/useActivityWindow'

import { HomeAchievementGallery } from './home-stats/HomeAchievementGallery'
import { HomeProgressPanel } from './home-stats/HomeProgressPanel'
import { HomeResultsPanel } from './home-stats/HomeResultsPanel'
import { HomeSkillsPanel } from './home-stats/HomeSkillsPanel'
import { buildHomeStatsModel } from './home-stats/homeStatsModel'

/**
 * The data categories of Home. Profile is the third category and is composed by
 * the hub instead, because it owns companion and rank state rather than summary
 * data. Whichever category is active, exactly one panel set renders.
 *
 * Progress is one plaque of two bands: where the account stands, then the record
 * behind that standing. They were separate categories until each discovered it
 * was quoting the other's numbers back.
 */
export function HomeStatsView({
  home,
  stats,
  view,
}: {
  home: HomeSummary
  stats: StatsSummary
  view: HomeView
}) {
  const model = useMemo(() => buildHomeStatsModel(home, stats), [home, stats])
  // The band renders the span control; HomePage reads the same URL parameter to
  // scope its request, so the two can never disagree about what is on screen.
  const [activityWindow, selectActivityWindow] = useActivityWindow()

  return (
    <section
      className={`home-overview-grid${view === 'skills' ? ' is-split' : ''}`}
      aria-label="Player overview"
    >
      {view === 'progress' ? (
        <article className="home-overview-standing" aria-label="Progress">
          <HomeProgressPanel
            activityWindow={activityWindow}
            onSelectActivityWindow={selectActivityWindow}
            progress={model.progress}
          />
          <HomeResultsPanel results={model.results} />
        </article>
      ) : null}
      {view === 'skills' ? (
        <>
          <HomeSkillsPanel skills={model.skills} />
          <HomeAchievementGallery achievements={model.achievements} />
        </>
      ) : null}
    </section>
  )
}
