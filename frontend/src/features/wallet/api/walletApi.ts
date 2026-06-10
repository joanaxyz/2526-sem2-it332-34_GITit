import { apiRequest } from '@/shared/api/httpClient'

export type CoinTransactionEntry = {
  amount: number
  reason: string
  created_at: string
}

export type WalletSummary = {
  balance: number
  recent: CoinTransactionEntry[]
}

export const walletApi = {
  summary() {
    return apiRequest<WalletSummary>('/progress/wallet/')
  },
}
