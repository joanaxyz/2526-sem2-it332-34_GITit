import { useMemo } from 'react'
import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

import type { HomeSummary } from '@/features/home/types'
import type { StatsSummary } from '@/features/stats/types'
import { SHOP_ROUTE, storyPath } from '@/shared/navigation/routes'

import { HomeAchievementGallery } from './home-stats/HomeAchievementGallery'
import { HomeStatsDashboard } from './home-stats/HomeStatsDashboard'
import { buildHomeStatsModel } from './home-stats/homeStatsModel'

export function HomeStatsView({
  home,
  stats,
  companionRequired,
}: {
  home: HomeSummary
  stats: StatsSummary
  companionRequired: boolean
}) {
  const model = useMemo(() => buildHomeStatsModel(home, stats), [home, stats])

  return (
    <section className="home-overview-grid" aria-label="Player overview">
      <header className="home-overview-continue" data-onboarding="overview-next">
        <div>
          <span>{companionRequired ? 'First step' : 'Recommended next step'}</span>
          <h2>{companionRequired ? 'Choose your first companion' : 'Continue your Git journey'}</h2>
          <p>
            {companionRequired
              ? 'Recruit a companion before entering your first Adventure or Challenge.'
              : 'Return to the story map and pick up from the next available level.'}
          </p>
        </div>
        <Link
          className="home-overview-continue-action"
          to={companionRequired ? `${SHOP_ROUTE}?tab=companions&required=1` : storyPath()}
        >
          {companionRequired ? 'Choose companion' : 'Continue story'}
          <ArrowRight aria-hidden="true" />
        </Link>
      </header>
      <HomeStatsDashboard dashboard={model.dashboard} />
      <HomeAchievementGallery achievements={model.achievements} />
    </section>
  )
}
