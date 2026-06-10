import { useQuery } from '@tanstack/react-query'
import { ArrowRight, Radar } from 'lucide-react'
import { Link } from 'react-router-dom'

import { dashboardApi } from '@/features/dashboard/api/dashboardApi'
import { CurrentTrackCard } from '@/features/dashboard/components/CurrentTrackCard'
import { RecentActivityList } from '@/features/dashboard/components/RecentActivityList'
import { StreakCard } from '@/features/dashboard/components/StreakCard'
import { queryKeys } from '@/shared/api/queryKeys'
import { Card, CardContent } from '@/shared/components/Card'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

function StatsCtaCard() {
  return (
    <Link to="/stats" className="group block h-full">
      <Card
        className="dash-card-hover h-full overflow-hidden"
        style={{ borderLeft: '2px solid rgba(0,180,216,0.35)' }}
      >
        <CardContent className="flex h-full items-center gap-4 p-5">
          <div
            className="flex size-12 flex-shrink-0 items-center justify-center rounded-xl"
            style={{ background: 'radial-gradient(circle at 30% 30%, rgba(0,245,212,0.22), rgba(0,180,216,0.08))' }}
          >
            <Radar className="size-6 text-aurora-cyan transition-transform group-hover:scale-110" />
          </div>
          <div className="min-w-0">
            <p className="font-bold tracking-tight">See your skill profile</p>
            <p className="mt-0.5 text-xs text-muted-foreground">
              Accuracy, efficiency, mastery and more — across adventures and challenges.
            </p>
          </div>
          <ArrowRight className="ml-auto size-5 flex-shrink-0 text-aurora-blue/70 transition-transform group-hover:translate-x-1" />
        </CardContent>
      </Card>
    </Link>
  )
}

export function DashboardPage() {
  const { data, error, isError, isLoading } = useQuery({
    queryKey: queryKeys.dashboardSummary,
    queryFn: dashboardApi.summary,
    staleTime: 5 * 60 * 1000,
  })

  if (isLoading) {
    return (
      <LoadingState
        description="Pulling your current track, streak, and recent quest activity."
        label="Loading dashboard"
        variant="page"
      />
    )
  }
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
        className="animate-fade-in-up grid grid-cols-2 gap-4 max-xl:grid-cols-1"
        style={{ animationDelay: '100ms' }}
      >
        <RecentActivityList summary={data} />
        <StatsCtaCard />
      </div>
    </div>
  )
}
