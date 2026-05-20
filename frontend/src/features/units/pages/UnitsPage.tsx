import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { unitsApi } from '@/features/units/api/unitsApi'
import { UnitCard } from '@/features/units/components/UnitCard'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function UnitsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const unitParam = searchParams.get('unit')
  const [expanded, setExpanded] = useState<number | null>(unitParam ? Number(unitParam) : null)
  const { data, error, isError, isLoading } = useQuery({ queryKey: ['units'], queryFn: unitsApi.listUnits })

  function handleToggle(unitId: number) {
    const next = expanded === unitId ? null : unitId
    setExpanded(next)
    if (next) {
      setSearchParams({ unit: String(next) })
    } else {
      setSearchParams({})
    }
  }

  if (isLoading) return <LoadingState label="Loading Units" />
  if (isError) return <ErrorState title="Could not load Units" description={error.message} />
  if (!data) return <ErrorState title="Could not load Units" description="The API returned no Unit data." />

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-4">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight">Units</h1>
      </div>
      <div className="flex flex-col gap-3">
        {data.map((unit) => (
          <UnitCard key={unit.id} unit={unit} expanded={expanded === unit.id} onToggle={() => handleToggle(unit.id)} />
        ))}
      </div>
    </div>
  )
}
