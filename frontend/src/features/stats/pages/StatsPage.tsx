import { useQuery } from '@tanstack/react-query'

import { statsApi } from '@/features/stats/api/statsApi'
import { StatsView } from '@/features/stats/components/StatsView'
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

  return <StatsView data={data} />
}
