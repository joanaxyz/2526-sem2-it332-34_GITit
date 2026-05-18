import { useQuery } from '@tanstack/react-query'

import { dashboardApi } from '@/features/dashboard/api/dashboardApi'
import { CurrentTrackCard } from '@/features/dashboard/components/CurrentTrackCard'
import { FirstAttemptStars } from '@/features/dashboard/components/FirstAttemptStars'
import { ProgressSummaryCards } from '@/features/dashboard/components/ProgressSummaryCards'
import { RecentActivityList } from '@/features/dashboard/components/RecentActivityList'
import { RetryTrendCard } from '@/features/dashboard/components/RetryTrendCard'
import { StreakCard } from '@/features/dashboard/components/StreakCard'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function DashboardPage() {
  const { data, error, isError, isLoading } = useQuery({ queryKey: ['dashboard-summary'], queryFn: dashboardApi.summary })

  if (isLoading) return <LoadingState label="Loading dashboard" />
  if (isError) return <ErrorState title="Could not load dashboard" description={error.message} />
  if (!data) return <ErrorState title="Could not load dashboard" description="The API returned no dashboard data." />

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-[minmax(0,1fr)_22rem] gap-4 max-xl:grid-cols-1">
        <CurrentTrackCard />
        <StreakCard summary={data} />
      </div>
      <ProgressSummaryCards summary={data} />
      <div className="grid grid-cols-3 gap-4 max-xl:grid-cols-1">
        <RetryTrendCard summary={data} />
        <FirstAttemptStars summary={data} />
        <RecentActivityList summary={data} />
      </div>
    </div>
  )
}
