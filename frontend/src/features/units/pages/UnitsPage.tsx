import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'

import { unitsApi } from '@/features/units/api/unitsApi'
import { UnitCard } from '@/features/units/components/UnitCard'
import { LoadingState } from '@/shared/components/LoadingState'

export function UnitsPage() {
  const [expanded, setExpanded] = useState<number | null>(null)
  const { data, isLoading } = useQuery({ queryKey: ['units'], queryFn: unitsApi.listUnits })

  if (isLoading || !data) return <LoadingState label="Loading Units" />

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-4">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight">Units</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
          Browse Unit lessons and expand scenario-bearing Units without leaving the dashboard flow.
        </p>
      </div>
      <div className="flex flex-col gap-3">
        {data.map((unit) => (
          <UnitCard key={unit.id} unit={unit} expanded={expanded === unit.id} onToggle={() => setExpanded(expanded === unit.id ? null : unit.id)} />
        ))}
      </div>
    </div>
  )
}
