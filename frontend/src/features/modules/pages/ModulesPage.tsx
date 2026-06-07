import { useEffect, useRef } from 'react'
import { BookOpenText, GitBranch, Layers3, Sparkles, TerminalSquare } from 'lucide-react'
import { motion, useScroll, useSpring } from 'motion/react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'

import { modulesApi } from '@/features/modules/api/modulesApi'
import { ModuleCard } from '@/features/modules/components/ModuleCard'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

function RouteKicker({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl border border-border/70 bg-background/35 px-4 py-3">
      <p className="font-mono text-[10px] font-black uppercase tracking-[0.18em] text-muted-foreground">{label}</p>
      <p className="mt-1 text-2xl font-black text-primary">{value}</p>
    </div>
  )
}

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
        <span className="grid size-8 place-items-center rounded-full border border-primary/20 bg-primary/10 text-primary">
          <Icon className="size-4" />
        </span>
        <h2 className="text-xs font-extrabold uppercase tracking-[0.18em] text-muted-foreground">{title}</h2>
      </div>
      {meta ? <span className="font-mono text-xs text-muted-foreground">{meta}</span> : null}
    </div>
  )
}

export function ModulesPage() {
  const [searchParams] = useSearchParams()
  const moduleParam = searchParams.get('module')
  const focusedModuleId = moduleParam ? Number(moduleParam) : null
  const pathRef = useRef<HTMLDivElement | null>(null)
  const { scrollYProgress } = useScroll({ target: pathRef, offset: ['start 82%', 'end 18%'] })
  const pathScaleY = useSpring(scrollYProgress, { stiffness: 120, damping: 28, mass: 0.35 })
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
        description="Building the practice map."
        label="Loading route"
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
  const totalChallenges = modules.reduce((sum, module) => sum + module.workflow_scenario_count, 0)
  const totalCommandLevels = modules.reduce((sum, module) => sum + module.command_topic_count, 0)

  return (
    <div className="modules-page-shell flex w-full flex-col gap-8">
      <motion.header
        className="module-quest-hero relative overflow-hidden rounded-[2rem] border border-primary/20 bg-card/55 p-6 shadow-[0_28px_90px_rgba(0,0,0,0.26)] md:p-8"
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="module-quest-hero-glow" aria-hidden="true" />
        <div className="relative grid gap-6 lg:grid-cols-[minmax(0,1fr)_22rem] lg:items-end">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-3 py-1 font-mono text-xs font-bold uppercase tracking-[0.16em] text-primary">
              <GitBranch className="size-3.5" />
              Branch map
            </div>
            <h1 className="mt-4 max-w-3xl text-4xl font-black tracking-tight md:text-6xl">
              Pick a route. Clear the tower.
            </h1>
            <p className="mt-3 max-w-xl text-sm leading-6 text-muted-foreground">
              Command Adventure unlocks the skills. Git it Challenge tests the flow.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <RouteKicker label="Modules" value={modules.length} />
            <RouteKicker label="Levels" value={totalCommandLevels} />
            <RouteKicker label="Towers" value={totalChallenges} />
          </div>
        </div>
      </motion.header>

      <section className="grid gap-3">
        <SectionHeader icon={BookOpenText} title="Foundations" meta={`${foundations.length} gates`} />
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {foundations.map((topic, index) => (
            <motion.article
              className="foundation-gate rounded-2xl border border-border/70 bg-background/35 p-4 shadow-[0_14px_38px_rgba(0,0,0,0.16)]"
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ amount: 0.35, once: false }}
              transition={{ duration: 0.38, delay: index * 0.03 }}
              key={topic.id}
            >
              <div className="flex items-center gap-3">
                <span className="grid size-10 shrink-0 place-items-center rounded-xl border border-primary/25 bg-primary/10 font-mono text-sm font-bold text-primary">
                  {topic.icon || topic.sort_order + 1}
                </span>
                <div className="min-w-0">
                  <h2 className="truncate text-base font-black">{topic.title}</h2>
                  <p className="mt-0.5 line-clamp-1 text-xs text-muted-foreground">{topic.summary}</p>
                </div>
              </div>
            </motion.article>
          ))}
        </div>
      </section>

      <section className="grid gap-4">
        <SectionHeader icon={Layers3} title="Practice route" meta={`${modules.length} modules`} />
        <div ref={pathRef} className="learning-branch relative grid gap-12 py-4">
          <div className="learning-branch-spine" aria-hidden="true" />
          <motion.div className="learning-branch-spine-fill" style={{ scaleY: pathScaleY }} aria-hidden="true" />
          <div className="learning-branch-start" aria-hidden="true">
            <Sparkles className="size-4" />
          </div>
          {modules.map((module, index) => (
            <ModuleCard module={module} index={index} key={module.id} />
          ))}
          <div className="learning-branch-finish" aria-hidden="true">
            <TerminalSquare className="size-4" />
          </div>
        </div>
      </section>
    </div>
  )
}
