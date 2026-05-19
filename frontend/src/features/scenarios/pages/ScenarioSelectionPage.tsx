import { useQuery } from '@tanstack/react-query'
import { ArrowLeft } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'

import { ScenarioList } from '@/features/scenarios/components/ScenarioList'
import { unitsApi } from '@/features/units/api/unitsApi'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function ScenarioSelectionPage() {
  const params = useParams()
  const lessonId = Number(params.lessonId)
  const lessonQuery = useQuery({
    queryKey: ['lesson', lessonId],
    queryFn: () => unitsApi.getLesson(lessonId),
    enabled: Number.isFinite(lessonId),
  })

  if (lessonQuery.isLoading) return <LoadingState label="Loading skill focuses" />
  if (lessonQuery.isError) return <ErrorState title="Could not load lesson" description={lessonQuery.error.message} />
  if (!lessonQuery.data) return <ErrorState title="Could not load skill focuses" description="The API returned no lesson data." />

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-4">
      <section className="rounded-lg border border-border bg-card p-6">
        <div className="mb-4">
          <Button asChild variant="ghost" size="sm">
            <Link to="/units">
              <ArrowLeft data-icon="inline-start" />
              Back to Units
            </Link>
          </Button>
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight">Scenario Skill Focuses</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
          This legacy route now uses the same Skill Focus Preview flow as the expanded Unit page. The main access path is
          Units → expanded unit → Scenario Skill Focus card.
        </p>
      </section>
      <ScenarioList scope="lesson" lessonId={lessonQuery.data.id} source="lesson" />
    </div>
  )
}
