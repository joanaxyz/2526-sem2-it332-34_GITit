import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { adminApi } from '@/features/admin/api/adminApi'
import { PageHeading } from '@/features/admin/components/adminUi'
import { formatDate } from '@/features/admin/utils/format'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { queryKeys } from '@/shared/api/queryKeys'

const KINDS = ['adventure', 'challenge', 'lesson'] as const

export function AdminContentPage() {
  const contentQuery = useQuery({ queryKey: queryKeys.adminContent, queryFn: () => adminApi.content() })

  return (
    <div>
      <PageHeading
        title="Official Content"
        description="Official adventures, challenges, and lessons. Staff-authored content compiles as official curriculum."
      />

      <div className="mb-4 flex flex-wrap gap-2">
        {KINDS.map((kind) => (
          <Button key={kind} asChild size="sm">
            <Link to={`/level-editor/new/${kind}`}>New {kind}</Link>
          </Button>
        ))}
      </div>

      {contentQuery.isPending ? (
        <LoadingState label="Loading content" variant="panel" />
      ) : contentQuery.isError ? (
        <ErrorState title="Could not load content" description="Try again shortly." />
      ) : contentQuery.data.results.length === 0 ? (
        <div className="rounded-lg border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
          No official content yet. Create one above.
        </div>
      ) : (
        <div className="overflow-hidden rounded-lg border border-border bg-card">
          <table className="w-full text-sm">
            <thead className="border-b border-border text-left text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-5 py-2 font-semibold">Title</th>
                <th className="px-5 py-2 font-semibold">Kind</th>
                <th className="px-5 py-2 font-semibold">Status</th>
                <th className="px-5 py-2 font-semibold">Updated</th>
                <th className="px-5 py-2" />
              </tr>
            </thead>
            <tbody>
              {contentQuery.data.results.map((content) => (
                <tr key={content.id} className="border-b border-border/40">
                  <td className="px-5 py-2.5 font-medium text-foreground">{content.title}</td>
                  <td className="px-5 py-2.5 capitalize text-muted-foreground">{content.kind}</td>
                  <td className="px-5 py-2.5 capitalize text-muted-foreground">{content.status}</td>
                  <td className="px-5 py-2.5 text-muted-foreground">{formatDate(content.updated_at)}</td>
                  <td className="px-5 py-2.5 text-right">
                    <Button asChild size="sm" variant="outline">
                      <Link to={`/level-editor/${content.id}`}>Edit</Link>
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
