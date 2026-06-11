import { EconomyChart } from '@/features/home/components/EconomyChart'
import { KpiStrip } from '@/features/home/components/KpiStrip'
import { RecentRuns } from '@/features/home/components/RecentRuns'
import { WeeklyActivityBars } from '@/features/home/components/WeeklyActivityBars'
import type { HomeSummary } from '@/features/home/types'
import { HeadlineBand } from '@/features/stats/components/HeadlineBand'
import { MetricGrid } from '@/features/stats/components/MetricGrid'
import { SkillProfileRadar } from '@/features/stats/components/SkillProfileRadar'
import type { StatsSummary } from '@/features/stats/types'

/**
 * Stats sub-tab: focused analytics surface. Streak and storey record live in
 * other home/tower surfaces; this tab keeps activity, performance, mastery,
 * and recent run evidence in one clean readout.
 */
export function StatsTab({ home, stats }: { home: HomeSummary; stats: StatsSummary }) {
  return (
    <section className="stats-deck flex flex-col gap-10" aria-label="Performance statistics">
      <div
        className="animate-fade-in-up grid grid-cols-[minmax(0,1.55fr)_minmax(20rem,0.8fr)] items-stretch gap-x-12 gap-y-10 max-lg:grid-cols-1"
      >
        <EconomyChart trend={stats.activity_trend} />
        <WeeklyActivityBars trend={stats.activity_trend} />
      </div>

      <div className="animate-fade-in-up" style={{ animationDelay: '90ms' }}>
        <HeadlineBand summary={stats} />
      </div>

      <div
        className="animate-fade-in-up grid grid-cols-[minmax(24rem,0.95fr)_minmax(0,1.05fr)] items-stretch gap-x-12 gap-y-10 max-xl:grid-cols-1"
        style={{ animationDelay: '170ms' }}
      >
        <SkillProfileRadar axes={stats.skill_profile} />
        <div className="flex flex-col gap-9">
          <MetricGrid summary={stats} />
          <KpiStrip summary={home} />
        </div>
      </div>

      <div className="animate-fade-in-up" style={{ animationDelay: '250ms' }}>
        <RecentRuns summary={home} />
      </div>
    </section>
  )
}
