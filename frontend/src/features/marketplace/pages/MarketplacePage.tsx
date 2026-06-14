import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { marketplaceApi, type MarketplaceListing } from '@/features/marketplace/api/marketplaceApi'
import { CATEGORY_ITEM_KIND, listingTitle, type Category } from '@/features/marketplace/categories'
import { MarketplaceCategoryRail } from '@/features/marketplace/components/MarketplaceCategoryRail'
import { MarketplaceGallery } from '@/features/marketplace/components/MarketplaceGallery'
import { PurchaseConfirm } from '@/features/marketplace/components/PurchaseConfirm'
import { walletApi } from '@/features/wallet/api/walletApi'
import { ApiError } from '@/shared/api/apiError'
import { queryKeys } from '@/shared/api/queryKeys'
import { ASSET_TAGS } from '@/shared/assets/tags'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function MarketplacePage() {
  const queryClient = useQueryClient()
  const [category, setCategory] = useState<Category>('relic')
  const [subKind, setSubKind] = useState<string | null>(null)
  const [ownedOnly, setOwnedOnly] = useState(false)
  const [tags, setTags] = useState<string[]>([])
  const [pending, setPending] = useState<MarketplaceListing | null>(null)

  const listings = useQuery({
    queryKey: queryKeys.marketplaceListings,
    queryFn: marketplaceApi.listings,
    staleTime: 60 * 1000,
  })
  const wallet = useQuery({ queryKey: queryKeys.wallet, queryFn: walletApi.summary })
  const balance = wallet.data?.balance ?? 0

  const purchase = useMutation({
    mutationFn: (listingId: number) => marketplaceApi.purchase(listingId),
    onSuccess: () => {
      // Refresh the store, wallet, gallery — and the editor pickers, so a bought
      // piece/artifact/content shows up immediately when designing the Spire.
      for (const key of [
        queryKeys.marketplaceListings,
        queryKeys.wallet,
        queryKeys.galleryContent,
        queryKeys.galleryAssets,
        queryKeys.galleryTowerDesigns,
        queryKeys.assetDescriptorsOwned('tower_piece'),
        queryKeys.assetDescriptorsOwned('tower_artifact'),
        queryKeys.authoringContent(),
        queryKeys.towerDesigns,
      ]) {
        queryClient.invalidateQueries({ queryKey: key })
      }
      setPending(null)
    },
  })

  // Category/sub-kind/owned filtering, BEFORE tags, so the tag chips reflect
  // what's actually buyable in this category rather than collapsing as you pick.
  const categoryFiltered = useMemo(() => {
    const itemKind = CATEGORY_ITEM_KIND[category]
    return (listings.data?.results ?? []).filter((listing) => {
      if (listing.item_kind !== itemKind) return false
      if (subKind && listing.item.kind !== subKind) return false
      if (ownedOnly && !(listing.owned || listing.entitled)) return false
      return true
    })
  }, [listings.data, category, subKind, ownedOnly])

  // Tags present on the current category's listings, curated order first.
  const availableTags = useMemo(() => {
    const present = new Set<string>()
    for (const listing of categoryFiltered) for (const tag of listing.item.tags ?? []) present.add(tag)
    const curated = ASSET_TAGS.filter((tag) => present.has(tag))
    const extras = [...present].filter((tag) => !curated.includes(tag as never)).sort()
    return [...curated, ...extras]
  }, [categoryFiltered])

  // OR within the tag facet: a listing matches if it carries any selected tag.
  const filtered = useMemo(() => {
    if (tags.length === 0) return categoryFiltered
    return categoryFiltered.filter((listing) => {
      const itemTags = listing.item.tags ?? []
      return tags.some((tag) => itemTags.includes(tag))
    })
  }, [categoryFiltered, tags])

  function toggleTag(tag: string) {
    setTags((current) => (current.includes(tag) ? current.filter((t) => t !== tag) : [...current, tag]))
  }

  if (listings.isLoading) return <LoadingState label="Opening the shop" variant="page" />
  if (listings.isError) return <ErrorState title="Could not load shop" description={listings.error.message} />

  const purchaseError = purchase.error instanceof ApiError ? purchase.error.message : null

  return (
    <div className="marketplace">
      <header className="market-head">
        <p className="editor-eyebrow">Shop</p>
        <h1 className="market-title">The Arcane Bazaar</h1>
        <p className="market-sub">Acquire relics, lore, and whole Spires for GitCoins. Purchases unlock in your editor.</p>
      </header>

      <MarketplaceCategoryRail
        category={category}
        subKind={subKind}
        onCategory={(next) => {
          setCategory(next)
          setSubKind(null)
          setTags([])
        }}
        onSubKind={setSubKind}
        ownedOnly={ownedOnly}
        onOwnedOnly={setOwnedOnly}
        tags={tags}
        availableTags={availableTags}
        onToggleTag={toggleTag}
        onClearTags={() => setTags([])}
      />

      <MarketplaceGallery listings={filtered} balance={balance} onBuy={setPending} />

      {pending ? (
        <PurchaseConfirm
          listing={pending}
          title={listingTitle(pending)}
          balance={balance}
          isPending={purchase.isPending}
          error={purchaseError}
          onConfirm={() => purchase.mutate(pending.id)}
          onCancel={() => {
            purchase.reset()
            setPending(null)
          }}
        />
      ) : null}
    </div>
  )
}

export default MarketplacePage
