import { useQuery } from '@tanstack/react-query'

import { walletApi } from '@/features/wallet/api/walletApi'
import { queryKeys } from '@/shared/api/queryKeys'

export function useWalletSummary() {
  return useQuery({
    queryKey: queryKeys.wallet,
    queryFn: walletApi.summary,
    staleTime: 60 * 1000,
  })
}
