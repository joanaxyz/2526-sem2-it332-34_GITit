import { BookOpen, Compass, FolderOpen, GitBranch, GitMerge, LifeBuoy, type LucideIcon } from 'lucide-react'

import type { LearningModule } from '@/features/modules/types'
import { cn } from '@/shared/utils/cn'

type ModuleSymbolConfig = {
  icon: LucideIcon
  shortLabel: string
}

const MODULE_SYMBOLS: Record<string, ModuleSymbolConfig> = {
  orientation: { icon: Compass, shortLabel: 'Start' },
  'local-foundations': { icon: FolderOpen, shortLabel: 'Local' },
  'branching-navigation': { icon: GitBranch, shortLabel: 'Branch' },
  'collaboration-integration': { icon: GitMerge, shortLabel: 'Merge' },
  'recovery-repair': { icon: LifeBuoy, shortLabel: 'Recover' },
  'advanced-recovery-history': { icon: LifeBuoy, shortLabel: 'Recover' },
}

const FALLBACK_SYMBOL: ModuleSymbolConfig = { icon: BookOpen, shortLabel: 'Module' }

function getModuleSymbol(module: Pick<LearningModule, 'slug' | 'is_orientation'>) {
  if (module.is_orientation) return MODULE_SYMBOLS.orientation
  return MODULE_SYMBOLS[module.slug] ?? FALLBACK_SYMBOL
}

export function ModuleSymbol({
  module,
  className,
}: {
  module: Pick<LearningModule, 'slug' | 'title' | 'is_orientation'>
  className?: string
}) {
  const { icon: Icon, shortLabel } = getModuleSymbol(module)

  return (
    <div
      className={cn(
        'flex size-12 flex-col items-center justify-center gap-0.5 rounded-md border border-primary/25 bg-secondary text-primary transition-all duration-200 hover:border-primary/50 hover:shadow-aurora-sm',
        className,
      )}
      title={`${shortLabel}: ${module.title}`}
      aria-label={`${shortLabel} module: ${module.title}`}
    >
      <Icon className="size-5 shrink-0" aria-hidden />
      <span className="text-[10px] font-bold leading-none tracking-tight">{shortLabel}</span>
    </div>
  )
}
