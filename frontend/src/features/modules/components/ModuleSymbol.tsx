import { BookOpen, GitBranch, GitCommitHorizontal, GitMerge, History, LifeBuoy, PackageOpen, Radar, Route, Server, type LucideIcon } from 'lucide-react'

import type { LearningModule } from '@/features/modules/types'
import { cn } from '@/shared/utils/cn'

type ModuleSymbolConfig = {
  icon: LucideIcon
  shortLabel: string
}

const MODULE_SYMBOLS: Record<string, ModuleSymbolConfig> = {
  'creating-inspecting-repositories': { icon: Radar, shortLabel: 'Scout' },
  'tracking-changes-snapshots': { icon: GitCommitHorizontal, shortLabel: 'Stage' },
  'branching-switching': { icon: GitBranch, shortLabel: 'Branch' },
  'merging-conflicts': { icon: GitMerge, shortLabel: 'Merge' },
  'undoing-recovery': { icon: LifeBuoy, shortLabel: 'Undo' },
  'temporary-work-patches': { icon: PackageOpen, shortLabel: 'Patch' },
  'remotes-collaboration': { icon: Server, shortLabel: 'Remote' },
  'integrated-workflows': { icon: Route, shortLabel: 'Quest' },
  'advanced-recovery-history': { icon: History, shortLabel: 'Recover' },
}

const FALLBACK_SYMBOL: ModuleSymbolConfig = { icon: BookOpen, shortLabel: 'Module' }

function getModuleSymbol(module: Pick<LearningModule, 'slug'>) {
  return MODULE_SYMBOLS[module.slug] ?? FALLBACK_SYMBOL
}

export function ModuleSymbol({
  module,
  className,
}: {
  module: Pick<LearningModule, 'slug' | 'title'>
  className?: string
}) {
  const { icon: Icon, shortLabel } = getModuleSymbol(module)

  return (
    <div
      className={cn(
        'flex size-12 flex-col items-center justify-center gap-0.5 rounded-md border bg-secondary transition-all duration-200 hover:brightness-110',
        className,
      )}
      style={{
        borderColor: 'var(--module-border-rest, rgba(0,212,170,0.25))',
        color: 'var(--module-color, hsl(var(--primary)))',
      }}
      title={`${shortLabel}: ${module.title}`}
      aria-label={`${shortLabel} module: ${module.title}`}
    >
      <Icon className="size-5 shrink-0" aria-hidden />
      <span className="text-[10px] font-bold leading-none tracking-tight">{shortLabel}</span>
    </div>
  )
}
