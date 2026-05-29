import { Info } from 'lucide-react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import { modulesApi } from '@/features/modules/api/modulesApi'
import { ModuleCard } from '@/features/modules/components/ModuleCard'
import { SkillFocusPreviewModal } from '@/features/scenarios/components/SkillFocusPreviewModal'
import type { ScenarioSkillFocus } from '@/features/scenarios/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

// SkillFocusPreviewModal only uses scenario.slug to fetch its own data internally;
// all other fields are replaced by the API response before they are rendered.
function previewScenarioStub(slug: string): ScenarioSkillFocus {
  return {
    id: 0,
    slug,
    title: '',
    focus: '',
    summary: '',
    skill_focus_type: 'command_specific',
    primary_focus_commands: [],
    difficulties: [],
    learning_unit_id: 0,
    lesson_id: 0,
  }
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p
      className="pl-3 text-[10px] font-bold uppercase tracking-[0.16em] text-muted-foreground/70"
      style={{ borderLeft: '2px solid hsl(var(--border))' }}
    >
      {children}
    </p>
  )
}

export function ModulesPage() {
  const queryClient = useQueryClient()
  const [searchParams, setSearchParams] = useSearchParams()
  // TODO(module-terminology): drop the legacy unit param after old links age out.
  const moduleParam = searchParams.get('module') ?? searchParams.get('unit')
  const focusedModuleId = moduleParam ? Number(moduleParam) : null
  // ?preview=slug is appended when the student navigates here via scaffold "Proceed to Command Preview"
  const autoPreviewSlug = searchParams.get('preview')
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
    if (focusedModuleId && Number.isFinite(focusedModuleId)) return
    window.scrollTo({ top: 0, behavior: 'auto' })
  }, [focusedModuleId])

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

  if (isLoading) {
    return (
      <LoadingState
        description="Getting your modules and practice progress ready."
        label="Loading modules"
        variant="page"
      />
    )
  }
  if (isError) return <ErrorState title="Could not load modules" description={error.message} />
  if (!data) return <ErrorState title="Could not load modules" description="The API returned no module data." />

  const orientationModules = data.filter((m) => m.is_orientation)
  const coreModules = data.filter((m) => !m.is_orientation)
  const coreOffset = orientationModules.length

  const renderCard = (module: (typeof data)[number], index: number) => (
    <div
      key={module.id}
      data-module-id={module.id}
      className="animate-fade-in-up"
      style={{ animationDelay: `${index * 100}ms` }}
    >
      <ModuleCard
        module={module}
        isExpanded={expandedModuleIds.has(module.id)}
        scenarioSummary={scenarioSummaryQuery.data?.[String(module.id)]}
        scenarioSummaryPending={scenarioSummaryQuery.isLoading}
        onToggle={() => toggleModule(module.id)}
      />
    </div>
  )

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-4">
      {/* Animated background orbs — same pattern as Dashboard */}
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div
          className="absolute"
          style={{
            width: '55%', height: '60%', left: '-8%', top: '15%',
            background: 'radial-gradient(ellipse at center, rgba(0,245,212,0.045) 0%, transparent 70%)',
            filter: 'blur(50px)',
            animation: 'bg-drift 18s ease-in-out infinite alternate',
          }}
        />
        <div
          className="absolute"
          style={{
            width: '45%', height: '50%', right: '-5%', bottom: '10%',
            background: 'radial-gradient(ellipse at center, rgba(0,180,216,0.035) 0%, transparent 70%)',
            filter: 'blur(50px)',
            animation: 'bg-drift 24s ease-in-out infinite alternate-reverse',
          }}
        />
      </div>

      <div>
        <h1
          className="text-4xl font-extrabold tracking-tight"
          style={{ textShadow: '0 0 30px rgba(0,245,212,0.35), 0 0 60px rgba(0,180,216,0.18)' }}
        >
          Modules
        </h1>
      </div>

      {/* Info banner */}
      <div
        className="flex items-start gap-2.5 rounded-md px-4 py-3 text-xs leading-5"
        style={{
          background: 'rgba(0,245,212,0.04)',
          border: '1px solid rgba(0,245,212,0.14)',
          borderLeft: '3px solid rgba(0,245,212,0.55)',
        }}
      >
        <Info className="mt-0.5 size-3.5 shrink-0 text-primary" />
        <p className="text-muted-foreground">
          <span className="font-semibold text-primary">New to Git?</span> We recommend completing{' '}
          <span className="font-semibold text-foreground">Module 0: Orientation</span> before the
          core modules — optional but helpful!
        </p>
      </div>

      {/* Getting Started */}
      <div className="flex flex-col gap-3 pt-1">
        <SectionLabel>Getting Started</SectionLabel>
        {orientationModules.map((module, i) => renderCard(module, i))}
      </div>

      {/* Divider */}
      <div className="border-t border-border/40" />

      {/* Core Modules */}
      <div className="flex flex-col gap-3 pt-1">
        <SectionLabel>Core Modules</SectionLabel>
        {coreModules.map((module, i) => renderCard(module, coreOffset + i))}
      </div>
      {autoPreviewSlug ? (
        <SkillFocusPreviewModal
          scenario={previewScenarioStub(autoPreviewSlug)}
          onClose={() => {
            setSearchParams(
              (prev) => {
                const next = new URLSearchParams(prev)
                next.delete('preview')
                return next
              },
              { replace: true },
            )
          }}
        />
      ) : null}
    </div>
  )
}
