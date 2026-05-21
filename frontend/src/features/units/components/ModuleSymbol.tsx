import { BookOpen, Compass, FolderOpen, GitBranch, GitMerge, LifeBuoy, type LucideIcon } from 'lucide-react'

import type { LearningUnit } from '@/features/units/types'
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
}

const FALLBACK_SYMBOL: ModuleSymbolConfig = { icon: BookOpen, shortLabel: 'Module' }

function getModuleSymbol(unit: Pick<LearningUnit, 'slug' | 'is_orientation'>) {
  if (unit.is_orientation) return MODULE_SYMBOLS.orientation
  return MODULE_SYMBOLS[unit.slug] ?? FALLBACK_SYMBOL
}

export function ModuleSymbol({
  unit,
  className,
}: {
  unit: Pick<LearningUnit, 'slug' | 'title' | 'is_orientation'>
  className?: string
}) {
  const { icon: Icon, shortLabel } = getModuleSymbol(unit)

  return (
    <div
      className={cn(
        'flex size-12 flex-col items-center justify-center gap-0.5 rounded-md border border-border bg-secondary text-primary',
        className,
      )}
      title={`${shortLabel}: ${unit.title}`}
      aria-label={`${shortLabel} module: ${unit.title}`}
    >
      <Icon className="size-5 shrink-0" aria-hidden />
      <span className="text-[10px] font-bold leading-none tracking-tight">{shortLabel}</span>
    </div>
  )
}
