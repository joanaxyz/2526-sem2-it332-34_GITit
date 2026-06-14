import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus, RadioTower } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'

import { towersApi } from '@/features/towers/api/towersApi'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function TowerEditorPage() {
  const { designId } = useParams()
  const queryClient = useQueryClient()
  const designs = useQuery({
    queryKey: queryKeys.towerDesigns,
    queryFn: towersApi.mine,
  })
  const createMutation = useMutation({
    mutationFn: () => {
      const stamp = Date.now().toString(36)
      return towersApi.create({ slug: `tower-${stamp}`, title: 'New Tower' })
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.towerDesigns }),
  })
  const activeMutation = useMutation({
    mutationFn: (id: number) => towersApi.setActive(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.towerDesigns })
      queryClient.invalidateQueries({ queryKey: queryKeys.myTower })
    },
  })

  if (designs.isLoading) return <LoadingState label="Loading tower designs" variant="page" />
  if (designs.isError) return <ErrorState title="Could not load tower designs" description={designs.error.message} />

  const selected = designs.data?.results.find((design) => String(design.id) === designId)

  return (
    <div className="grid gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-primary">Tower editor</p>
          <h1 className="mt-2 text-3xl font-black text-foreground">Design library</h1>
        </div>
        <Button disabled={createMutation.isPending} onClick={() => createMutation.mutate()}>
          <Plus className="size-4" />
          New tower
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {(designs.data?.results ?? []).map((design) => (
          <Card className={design.id === selected?.id ? 'border-primary/60' : undefined} key={design.id}>
            <CardHeader>
              <div className="flex items-center justify-between gap-3">
                <CardTitle>{design.title}</CardTitle>
                {design.is_active ? <RadioTower className="size-5 text-primary" /> : null}
              </div>
              <CardDescription>{design.summary || 'No summary yet.'}</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              <Button asChild variant="outline" size="sm">
                <Link to={`/tower/editor/${design.id}`}>Open</Link>
              </Button>
              <Button disabled={activeMutation.isPending || design.is_active} size="sm" onClick={() => activeMutation.mutate(design.id)}>
                Set active
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

export default TowerEditorPage
