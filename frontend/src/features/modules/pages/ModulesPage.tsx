import { CheckCircle2, Layers3, ListChecks, Lock, Route, Swords, Trophy, Zap, type LucideIcon } from 'lucide-react'
import { motion } from 'motion/react'
import { useEffect, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'

import { towersApi } from '@/features/modules/api/modulesApi'
import { TowerPracticeHub } from '@/features/modules/components/ModulePracticeHub'
import type { LearningTower } from '@/features/modules/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { EmptyState } from '@/shared/components/EmptyState'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { ProgressBar } from '@/shared/components/ProgressBar'

function isFoundationsTower(tower: LearningTower) {
  return tower.number === 1 || tower.slug === 'creating-inspecting-repositories'
}

function towerTitle(tower: LearningTower) {
  return isFoundationsTower(tower) ? 'Foundations' : tower.title
}

function towerTotals(towers: LearningTower[]) {
  const commands = towers.reduce((sum, tower) => sum + tower.command_topic_count, 0)
  const challenges = towers.reduce((sum, tower) => sum + tower.workflow_scenario_count, 0)
  const numerator = towers.reduce((sum, tower) => sum + (tower.practice_completion?.numerator ?? 0), 0)
  const denominator = towers.reduce((sum, tower) => sum + (tower.practice_completion?.denominator ?? 0), 0)
  const progress = denominator ? Math.round((numerator / denominator) * 100) : 0

  return {
    commands,
    challenges,
    levels: challenges * 3,
    progress,
  }
}

function OverviewStat({
  icon: Icon,
  label,
  value,
}: {
  icon: LucideIcon
  label: string
  value: string | number
}) {
  return (
    <div className="tower-overview-stat">
      <span className="tower-overview-stat-icon">
        <Icon className="size-4" />
      </span>
      <span className="text-sm text-muted-foreground">{label}</span>
      <strong className="ml-auto text-sm text-foreground">{value}</strong>
    </div>
  )
}

function HowItWorksItem({ icon: Icon, children }: { icon: LucideIcon; children: string }) {
  return (
    <li className="tower-how-item">
      <span className="tower-how-icon">
        <Icon className="size-5" />
      </span>
      <span>{children}</span>
    </li>
  )
}

export function TowerPage() {
  const [searchParams] = useSearchParams()
  const towerParam = searchParams.get('tower') ?? searchParams.get('module')
  const focusedTowerId = towerParam ? Number(towerParam) : null
  const towersQuery = useQuery({
    queryKey: queryKeys.towers,
    queryFn: towersApi.listTowers,
    staleTime: 5 * 60 * 1000,
  })

  const towers = towersQuery.data ?? []
  const totals = useMemo(() => towerTotals(towers), [towers])

  useEffect(() => {
    if (!focusedTowerId || !Number.isFinite(focusedTowerId) || !towers.length) return
    window.requestAnimationFrame(() => {
      document.querySelector(`[data-tower-id="${focusedTowerId}"]`)?.scrollIntoView({
        block: 'start',
        behavior: 'smooth',
      })
    })
  }, [focusedTowerId, towers])

  if (towersQuery.isLoading) {
    return (
      <LoadingState
        description="Preparing the tower."
        label="Loading tower"
        variant="page"
      />
    )
  }
  if (towersQuery.isError) {
    return <ErrorState title="Could not load tower" description={towersQuery.error.message} />
  }
  if (!towers.length) {
    return <EmptyState title="No tower available" description="Publish a learning tower to start the climb." />
  }

  return (
    <div className="tower-page-shell">
      <div className="tower-sky" aria-hidden="true" />
      <section className="tower-stage-grid" aria-labelledby="tower-title">
        <motion.aside
          className="tower-overview-column"
          initial={{ opacity: 0, x: -18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.48, ease: [0.16, 1, 0.3, 1] }}
        >
          <div>
            <div className="tower-heading-row">
              <h1 id="tower-title" className="text-4xl font-black text-foreground">
                Git Tower
              </h1>
              <span className="tower-index-pill">
                <Zap className="size-3.5" />
                {towers.length} Towers
              </span>
            </div>
            <p className="mt-4 max-w-xs text-base leading-7 text-muted-foreground">
              Climb every Git tower in order. Each stage stacks directly below the last.
            </p>
          </div>

          <section className="tower-side-panel" aria-label="Tower overview">
            <div className="grid gap-4">
              <OverviewStat icon={ListChecks} label="Commands to learn" value={totals.commands} />
              <OverviewStat icon={Swords} label="Challenges" value={totals.challenges} />
              <OverviewStat icon={Layers3} label="Total levels" value={totals.levels} />
            </div>
            <div className="tower-progress-block">
              <div className="flex items-center justify-between gap-3">
                <span className="text-sm text-muted-foreground">Tower Progress</span>
                <strong className="font-mono text-sm text-foreground">{totals.progress}%</strong>
              </div>
              <ProgressBar value={totals.progress} className="mt-3 h-2.5 bg-secondary/70" glow fillAnimate />
            </div>
          </section>

          <section className="stage-reward-panel" aria-label="Stage reward">
            <div>
              <p className="text-sm text-muted-foreground">Stage Reward</p>
              <p className="mt-2 text-sm font-semibold text-foreground">Clear each Command Adventure</p>
              <p className="mt-3 inline-flex items-center gap-1.5 text-2xl font-black text-foreground">
                +25 <Zap className="size-5 text-warning" />
              </p>
            </div>
            <span className="stage-reward-icon">
              <img className="stage-reward-chest" src="/stage_reward_neon_chest.png" alt="" aria-hidden="true" />
            </span>
          </section>
        </motion.aside>

        <div className="tower-stack-column">
          {towers.map((tower, index) => (
            <TowerPracticeHub
              displayTitle={towerTitle(tower)}
              isFirst={index === 0}
              isLast={index === towers.length - 1}
              key={tower.id}
              sequenceIndex={index}
              tower={tower}
            />
          ))}
        </div>

        <motion.aside
          className="tower-how-panel"
          initial={{ opacity: 0, x: 18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.48, ease: [0.16, 1, 0.3, 1], delay: 0.08 }}
        >
          <h2 className="text-lg font-black text-primary">How it works</h2>
          <ul className="mt-6 grid gap-6">
            <HowItWorksItem icon={Swords}>Clear each Command Adventure to unlock challenges.</HowItWorksItem>
            <HowItWorksItem icon={Trophy}>Each challenge has Easy, Medium, and Hard levels.</HowItWorksItem>
            <HowItWorksItem icon={Lock}>Clear all stacked levels to complete the tower.</HowItWorksItem>
            <HowItWorksItem icon={CheckCircle2}>Progress saves after every cleared practice.</HowItWorksItem>
          </ul>
          <div className="tower-how-footer" aria-hidden="true">
            <Route className="size-4" />
            <span>Climb the tower</span>
          </div>
        </motion.aside>
      </section>
    </div>
  )
}

export const ModulesPage = TowerPage
