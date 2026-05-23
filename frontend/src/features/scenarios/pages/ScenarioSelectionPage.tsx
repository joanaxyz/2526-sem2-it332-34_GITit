import { useQuery } from '@tanstack/react-query'
import { ArrowLeft } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'

import { ScenarioList } from '@/features/scenarios/components/ScenarioList'
import { modulesApi } from '@/features/modules/api/modulesApi'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function ScenarioSelectionPage() {
  const params = useParams()
  const lessonId = Number(params.lessonId)
  const lessonQuery = useQuery({
    queryKey: ['lesson', lessonId],
    queryFn: () => modulesApi.getLesson(lessonId),
    enabled: Number.isFinite(lessonId),
  })

  if (lessonQuery.isLoading) return <LoadingState label="Loading scenarios" />
  if (lessonQuery.isError) return <ErrorState title="Could not load lesson" description={lessonQuery.error.message} />
  if (!lessonQuery.data) return <ErrorState title="Could not load scenarios" description="The API returned no lesson data." />

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-4">
      <section className="rounded-lg border border-border bg-card p-6">
        <div className="mb-4">
          <Button asChild variant="ghost" size="sm">
            <Link to="/modules">
              <ArrowLeft data-icon="inline-start" />
              Back to Modules
            </Link>
          </Button>
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight">Scenarios</h1>
      </section>
      <ScenarioList scope="lesson" lessonId={lessonQuery.data.id} source="lesson" />
    </div>
  )
}
