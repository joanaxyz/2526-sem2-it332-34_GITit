import { useQuery } from '@tanstack/react-query'

import { dashboardApi } from '@/features/dashboard/api/dashboardApi'
import { CurrentTrackCard } from '@/features/dashboard/components/CurrentTrackCard'
import { FirstAttemptStars } from '@/features/dashboard/components/FirstAttemptStars'
import { RecentActivityList } from '@/features/dashboard/components/RecentActivityList'
import { RetryTrendCard } from '@/features/dashboard/components/RetryTrendCard'
import { StreakCard } from '@/features/dashboard/components/StreakCard'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function DashboardPage() {
  const { data, error, isError, isLoading } = useQuery({
    queryKey: queryKeys.dashboardSummary,
    queryFn: dashboardApi.summary,
    staleTime: 5 * 60 * 1000,
  })

  if (isLoading) return <LoadingState label="Loading dashboard" />
  if (isError) return <ErrorState title="Could not load dashboard" description={error.message} />
  if (!data) return <ErrorState title="Could not load dashboard" description="The API returned no dashboard data." />

  return (
    <div className="flex flex-col gap-5">
      {/* Animated background — slow-drifting aurora orbs, dashboard-only */}
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div
          className="absolute"
          style={{
            width: '55%', height: '60%', left: '-8%', top: '15%',
            background: 'radial-gradient(ellipse at center, rgba(0,245,212,0.045) 0%, transparent 70%)',
            filter: 'blur(50px)',
            animation: 'bg-drift 18s ease-in-out infinite alternate',
          }}
        />
        <div
          className="absolute"
          style={{
            width: '45%', height: '50%', right: '-5%', bottom: '10%',
            background: 'radial-gradient(ellipse at center, rgba(0,180,216,0.035) 0%, transparent 70%)',
            filter: 'blur(50px)',
            animation: 'bg-drift 24s ease-in-out infinite alternate-reverse',
          }}
        />
      </div>

      <div className="animate-fade-in-up grid grid-cols-[minmax(0,1fr)_22rem] gap-4 max-xl:grid-cols-1">
        <CurrentTrackCard summary={data} />
        <StreakCard summary={data} />
      </div>
      <div
        className="animate-fade-in-up grid grid-cols-3 gap-4 max-2xl:grid-cols-2 max-xl:grid-cols-1"
        style={{ animationDelay: '100ms' }}
      >
        <RetryTrendCard summary={data} />
        <FirstAttemptStars summary={data} />
        <RecentActivityList summary={data} />
      </div>
    </div>
  )
}
