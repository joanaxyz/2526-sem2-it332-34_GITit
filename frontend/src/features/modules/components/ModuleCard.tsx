import { useEffect, useRef, useState } from 'react'
import type { CSSProperties } from 'react'

import { ModulePracticeHub } from '@/features/modules/components/ModulePracticeHub'
import { ModuleSymbol } from '@/features/modules/components/ModuleSymbol'
import { getModuleAccent } from '@/features/modules/moduleColors'
import type { LearningModule } from '@/features/modules/types'
import { ProgressBar } from '@/shared/components/ProgressBar'
import { cn } from '@/shared/utils/cn'

function StatusBadge({ progress }: { progress: number }) {
  if (progress >= 100) {
    return (
      <span className="inline-flex items-center rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold leading-none text-emerald-400">
        Completed
      </span>
    )
  }
  if (progress > 0) {
    return (
      <span className="inline-flex items-center rounded-full border border-primary/30 bg-primary/10 px-2 py-0.5 text-[10px] font-semibold leading-none text-primary">
        In Progress
      </span>
    )
  }
  return (
    <span className="inline-flex items-center rounded-full border border-border/60 bg-transparent px-2 py-0.5 text-[10px] font-semibold leading-none text-muted-foreground/70">
      Not Started
    </span>
  )
}

function useApproachingViewport() {
  const ref = useRef<HTMLElement | null>(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (visible || !ref.current) return
    const observer = new IntersectionObserver((entries) => {
      if (entries.some((entry) => entry.isIntersecting)) setVisible(true)
    }, { rootMargin: '420px' })
    observer.observe(ref.current)
    return () => observer.disconnect()
  }, [visible])

  return { ref, visible }
}

export function ModuleCard({
  module,
  index,
}: {
  module: LearningModule
  index: number
}) {
  const accent = getModuleAccent(module.number)
  const progressValue = Math.round(module.practice_completion?.value ?? 0)
  const { ref, visible } = useApproachingViewport()
  const side = index % 2 === 0 ? 'left' : 'right'

  return (
    <article
      ref={ref}
      className={cn(
        'learning-path-card relative w-full animate-fade-in-up rounded-lg border border-border bg-card/88 p-5 shadow-none backdrop-blur-sm',
        side === 'right' && 'lg:ml-auto',
      )}
      style={{
        '--module-color': accent.color,
        '--module-border-rest': accent.borderRgba,
        '--module-border-hover': accent.borderHoverRgba,
        '--module-glow': accent.glowRgba,
        animationDelay: `${index * 80}ms`,
      } as CSSProperties}
    >
      <div className="learning-path-node" />
      <div className="grid gap-5">
        <div className="grid w-full grid-cols-[3rem_minmax(0,1fr)] gap-4 text-left sm:grid-cols-[3.25rem_minmax(0,1fr)_minmax(10rem,13rem)]">
          <ModuleSymbol module={module} />
          <div className="min-w-0">
            <p className="font-mono text-xs font-bold" style={{ color: accent.color }}>
              Module {module.number}
            </p>
            <h2 className="mt-1 text-xl font-extrabold leading-tight">{module.title}</h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">{module.description}</p>
          </div>
          <div className="min-w-0 max-sm:col-span-2">
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-bold uppercase tracking-normal text-muted-foreground">Overall progress</span>
              <span className="font-mono text-xs" style={{ color: `${accent.color}B3` }}>{progressValue}%</span>
            </div>
            <ProgressBar value={progressValue} className="mt-2 h-2" glow fillAnimate fillFrom={accent.color} fillTo={accent.gradientTo} />
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <StatusBadge progress={progressValue} />
              <span className="font-mono text-[11px] text-muted-foreground">
                {module.command_topic_count} levels / {module.workflow_scenario_count} workflows
              </span>
            </div>
          </div>
        </div>
        <ModulePracticeHub enabled={visible} module={module} />
      </div>
    </article>
  )
}
