import { useQuery } from '@tanstack/react-query'

import { useAuthStore } from '@/features/auth/hooks/useAuth'
import { dashboardApi } from '@/features/dashboard/api/dashboardApi'
import { DashboardView } from '@/features/dashboard/components/DashboardView'
import { useWalletSummary } from '@/features/wallet/hooks/useWallet'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function DashboardPage() {
  const { data, error, isError, isLoading } = useQuery({
    queryKey: queryKeys.dashboardSummary,
    queryFn: dashboardApi.summary,
    staleTime: 5 * 60 * 1000,
  })
  const wallet = useWalletSummary()
  const user = useAuthStore((state) => state.user)

  if (isLoading) {
    return (
      <LoadingState
        description="Pulling your rank, streak, and recent quest activity."
        label="Loading dashboard"
        variant="page"
      />
    )
  }
  if (isError) return <ErrorState title="Could not load dashboard" description={error.message} />
  if (!data) return <ErrorState title="Could not load dashboard" description="The API returned no dashboard data." />

  return (
    <DashboardView
      data={data}
      playerName={user?.username ?? 'Player'}
      gitcoins={typeof wallet.data?.balance === 'number' ? wallet.data.balance : null}
    />
  )
}
