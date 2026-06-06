import React from 'react'

import { ModulePracticeHub } from '@/features/modules/components/ModulePracticeHub'
import { ModuleSymbol } from '@/features/modules/components/ModuleSymbol'
import { getModuleAccent } from '@/features/modules/moduleColors'
import type { LearningModule } from '@/features/modules/types'
import { Card } from '@/shared/components/Card'
import { ExpandToggleButton } from '@/shared/components/ExpandToggleButton'
import { ProgressBar } from '@/shared/components/ProgressBar'

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

export function ModuleCard({
  module,
  isExpanded,
  onToggle,
}: {
  module: LearningModule
  isExpanded: boolean
  onToggle: () => void
}) {
  const accent = getModuleAccent(module.number)
  const progressValue = Math.round(module.practice_completion?.value ?? 0)
  const panelId = `module-panel-${module.id}`

  return (
    <Card
      className="module-card-hover overflow-hidden shadow-none"
      style={{
        '--module-color': accent.color,
        '--module-border-rest': accent.borderRgba,
        '--module-border-hover': accent.borderHoverRgba,
        '--module-glow': accent.glowRgba,
      } as React.CSSProperties}
    >
      <div className="grid w-full grid-cols-[3rem_minmax(0,1fr)_auto] items-center gap-4 p-5 text-left max-sm:grid-cols-[2.75rem_minmax(0,1fr)]">
        <ModuleSymbol module={module} />
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-lg font-bold leading-tight">
              <span style={{ color: accent.color }}>Module {module.number}:</span>{' '}
              {module.title}
            </h2>
          </div>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">{module.description}</p>
          <div className="mt-3 flex max-w-xl flex-wrap items-center gap-3">
            <ProgressBar value={progressValue} className="flex-1" glow fillAnimate fillFrom={accent.color} fillTo={accent.gradientTo} />
            <span className="font-mono text-xs" style={{ color: `${accent.color}B3` }}>{progressValue}%</span>
            <StatusBadge progress={progressValue} />
            <span className="font-mono text-xs text-muted-foreground">
              {module.command_topic_count} command topics / {module.workflow_scenario_count} workflows
            </span>
          </div>
        </div>
        <ExpandToggleButton expanded={isExpanded} controlsId={panelId} label={module.title} onToggle={onToggle} />
      </div>
      {isExpanded ? (
        <div
          className="grid"
          style={{
            gridTemplateRows: isExpanded ? '1fr' : '0fr',
            transition: 'grid-template-rows 0.35s cubic-bezier(0.16, 1, 0.3, 1)',
          }}
        >
          <div style={{ overflow: 'hidden' }}>
            <div className="border-t border-border/50 bg-secondary/20 p-5" id={panelId}>
              <ModulePracticeHub expanded={isExpanded} module={module} />
            </div>
          </div>
        </div>
      ) : null}
    </Card>
  )
}
