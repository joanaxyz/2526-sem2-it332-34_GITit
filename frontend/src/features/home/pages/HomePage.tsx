import { useQuery } from '@tanstack/react-query'

import { useAuthStore } from '@/features/auth/hooks/useAuth'
import { homeApi } from '@/features/home/api/homeApi'
import { HomeHubView } from '@/features/home/components/HomeHubView'
import { statsApi } from '@/features/stats/api/statsApi'
import { useWalletSummary } from '@/features/wallet/hooks/useWallet'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function HomePage() {
  const home = useQuery({
    queryKey: queryKeys.homeSummary,
    queryFn: homeApi.summary,
    staleTime: 5 * 60 * 1000,
  })
  const stats = useQuery({
    queryKey: queryKeys.statsSummary,
    queryFn: statsApi.summary,
    staleTime: 5 * 60 * 1000,
  })
  const wallet = useWalletSummary()
  const user = useAuthStore((state) => state.user)

  if (home.isLoading || stats.isLoading) {
    return (
      <LoadingState
        description="Pulling your rank, streak, stats, and achievements."
        label="Loading home"
        variant="page"
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
      gitcoins={typeof wallet.data?.balance === 'number' ? wallet.data.balance : null}
    />
  )
}
