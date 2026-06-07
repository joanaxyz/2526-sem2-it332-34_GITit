import { useEffect, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'

import { storeysApi } from '@/features/storeys/api/storeysApi'
import { StoreyPracticeHub } from '@/features/storeys/components/StoreyPracticeHub'
import type { LearningStorey } from '@/features/storeys/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { EmptyState } from '@/shared/components/EmptyState'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

function isFoundationsStorey(storey: LearningStorey) {
  return storey.number === 1 || storey.slug === 'creating-inspecting-repositories'
}

function storeyTitle(storey: LearningStorey) {
  return isFoundationsStorey(storey) ? 'Foundations' : storey.title
}

export function StoreyMapPage() {
  const [searchParams] = useSearchParams()
  const storeyParam = searchParams.get('storey')
  const focusedStoreyId = storeyParam ? Number(storeyParam) : null
  const storeysQuery = useQuery({
    queryKey: queryKeys.storeys,
    queryFn: storeysApi.listStoreys,
    staleTime: 5 * 60 * 1000,
  })

  const storeys = useMemo(() => storeysQuery.data ?? [], [storeysQuery.data])

  useEffect(() => {
    if (!focusedStoreyId || !Number.isFinite(focusedStoreyId) || !storeys.length) return
    window.requestAnimationFrame(() => {
      document.querySelector(`[data-storey-id="${focusedStoreyId}"]`)?.scrollIntoView({
        block: 'start',
        behavior: 'smooth',
      })
    })
  }, [focusedStoreyId, storeys])

  if (storeysQuery.isLoading) {
    return (
      <LoadingState
        description="Preparing the tower."
        label="Loading tower"
        variant="page"
      />
    )
  }
  if (storeysQuery.isError) {
    return <ErrorState title="Could not load tower" description={storeysQuery.error.message} />
  }
  if (!storeys.length) {
    return <EmptyState title="No tower available" description="Publish storeys to start the climb." />
  }

  return (
    <div className="tower-page-shell">
      <div className="tower-sky" aria-hidden="true" />
      <h1 className="sr-only">Git Tower</h1>
      <section className="tower-stage-grid" aria-label="Git Tower storeys">
        <div className="tower-stack-column">
          {storeys.map((storey, index) => (
            <StoreyPracticeHub
              displayTitle={storeyTitle(storey)}
              isFirst={index === 0}
              isLast={index === storeys.length - 1}
              key={storey.id}
              sequenceIndex={index}
              storey={storey}
            />
          ))}
        </div>
      </section>
    </div>
  )
}
