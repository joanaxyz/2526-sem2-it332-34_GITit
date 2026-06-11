import { ActivityTrendChart } from '@/features/stats/components/ActivityTrendChart'
import { HeadlineBand } from '@/features/stats/components/HeadlineBand'
import { MetricGrid } from '@/features/stats/components/MetricGrid'
import { SkillProfileRadar } from '@/features/stats/components/SkillProfileRadar'
import type { StatsSummary } from '@/features/stats/types'

/**
 * Pure performance-profile composition: headline band, then the skill radar
 * flanked by milestone metrics and the activity trend. Data arrives via
 * props so the same view powers the live page and the dev design previews.
 */
export function StatsView({ data }: { data: StatsSummary }) {
  return (
    <div className="flex flex-col gap-4">
      {/* Animated background — same aurora orbs as the rest of the app */}
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div
          className="absolute"
          style={{
            width: '50%', height: '55%', left: '-6%', top: '18%',
            background: 'radial-gradient(ellipse at center, rgba(0,245,212,0.04) 0%, transparent 70%)',
            filter: 'blur(50px)',
            animation: 'bg-drift 20s ease-in-out infinite alternate',
          }}
        />
        <div
          className="absolute"
          style={{
            width: '42%', height: '48%', right: '-4%', bottom: '8%',
            background: 'radial-gradient(ellipse at center, rgba(0,180,216,0.03) 0%, transparent 70%)',
            filter: 'blur(50px)',
            animation: 'bg-drift 26s ease-in-out infinite alternate-reverse',
          }}
        />
      </div>

      <div className="animate-fade-in-up flex items-end justify-between gap-4">
        <div>
          <p className="font-mono text-[0.62rem] font-semibold uppercase tracking-[0.26em] text-aurora-blue/80">
            Performance Profile
          </p>
          <h1
            className="mt-1 text-3xl font-extrabold tracking-tight"
            style={{ textShadow: '0 0 30px rgba(0,245,212,0.35), 0 0 60px rgba(0,180,216,0.18)' }}
          >
            Stats
          </h1>
        </div>
        <p className="mb-1 max-w-xs text-right text-xs text-muted-foreground max-md:hidden">
          How you&apos;re growing as a git user — across adventures and challenges.
        </p>
      </div>

      <div className="animate-fade-in-up" style={{ animationDelay: '80ms' }}>
        <HeadlineBand summary={data} />
      </div>

      <div
        className="animate-fade-in-up grid grid-cols-[minmax(0,1fr)_minmax(0,1.25fr)] items-stretch gap-4 max-xl:grid-cols-1"
        style={{ animationDelay: '160ms' }}
      >
        <SkillProfileRadar axes={data.skill_profile} />
        <div className="flex flex-col gap-4">
          <MetricGrid summary={data} />
          <ActivityTrendChart trend={data.activity_trend} />
        </div>
      </div>
    </div>
  )
}
