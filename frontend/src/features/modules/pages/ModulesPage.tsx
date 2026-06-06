import { useEffect } from 'react'
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

  useEffect(() => {
    if (focusedModuleId && Number.isFinite(focusedModuleId)) return
    window.scrollTo({ top: 0, behavior: 'auto' })
  }, [focusedModuleId])

  useEffect(() => {
    if (!focusedModuleId || !modulesQuery.data?.length) return
    window.requestAnimationFrame(() => {
      document.querySelector(`[data-module-id="${focusedModuleId}"]`)?.scrollIntoView({
        block: 'center',
        behavior: 'smooth',
      })
    })
  }, [modulesQuery.data, focusedModuleId])

  if (foundationsQuery.isLoading || modulesQuery.isLoading) {
    return (
      <LoadingState
        description="Getting foundations, command adventures, and workflow scenarios ready."
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
    <div className="flex w-full flex-col gap-8">
      <header className="grid gap-3">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="font-mono text-xs font-bold uppercase tracking-normal text-primary">Curriculum V2</p>
            <h1 className="mt-2 text-3xl font-extrabold tracking-normal">Learning Path</h1>
          </div>
          <p className="max-w-2xl text-sm leading-6 text-muted-foreground">
            Build from foundations, clear command adventure levels, then solve workflows that combine the commands under Easy, Medium, and Hard constraints.
          </p>
        </div>
      </header>

      <section className="grid gap-3">
        <SectionHeader icon={BookOpenText} title="Foundations" meta={`${foundations.length} topics`} />
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
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
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-4">
        <SectionHeader icon={Layers3} title="Command adventures and workflow scenarios" meta={`${modules.length} modules`} />
        <div className="learning-path relative grid gap-8 py-2">
          {modules.map((module, index) => (
            <div
              className="relative grid lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]"
              data-module-id={module.id}
              key={module.id}
            >
              <div className={index % 2 === 0 ? 'lg:pr-12' : 'lg:col-start-2 lg:pl-12'}>
                <ModuleCard module={module} index={index} />
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
