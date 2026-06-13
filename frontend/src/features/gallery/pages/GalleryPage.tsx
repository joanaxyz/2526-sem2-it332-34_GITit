import { useQuery } from '@tanstack/react-query'

import { galleryApi } from '@/features/gallery/api/galleryApi'
import { queryKeys } from '@/shared/api/queryKeys'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function GalleryPage() {
  const assets = useQuery({ queryKey: queryKeys.galleryAssets, queryFn: galleryApi.assets })
  const content = useQuery({ queryKey: queryKeys.galleryContent, queryFn: galleryApi.content })
  const towers = useQuery({ queryKey: queryKeys.galleryTowerDesigns, queryFn: galleryApi.towerDesigns })

  if (assets.isLoading || content.isLoading || towers.isLoading) {
    return <LoadingState label="Loading gallery" variant="page" />
  }
  const error = assets.error ?? content.error ?? towers.error
  if (assets.isError || content.isError || towers.isError) {
    return <ErrorState title="Could not load gallery" description={error?.message ?? 'Unknown error'} />
  }

  return (
    <div className="grid gap-6">
      <div>
        <p className="text-sm font-semibold uppercase tracking-wide text-primary">Gallery</p>
        <h1 className="mt-2 text-3xl font-black text-foreground">Community library</h1>
      </div>
      <GallerySection title="Assets" items={(assets.data?.results ?? []).map((item) => ({ id: item.id, title: item.label, meta: item.kind }))} />
      <GallerySection title="Content" items={(content.data?.results ?? []).map((item) => ({ id: item.id, title: item.title, meta: item.kind }))} />
      <GallerySection title="Tower designs" items={(towers.data?.results ?? []).map((item) => ({ id: item.id, title: item.title, meta: item.status }))} />
    </div>
  )
}

function GallerySection({ title, items }: { title: string; items: Array<{ id: number; title: string; meta: string }> }) {
  return (
    <section className="grid gap-3">
      <h2 className="text-xl font-black text-foreground">{title}</h2>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {items.map((item) => (
          <Card key={`${title}-${item.id}`}>
            <CardHeader>
              <CardTitle>{item.title}</CardTitle>
              <CardDescription>{item.meta}</CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">Available in your workspace when owned or unlocked.</CardContent>
          </Card>
        ))}
      </div>
    </section>
  )
}

export default GalleryPage
