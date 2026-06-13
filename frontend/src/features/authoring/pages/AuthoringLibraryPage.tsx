import { useQuery } from '@tanstack/react-query'
import { FilePlus2, Pencil } from 'lucide-react'
import { Link } from 'react-router-dom'

import { authoringApi } from '@/features/authoring/api/authoringApi'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

const newContentLinks = [
  { kind: 'adventure', label: 'Adventure' },
  { kind: 'challenge', label: 'Challenge' },
  { kind: 'tome', label: 'Tome' },
] as const

export function AuthoringLibraryPage() {
  const query = useQuery({
    queryKey: queryKeys.authoringContent(),
    queryFn: () => authoringApi.list(),
    staleTime: 60 * 1000,
  })

  if (query.isLoading) return <LoadingState label="Loading authored content" variant="page" />
  if (query.isError) {
    return <ErrorState title="Could not load authored content" description={query.error.message} />
  }

  return (
    <div className="grid gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-primary">Authoring</p>
          <h1 className="mt-2 text-3xl font-black text-foreground">Content workshop</h1>
        </div>
        <div className="flex flex-wrap gap-2">
          {newContentLinks.map((item) => (
            <Button asChild key={item.kind} size="sm">
              <Link to={`/authoring/new/${item.kind}`}>
                <FilePlus2 className="size-4" />
                {item.label}
              </Link>
            </Button>
          ))}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {(query.data?.results ?? []).map((content) => (
          <Card key={content.id}>
            <CardHeader>
              <div className="flex items-center justify-between gap-3">
                <CardTitle>{content.title}</CardTitle>
                <span className="rounded-sm border border-primary/25 px-2 py-1 text-xs font-semibold text-primary">
                  {content.kind}
                </span>
              </div>
              <CardDescription>{content.summary || 'No summary yet.'}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4 flex flex-wrap gap-2 text-xs text-muted-foreground">
                <span>{content.status}</span>
                <span>{content.visibility}</span>
                {content.command_family ? <span>{content.command_family}</span> : null}
              </div>
              <Button asChild variant="outline" size="sm">
                <Link to={`/authoring/${content.id}`}>
                  <Pencil className="size-4" />
                  Edit
                </Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

export default AuthoringLibraryPage
