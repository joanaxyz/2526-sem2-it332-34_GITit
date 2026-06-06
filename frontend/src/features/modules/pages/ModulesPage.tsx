import { useCallback, useEffect, useState } from 'react'
import { BookOpenText, Layers3 } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'

import { modulesApi } from '@/features/modules/api/modulesApi'
import { ModuleCard } from '@/features/modules/components/ModuleCard'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

function SectionHeader({
  icon: Icon,
  title,
  meta,
}: {
  icon: typeof BookOpenText
  title: string
  meta?: string
}) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div className="flex items-center gap-2">
        <Icon className="size-4 text-primary" />
        <h2 className="text-sm font-extrabold uppercase tracking-normal">{title}</h2>
      </div>
      {meta ? <span className="font-mono text-xs text-muted-foreground">{meta}</span> : null}
    </div>
  )
}

export function ModulesPage() {
  const [searchParams] = useSearchParams()
  const moduleParam = searchParams.get('module')
  const focusedModuleId = moduleParam ? Number(moduleParam) : null
  const [expandedModuleIds, setExpandedModuleIds] = useState<Set<number>>(() => {
    if (focusedModuleId && Number.isFinite(focusedModuleId)) return new Set([focusedModuleId])
    return new Set()
  })
  const foundationsQuery = useQuery({
    queryKey: queryKeys.foundations,
    queryFn: modulesApi.listFoundations,
    staleTime: 5 * 60 * 1000,
  })
  const modulesQuery = useQuery({
    queryKey: queryKeys.modules,
    queryFn: modulesApi.listModules,
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
    if (!focusedModuleId || !modulesQuery.data?.length) return
    window.requestAnimationFrame(() => {
      document.querySelector(`[data-module-id="${focusedModuleId}"]`)?.scrollIntoView({
        block: 'start',
        behavior: 'smooth',
      })
    })
  }, [modulesQuery.data, focusedModuleId])

  if (foundationsQuery.isLoading || modulesQuery.isLoading) {
    return (
      <LoadingState
        description="Getting foundations, command drills, and workflow scenarios ready."
        label="Loading curriculum"
        variant="page"
      />
    )
  }
  if (foundationsQuery.isError) {
    return <ErrorState title="Could not load foundations" description={foundationsQuery.error.message} />
  }
  if (modulesQuery.isError) {
    return <ErrorState title="Could not load modules" description={modulesQuery.error.message} />
  }

  const foundations = foundationsQuery.data ?? []
  const modules = modulesQuery.data ?? []

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6">
      <header className="grid gap-2">
        <h1 className="text-3xl font-extrabold tracking-tight">Modules</h1>
        <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
          Build up from Git foundations, drill individual commands, then solve workflow scenarios with increasing constraints.
        </p>
      </header>

      <section className="grid gap-3">
        <SectionHeader icon={BookOpenText} title="Foundations" meta={`${foundations.length} topics`} />
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {foundations.map((topic) => (
            <article className="rounded-md border border-border bg-background/40 p-4" key={topic.id}>
              <div className="flex items-start gap-3">
                <span className="grid size-9 shrink-0 place-items-center rounded-md border border-primary/25 bg-primary/10 font-mono text-sm font-bold text-primary">
                  {topic.icon || topic.sort_order + 1}
                </span>
                <div>
                  <h2 className="text-base font-bold">{topic.title}</h2>
                  <p className="mt-1 text-sm leading-6 text-muted-foreground">{topic.summary}</p>
                </div>
              </div>
              {topic.cards?.length ? (
                <div className="mt-3 grid gap-2">
                  {topic.cards.slice(0, 2).map((card) => (
                    <div className="rounded-md border border-border/70 bg-secondary/25 px-3 py-2" key={card.title}>
                      <p className="text-xs font-bold">{card.title}</p>
                      <p className="mt-1 text-xs leading-5 text-muted-foreground">{card.body}</p>
                      {card.command ? <code className="mt-2 block font-mono text-xs text-primary">{card.command}</code> : null}
                    </div>
                  ))}
                </div>
              ) : null}
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-3">
        <SectionHeader icon={Layers3} title="Command drills and workflow scenarios" meta={`${modules.length} modules`} />
        <div className="flex flex-col gap-3">
          {modules.map((module, index) => (
            <div
              className="animate-fade-in-up"
              data-module-id={module.id}
              key={module.id}
              style={{ animationDelay: `${index * 70}ms` }}
            >
              <ModuleCard
                module={module}
                isExpanded={expandedModuleIds.has(module.id)}
                onToggle={() => toggleModule(module.id)}
              />
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
