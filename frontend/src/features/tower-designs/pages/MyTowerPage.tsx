import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { towerDesignsApi } from '@/features/tower-designs/api/towerDesignsApi'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function MyTowerPage() {
  const query = useQuery({
    queryKey: queryKeys.myTower,
    queryFn: towerDesignsApi.overview,
    retry: false,
  })

  if (query.isLoading) return <LoadingState label="Loading private tower" variant="page" />

  if (query.isError) {
    return (
      <div className="grid gap-5">
        <ErrorState title="No active private tower" description="Create or activate a tower design to preview it here." />
        <Button asChild className="w-fit">
          <Link to="/tower/editor">Open tower editor</Link>
        </Button>
      </div>
    )
  }
  if (!query.data) {
    return <ErrorState title="No active private tower" description="The API returned no tower design." />
  }

  const overview = query.data

  return (
    <div className="grid gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-primary">Private tower</p>
          <h1 className="mt-2 text-3xl font-black text-foreground">{overview.design.title}</h1>
        </div>
        <Button asChild variant="outline">
          <Link to={`/tower/editor/${overview.design.id}`}>Edit design</Link>
        </Button>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <Card>
          <CardHeader>
            <CardTitle>Tower pieces</CardTitle>
            <CardDescription>{overview.tower_layout.pieces.length} pieces in this design.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3">
            {overview.tower_layout.pieces.map((piece, index) => (
              <div className="flex items-center justify-between rounded-md border border-border bg-background/30 px-3 py-2" key={piece.instanceId}>
                <span className="font-semibold text-foreground">{index + 1}. {piece.pieceType}</span>
                <span className="text-sm text-muted-foreground">{piece.assetSlug}</span>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Bindings</CardTitle>
            <CardDescription>Authored content attached to this tower.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3 text-sm">
            <strong>{Object.keys(overview.content.adventures).length} adventures</strong>
            <strong>{Object.keys(overview.content.challenges).length} challenges</strong>
            <strong>{Object.keys(overview.content.tomes).length} tomes</strong>
            <strong>{overview.artifacts.length} artifacts</strong>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default MyTowerPage
