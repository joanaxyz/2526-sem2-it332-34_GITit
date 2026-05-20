import { useQuery } from '@tanstack/react-query'
import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { unitsApi } from '@/features/units/api/unitsApi'
import { UnitCard } from '@/features/units/components/UnitCard'
import { ErrorState } from '@/shared/components/ErrorState'
import { UnitsSkeleton } from '@/shared/components/Skeleton'

export function UnitsPage() {
  const [searchParams] = useSearchParams()
  const unitParam = searchParams.get('unit')
  const focusedUnitId = unitParam ? Number(unitParam) : null
  const [visibleUnitIds, setVisibleUnitIds] = useState<Set<number>>(
    () => new Set(focusedUnitId ? [focusedUnitId] : []),
  )
  const { data, error, isError, isLoading } = useQuery({ queryKey: ['units'], queryFn: unitsApi.listUnits })
  const renderedVisibleUnitIds = useMemo(() => {
    const next = new Set(visibleUnitIds)
    if (!data?.length) return next
    if (focusedUnitId) next.add(focusedUnitId)
    if (typeof IntersectionObserver === 'undefined') {
      data.forEach((unit) => next.add(unit.id))
    } else if (!next.size) {
      data.slice(0, 2).forEach((unit) => next.add(unit.id))
    }
    return next
  }, [data, focusedUnitId, visibleUnitIds])

  useEffect(() => {
    if (!data?.length) return
    if (typeof IntersectionObserver === 'undefined') return
    const observer = new IntersectionObserver(
      (entries) => {
        const nextVisibleIds = entries
          .filter((entry) => entry.isIntersecting)
          .map((entry) => Number((entry.target as HTMLElement).dataset.unitId))
          .filter(Number.isFinite)

        if (!nextVisibleIds.length) return
        setVisibleUnitIds((current) => {
          const next = new Set(current)
          nextVisibleIds.forEach((id) => next.add(id))
          return next
        })
      },
      { rootMargin: '720px 0px' },
    )

    document.querySelectorAll<HTMLElement>('[data-unit-id]').forEach((element) => observer.observe(element))
    return () => observer.disconnect()
  }, [data])

  useEffect(() => {
    if (!focusedUnitId || !data?.length) return
    window.requestAnimationFrame(() => {
      document.querySelector(`[data-unit-id="${focusedUnitId}"]`)?.scrollIntoView({
        block: 'start',
        behavior: 'smooth',
      })
    })
  }, [data, focusedUnitId])

  if (isLoading) return <UnitsSkeleton />
  if (isError) return <ErrorState title="Could not load Units" description={error.message} />
  if (!data) return <ErrorState title="Could not load Units" description="The API returned no Unit data." />

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-4">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight">Units</h1>
      </div>
      <div className="flex flex-col gap-3">
        {data.map((unit) => (
          <UnitCard key={unit.id} unit={unit} isContentVisible={renderedVisibleUnitIds.has(unit.id)} />
        ))}
      </div>
    </div>
  )
}
