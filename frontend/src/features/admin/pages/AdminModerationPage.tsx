import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { adminApi } from '@/features/admin/api/adminApi'
import { PageHeading } from '@/features/admin/components/adminUi'
import { formatDate } from '@/features/admin/utils/format'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { queryKeys } from '@/shared/api/queryKeys'

export function AdminModerationPage() {
  const queryClient = useQueryClient()
  const { data, isPending, isError } = useQuery({ queryKey: queryKeys.adminModeration, queryFn: adminApi.moderation })

  const unpublish = useMutation({
    mutationFn: adminApi.unpublish,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.adminModeration }),
  })

  if (isPending) return <LoadingState label="Loading shared content" variant="page" />
  if (isError || !data) return <ErrorState title="Could not load moderation queue" description="Try again shortly." />

  return (
    <div>
      <PageHeading title="Moderation" description="Player-shared content. Unpublish anything that breaks the rules." />

      <section className="overflow-hidden rounded-lg border border-border bg-card">
        <div className="border-b border-border px-5 py-3 text-sm font-bold text-foreground">Shared content</div>
        {data.content.length === 0 ? (
          <p className="px-5 py-6 text-sm text-muted-foreground">No shared content.</p>
        ) : (
          <ul className="divide-y divide-border/50">
            {data.content.map((content) => (
              <li key={content.id} className="flex items-center justify-between px-5 py-2.5 text-sm">
                <span>
                  <span className="font-medium text-foreground">{content.title}</span>
                  <span className="ml-2 text-xs capitalize text-muted-foreground">{content.kind} · by {content.owner ?? 'unknown'} · {formatDate(content.updated_at)}</span>
                </span>
                <Button size="sm" variant="destructive" disabled={unpublish.isPending} onClick={() => unpublish.mutate({ kind: 'content', id: content.id })}>
                  Unpublish
                </Button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
