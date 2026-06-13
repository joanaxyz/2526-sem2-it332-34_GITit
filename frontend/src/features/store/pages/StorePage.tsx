import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ShoppingCart } from 'lucide-react'

import { storeApi } from '@/features/store/api/storeApi'
import { GitCoinIcon } from '@/features/wallet/components/GitCoinIcon'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function StorePage() {
  const queryClient = useQueryClient()
  const listings = useQuery({
    queryKey: queryKeys.storeListings,
    queryFn: storeApi.listings,
    staleTime: 60 * 1000,
  })
  const purchase = useMutation({
    mutationFn: (listingId: number) => storeApi.purchase(listingId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.storeListings })
      queryClient.invalidateQueries({ queryKey: queryKeys.wallet })
      queryClient.invalidateQueries({ queryKey: queryKeys.galleryContent })
      queryClient.invalidateQueries({ queryKey: queryKeys.galleryAssets })
      queryClient.invalidateQueries({ queryKey: queryKeys.galleryTowerDesigns })
    },
  })

  if (listings.isLoading) return <LoadingState label="Loading store" variant="page" />
  if (listings.isError) return <ErrorState title="Could not load store" description={listings.error.message} />

  return (
    <div className="grid gap-6">
      <div>
        <p className="text-sm font-semibold uppercase tracking-wide text-primary">Store</p>
        <h1 className="mt-2 text-3xl font-black text-foreground">Tower marketplace</h1>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {(listings.data?.results ?? []).map((listing) => {
          const title = listing.item.title || listing.item.label || listing.item.slug || `${listing.item_kind} #${listing.item_id}`
          const unlocked = listing.owned || listing.entitled
          return (
            <Card key={listing.id}>
              <CardHeader>
                <div className="flex items-center justify-between gap-3">
                  <CardTitle>{title}</CardTitle>
                  <span className="rounded-sm border border-primary/25 px-2 py-1 text-xs font-semibold text-primary">
                    {listing.item_kind}
                  </span>
                </div>
                <CardDescription>{listing.item.summary || listing.item.visibility || 'Marketplace item'}</CardDescription>
              </CardHeader>
              <CardContent className="flex items-center justify-between gap-3">
                <span className="inline-flex items-center gap-2 font-black text-primary">
                  {listing.price}
                  <GitCoinIcon className="size-5" />
                </span>
                <Button disabled={purchase.isPending || unlocked} size="sm" onClick={() => purchase.mutate(listing.id)}>
                  <ShoppingCart className="size-4" />
                  {unlocked ? 'Unlocked' : 'Buy'}
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}

export default StorePage
