import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import { unitsApi } from '@/features/units/api/unitsApi'
import { UnitCard } from '@/features/units/components/UnitCard'
import { ErrorState } from '@/shared/components/ErrorState'
import { UnitsSkeleton } from '@/shared/components/Skeleton'

export function UnitsPage() {
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  const unitParam = searchParams.get('unit')
  const focusedUnitId = unitParam ? Number(unitParam) : null
  const [expandedUnitIds, setExpandedUnitIds] = useState<Set<number>>(() => {
    if (focusedUnitId && Number.isFinite(focusedUnitId)) return new Set([focusedUnitId])
    return new Set()
  })
  const { data, error, isError, isLoading } = useQuery({ queryKey: ['units'], queryFn: unitsApi.listUnits })
  const scenarioUnitIds = useMemo(
    () => data?.filter((unit) => !unit.is_orientation && unit.scenario_count > 0).map((unit) => unit.id) ?? [],
    [data],
  )
  const scenarioUnitIdKey = scenarioUnitIds.join(',')
  const scenarioSummaryQuery = useQuery({
    queryKey: ['unit-scenarios-summary', scenarioUnitIdKey],
    queryFn: () => scenariosApi.listForUnits(scenarioUnitIds),
    enabled: scenarioUnitIds.length > 0,
    staleTime: 5 * 60 * 1000,
  })

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

  useEffect(() => {
    if (!scenarioSummaryQuery.data) return
    for (const [unitId, scenarios] of Object.entries(scenarioSummaryQuery.data)) {
      queryClient.setQueryData(['unit-scenarios', Number(unitId)], scenarios)
    }
  }, [queryClient, scenarioSummaryQuery.data])

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
            scenarioSummary={scenarioSummaryQuery.data?.[String(unit.id)]}
            scenarioSummaryPending={scenarioSummaryQuery.isLoading}
            onToggle={() => toggleUnit(unit.id)}
          />
        ))}
      </div>
    </div>
  )
}
