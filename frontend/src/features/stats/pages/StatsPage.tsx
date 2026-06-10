import { useQuery } from '@tanstack/react-query'

import { statsApi } from '@/features/stats/api/statsApi'
import { ActivityTrendChart } from '@/features/stats/components/ActivityTrendChart'
import { SkillProfileRadar } from '@/features/stats/components/SkillProfileRadar'
import { StatHighlightCards } from '@/features/stats/components/StatHighlightCards'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function StatsPage() {
  const { data, error, isError, isLoading } = useQuery({
    queryKey: queryKeys.statsSummary,
    queryFn: statsApi.summary,
    staleTime: 5 * 60 * 1000,
  })

  if (isLoading) {
    return (
      <LoadingState
        description="Crunching your skill profile, trends, and milestones."
        label="Loading stats"
        variant="page"
      />
    )
  }
  if (isError) return <ErrorState title="Could not load stats" description={error.message} />
  if (!data) return <ErrorState title="Could not load stats" description="The API returned no stats data." />

  return (
    <div className="flex flex-col gap-5">
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

      <div className="animate-fade-in-up">
        <h1
          className="text-4xl font-extrabold tracking-tight"
          style={{ textShadow: '0 0 30px rgba(0,245,212,0.35), 0 0 60px rgba(0,180,216,0.18)' }}
        >
          Stats
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          How you're growing as a git user — across both adventures and challenges.
        </p>
      </div>

      <div className="animate-fade-in-up" style={{ animationDelay: '80ms' }}>
        <StatHighlightCards summary={data} />
      </div>

      <div
        className="animate-fade-in-up grid grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)] gap-4 max-xl:grid-cols-1"
        style={{ animationDelay: '160ms' }}
      >
        <SkillProfileRadar axes={data.skill_profile} />
        <ActivityTrendChart trend={data.activity_trend} />
      </div>
    </div>
  )
}
