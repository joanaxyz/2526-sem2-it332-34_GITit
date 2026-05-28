import { useQuery } from '@tanstack/react-query'

import { dashboardApi } from '@/features/dashboard/api/dashboardApi'
import { ModulePerformanceCard } from '@/features/dashboard/components/ModulePerformanceCard'
import { ProgressSummaryCards } from '@/features/dashboard/components/ProgressSummaryCards'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function PerformancePage() {
  const { data, error, isError, isLoading } = useQuery({
    queryKey: queryKeys.dashboardSummary,
    queryFn: dashboardApi.summary,
    staleTime: 5 * 60 * 1000,
  })

  if (isLoading) return <LoadingState label="Loading performance" />
  if (isError) return <ErrorState title="Could not load performance" description={error.message} />
  if (!data) return <ErrorState title="Could not load performance" description="The API returned no data." />

  return (
    <div className="flex flex-col gap-5">
      {/* Animated background — same aurora orbs as dashboard */}
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div
          className="absolute"
          style={{
            width: '50%', height: '55%', left: '-6%', top: '20%',
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
        <div
          className="absolute"
          style={{
            width: '30%', height: '35%', right: '15%', top: '5%',
            background: 'radial-gradient(ellipse at center, rgba(125,211,252,0.025) 0%, transparent 70%)',
            filter: 'blur(60px)',
            animation: 'bg-drift 32s ease-in-out infinite alternate',
          }}
        />
      </div>

      <div className="animate-fade-in-up">
        <h1
          className="text-4xl font-extrabold tracking-tight"
          style={{ textShadow: '0 0 30px rgba(0,245,212,0.35), 0 0 60px rgba(0,180,216,0.18)' }}
        >
          Performance
        </h1>
      </div>
      <div className="animate-fade-in-up" style={{ animationDelay: '100ms' }}>
        <ProgressSummaryCards summary={data} />
      </div>
      <div className="animate-fade-in-up" style={{ animationDelay: '200ms' }}>
        <ModulePerformanceCard summary={data} />
      </div>
    </div>
  )
}
