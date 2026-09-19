import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'

import { useAuthStore } from '@/shared/auth/useAuth'
import { homeApi } from '@/features/home/api/homeApi'
import { HomeHubView } from '@/features/home/components/HomeHubView'
import { statsApi } from '@/features/stats/api/statsApi'
import { activityWindowFromParam } from '@/features/stats/utils/activityWindow'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingScreen } from '@/shared/components/LoadingScreen'

export function HomePage() {
  const [searchParams] = useSearchParams()
  // The activity band's window lives in the URL so the request that fetches it
  // and the control that sets it read the same source, and a chosen span
  // survives a reload or a shared link.
  const activityWindow = activityWindowFromParam(searchParams.get('range'))
  const home = useQuery({
    queryKey: queryKeys.homeSummary,
    queryFn: homeApi.summary,
    staleTime: 5 * 60 * 1000,
  })
  const stats = useQuery({
    queryKey: [...queryKeys.statsSummary, activityWindow],
    queryFn: () => statsApi.summary(activityWindow),
    staleTime: 5 * 60 * 1000,
    // Switching span re-fetches; holding the previous summary keeps the whole
    // screen up instead of dropping it to the page loader for one request.
    placeholderData: keepPreviousData,
  })
  const user = useAuthStore((state) => state.user)

  if (home.isLoading || stats.isLoading) {
    return (
      <LoadingScreen
        description="Pulling your rank, streak, stats, and achievements."
        label="Loading home"
      />
    )
  }
  const error = home.error ?? stats.error
  if (home.isError || stats.isError) {
    return <ErrorState title="Could not load home" description={error?.message ?? 'Unknown error'} />
  }
  if (!home.data || !stats.data) {
    return <ErrorState title="Could not load home" description="The API returned no home data." />
  }

  return (
    <HomeHubView
      home={home.data}
      stats={stats.data}
      playerName={user?.username ?? 'Player'}
    />
  )
}
