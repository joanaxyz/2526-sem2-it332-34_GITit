import { useQuery } from '@tanstack/react-query'
import { useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { unitsApi } from '@/features/units/api/unitsApi'
import { UnitCard } from '@/features/units/components/UnitCard'
import { ErrorState } from '@/shared/components/ErrorState'
import { UnitsSkeleton } from '@/shared/components/Skeleton'

export function UnitsPage() {
  const [searchParams] = useSearchParams()
  const unitParam = searchParams.get('unit')
  const focusedUnitId = unitParam ? Number(unitParam) : null
  const [expandedUnitIds, setExpandedUnitIds] = useState<Set<number>>(() => {
    if (focusedUnitId && Number.isFinite(focusedUnitId)) return new Set([focusedUnitId])
    return new Set()
  })
  const { data, error, isError, isLoading } = useQuery({ queryKey: ['units'], queryFn: unitsApi.listUnits })

  const toggleUnit = useCallback((unitId: number) => {
    setExpandedUnitIds((current) => {
      const next = new Set(current)
      if (next.has(unitId)) next.delete(unitId)
      else next.add(unitId)
      return next
    })
  }, [])

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
  if (isError) return <ErrorState title="Could not load modules" description={error.message} />
  if (!data) return <ErrorState title="Could not load modules" description="The API returned no module data." />

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-4">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight">Modules</h1>
      </div>
      <div className="flex flex-col gap-3">
        {data.map((unit) => (
          <UnitCard
            key={unit.id}
            unit={unit}
            isExpanded={expandedUnitIds.has(unit.id)}
            onToggle={() => toggleUnit(unit.id)}
          />
        ))}
      </div>
    </div>
  )
}
