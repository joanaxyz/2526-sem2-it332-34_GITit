import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import { modulesApi } from '@/features/modules/api/modulesApi'
import { ModuleCard } from '@/features/modules/components/ModuleCard'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { ModulesSkeleton } from '@/shared/components/Skeleton'

export function ModulesPage() {
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  // TODO(module-terminology): drop the legacy unit param after old links age out.
  const moduleParam = searchParams.get('module') ?? searchParams.get('unit')
  const focusedModuleId = moduleParam ? Number(moduleParam) : null
  const [expandedModuleIds, setExpandedModuleIds] = useState<Set<number>>(() => {
    if (focusedModuleId && Number.isFinite(focusedModuleId)) return new Set([focusedModuleId])
    return new Set()
  })
  const { data, error, isError, isLoading } = useQuery({
    queryKey: queryKeys.modules,
    queryFn: modulesApi.listModules,
    staleTime: 5 * 60 * 1000,
  })
  const scenarioModuleIds = useMemo(
    () => data?.filter((module) => !module.is_orientation && module.scenario_count > 0).map((module) => module.id) ?? [],
    [data],
  )
  const scenarioModuleIdKey = scenarioModuleIds.join(',')
  const scenarioSummaryQuery = useQuery({
    queryKey: queryKeys.moduleScenariosSummary(scenarioModuleIdKey),
    queryFn: () => scenariosApi.listForModules(scenarioModuleIds),
    enabled: scenarioModuleIds.length > 0,
    staleTime: 5 * 60 * 1000,
  })

  const toggleModule = useCallback((moduleId: number) => {
    setExpandedModuleIds((current) => {
      const next = new Set(current)
      if (next.has(moduleId)) next.delete(moduleId)
      else next.add(moduleId)
      return next
    })
  }, [])

  useEffect(() => {
    if (!focusedModuleId || !data?.length) return
    window.requestAnimationFrame(() => {
      document.querySelector(`[data-module-id="${focusedModuleId}"]`)?.scrollIntoView({
        block: 'start',
        behavior: 'smooth',
      })
    })
  }, [data, focusedModuleId])

  useEffect(() => {
    if (!scenarioSummaryQuery.data) return
    for (const [moduleId, scenarios] of Object.entries(scenarioSummaryQuery.data)) {
      queryClient.setQueryData(queryKeys.moduleScenarios(Number(moduleId)), scenarios)
    }
  }, [queryClient, scenarioSummaryQuery.data])

  if (isLoading) return <ModulesSkeleton />
  if (isError) return <ErrorState title="Could not load modules" description={error.message} />
  if (!data) return <ErrorState title="Could not load modules" description="The API returned no module data." />

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-4">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight">Modules</h1>
      </div>
      <div className="flex flex-col gap-3">
        {data.map((module) => (
          <ModuleCard
            key={module.id}
            module={module}
            isExpanded={expandedModuleIds.has(module.id)}
            scenarioSummary={scenarioSummaryQuery.data?.[String(module.id)]}
            scenarioSummaryPending={scenarioSummaryQuery.isLoading}
            onToggle={() => toggleModule(module.id)}
          />
        ))}
      </div>
    </div>
  )
}
