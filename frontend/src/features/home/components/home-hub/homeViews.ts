import { Map, Sparkles, UserRound, type LucideIcon } from 'lucide-react'

/**
 * Home is one surface with three categories, switched by a dropdown rather than a
 * tab strip. Every category answers a single question, so a learner always knows
 * which one to open.
 *
 * Progress and Run results used to be separate categories, but they reported the
 * same facts under different names — the citadel meter and the "Levels finished"
 * tile were both the backend's one finish rate. They are one category now, and
 * each number is stated exactly once.
 */
export type HomeView = 'progress' | 'skills' | 'profile'

export type HomeViewOption = {
  id: HomeView
  label: string
  blurb: string
  Icon: LucideIcon
}

export const HOME_VIEWS: readonly HomeViewOption[] = [
  {
    id: 'progress',
    label: 'Progress',
    blurb: 'How far through the story you are, your recent activity, and your run record',
    Icon: Map,
  },
  {
    id: 'skills',
    label: 'Skills & achievements',
    blurb: 'How confidently you handle each Git command, and what you have earned',
    Icon: Sparkles,
  },
  {
    id: 'profile',
    label: 'Profile',
    blurb: 'Your rank, your companion, and the spells you have learned',
    Icon: UserRound,
  },
] as const

export const DEFAULT_HOME_VIEW: HomeView = 'progress'

export function homeViewFromParam(value: string | null): HomeView {
  const match = HOME_VIEWS.find((option) => option.id === value)
  return match ? match.id : DEFAULT_HOME_VIEW
}

export function homeViewOption(view: HomeView): HomeViewOption {
  return HOME_VIEWS.find((option) => option.id === view) ?? HOME_VIEWS[0]
}
