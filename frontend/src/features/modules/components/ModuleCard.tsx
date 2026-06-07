import type { CSSProperties } from 'react'
import { Gamepad2, GitBranch, Route } from 'lucide-react'
import { motion } from 'motion/react'

import { ModulePracticeHub } from '@/features/modules/components/ModulePracticeHub'
import { ModuleSymbol } from '@/features/modules/components/ModuleSymbol'
import { getModuleAccent } from '@/features/modules/moduleColors'
import type { LearningModule } from '@/features/modules/types'
import { ProgressBar } from '@/shared/components/ProgressBar'
import { cn } from '@/shared/utils/cn'

function StatusBadge({ progress }: { progress: number }) {
  const label = progress >= 100 ? 'Cleared' : progress > 0 ? 'Active' : 'Ready'
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.14em] leading-none',
        progress >= 100
          ? 'border-primary/30 bg-primary/10 text-primary'
          : progress > 0
            ? 'border-accent/30 bg-accent/10 text-accent'
            : 'border-border/70 bg-background/45 text-muted-foreground',
      )}
    >
      {label}
    </span>
  )
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
  const side = index % 2 === 0 ? 'left' : 'right'

  return (
    <motion.article
      className="learning-branch-row relative grid gap-4 lg:grid-cols-[minmax(0,0.9fr)_5.5rem_minmax(0,1.25fr)]"
      data-module-id={module.id}
      initial={{ opacity: 0, y: 38, scale: 0.98 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ amount: 0.2, once: false, margin: '-10% 0px -10% 0px' }}
      transition={{ duration: 0.58, ease: [0.16, 1, 0.3, 1] }}
      style={
        {
          '--module-color': accent.color,
          '--module-border-rest': accent.borderRgba,
          '--module-border-hover': accent.borderHoverRgba,
          '--module-glow': accent.glowRgba,
        } as CSSProperties
      }
    >
      <div className={cn('hidden lg:block', side === 'right' && 'lg:col-start-3')}>
        <motion.div
          className="module-route-label lg:sticky lg:top-24"
          initial={{ opacity: 0, x: side === 'left' ? -24 : 24, rotate: side === 'left' ? -1.5 : 1.5 }}
          whileInView={{ opacity: 1, x: 0, rotate: 0 }}
          viewport={{ amount: 0.6, once: false }}
          transition={{ duration: 0.48, delay: 0.06 }}
        >
          <ModuleSymbol module={module} className="size-14 rounded-2xl" />
          <div className="min-w-0">
            <p className="font-mono text-xs font-black uppercase tracking-[0.18em]" style={{ color: accent.color }}>
              Module {module.number}
            </p>
            <h2 className="mt-1 line-clamp-2 text-xl font-black leading-tight">{module.title}</h2>
            <div className="mt-3 flex items-center gap-2">
              <StatusBadge progress={progressValue} />
              <span className="font-mono text-xs text-muted-foreground">{progressValue}%</span>
            </div>
            <ProgressBar value={progressValue} className="mt-2 h-1.5" glow fillAnimate fillFrom={accent.color} fillTo={accent.gradientTo} />
          </div>
        </motion.div>
      </div>

      <div className="learning-branch-track relative hidden items-center justify-center lg:flex lg:col-start-2">
        <motion.div
          className="learning-branch-node"
          initial={{ scale: 0.6, opacity: 0 }}
          whileInView={{ scale: 1, opacity: 1 }}
          viewport={{ amount: 0.55, once: false }}
          transition={{ duration: 0.42, type: 'spring', stiffness: 280, damping: 18 }}
        >
          <GitBranch className="size-5" />
        </motion.div>
        <motion.div
          className={cn('learning-branch-connector', side === 'right' && 'learning-branch-connector-right')}
          initial={{ scaleX: 0, opacity: 0 }}
          whileInView={{ scaleX: 1, opacity: 1 }}
          viewport={{ amount: 0.5, once: false }}
          transition={{ duration: 0.48, ease: [0.16, 1, 0.3, 1], delay: 0.1 }}
        />
      </div>

      <div className={cn('lg:col-start-3', side === 'right' && 'lg:col-start-1 lg:row-start-1')}>
        <div className="mb-3 flex items-start gap-3 rounded-[1.35rem] border border-border/70 bg-card/50 p-4 lg:hidden">
          <ModuleSymbol module={module} />
          <div className="min-w-0 flex-1">
            <p className="font-mono text-xs font-black uppercase tracking-[0.16em] text-primary">Module {module.number}</p>
            <h2 className="mt-1 text-xl font-black leading-tight">{module.title}</h2>
            <div className="mt-3 flex items-center gap-3">
              <ProgressBar value={progressValue} className="h-1.5 flex-1" glow />
              <span className="font-mono text-xs text-muted-foreground">{progressValue}%</span>
            </div>
          </div>
        </div>
        <div className="mb-3 hidden items-center gap-2 text-xs font-bold uppercase tracking-[0.18em] text-muted-foreground lg:flex">
          <Route className="size-4 text-primary" />
          <span>{module.command_topic_count} command levels</span>
          <span className="text-border">/</span>
          <Gamepad2 className="size-4 text-accent" />
          <span>{module.workflow_scenario_count} challenges</span>
        </div>
        <ModulePracticeHub module={module} />
      </div>
    </motion.article>
  )
}
