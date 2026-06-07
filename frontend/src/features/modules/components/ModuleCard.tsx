import type { CSSProperties } from 'react'
import { GitBranch } from 'lucide-react'
import { motion } from 'motion/react'

import { ModulePracticeHub } from '@/features/modules/components/ModulePracticeHub'
import { ModuleSymbol } from '@/features/modules/components/ModuleSymbol'
import { getModuleAccent } from '@/features/modules/moduleColors'
import type { LearningModule } from '@/features/modules/types'
import { cn } from '@/shared/utils/cn'

export function ModuleCard({
  module,
  index,
}: {
  module: LearningModule
  index: number
}) {
  const accent = getModuleAccent(module.number)
  const side = index % 2 === 0 ? 'left' : 'right'

  return (
    <motion.article
      className="learning-branch-row relative grid gap-4 lg:grid-cols-[minmax(0,1fr)_5.5rem_minmax(0,1fr)]"
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
      <motion.header
        className="module-route-strip lg:col-span-3"
        initial={{ opacity: 0, y: 12 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ amount: 0.7, once: false }}
        transition={{ duration: 0.42, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="flex min-w-0 items-center gap-3">
          <ModuleSymbol module={module} className="size-10 shrink-0 rounded-xl" />
          <div className="min-w-0">
            <h2 className="truncate text-lg font-black leading-tight md:text-xl">{module.title}</h2>
            <p className="mt-0.5 font-mono text-[10px] font-black uppercase tracking-[0.18em] text-muted-foreground">
              Command Adventure · Git it Challenge
            </p>
          </div>
        </div>
      </motion.header>

      <div className="learning-branch-track relative hidden items-center justify-center lg:flex lg:col-start-2 lg:row-start-2">
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

      <div className={cn('lg:col-start-3 lg:row-start-2', side === 'right' && 'lg:col-start-1')}>
        <ModulePracticeHub module={module} />
      </div>
    </motion.article>
  )
}
