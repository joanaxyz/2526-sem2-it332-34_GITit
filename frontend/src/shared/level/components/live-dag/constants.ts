import type { EnteringDelta } from './types'

export const MIN_DAG_ZOOM = 0.55
export const MAX_DAG_ZOOM = 1.6

export const VARIANT_COLORS = {
  cyan: {
    border: 'rgba(var(--theme-primary-rgb),0.42)',
    headerBg: 'rgba(var(--theme-primary-rgb),0.025)',
    iconShadow: 'drop-shadow(0 0 4px rgba(var(--theme-primary-rgb),0.55))',
    titleClass: 'text-primary',
    gradientBg: 'radial-gradient(ellipse at 30% 40%, rgba(var(--theme-primary-rgb),0.05) 0%, transparent 62%)',
    dotColor: 'rgba(var(--theme-primary-rgb),0.06)',
    headNode: 'border-2 border-primary bg-primary/15 text-primary dag-head-glow',
    activePill: 'border-primary/55 bg-primary/10 text-primary shadow-[0_0_8px_rgba(var(--theme-primary-rgb),0.22)]',
    emptyHead: 'dag-head-glow border-2 border-dashed border-primary bg-primary/10 text-primary',
    emptyPill: 'border-primary/50 bg-primary/10 text-primary shadow-[0_0_6px_rgba(var(--theme-primary-rgb),0.2)]',
  },
} as const

export const NO_DELTA: EnteringDelta = { commits: new Set(), refsByCommit: new Map() }
