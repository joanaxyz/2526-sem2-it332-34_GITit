import type { ApiRequestBody, ApiSchemas } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'

export type GitCoinPack = ApiSchemas['GitCoinPackResponse']
export type GitCoinPacksResult = ApiSchemas['GitCoinPacksResponse']
export type CheckoutSessionResult = ApiSchemas['CheckoutSessionResponse']

export const paymentsApi = {
  packs() {
    return apiOperationRequest<'payments_packs_retrieve', GitCoinPacksResult>('payments_packs_retrieve', '/payments/packs/')
  },
  checkout(packSlug: string) {
    const body = { pack_slug: packSlug } satisfies ApiRequestBody<'payments_checkout_create'>
    return apiOperationRequest<'payments_checkout_create', CheckoutSessionResult>('payments_checkout_create', '/payments/checkout/', {
      body,
      headers: { 'Idempotency-Key': crypto.randomUUID() },
    })
  },
}
