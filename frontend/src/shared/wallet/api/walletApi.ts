import type { ApiSchemas } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'

export type WalletSummary = ApiSchemas['WalletSummaryResponse']

export const walletApi = {
  summary() {
    return apiOperationRequest<'progress_wallet_retrieve', WalletSummary>('progress_wallet_retrieve', '/progress/wallet/')
  },
}
