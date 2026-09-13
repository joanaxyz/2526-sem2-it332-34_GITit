import { Map, Sparkles, UserRound, type LucideIcon } from 'lucide-react'

/**
 * Home is one surface with three categories, switched by a dropdown rather than a
 * tab strip. Every category answers a single question, so a learner always knows
 * which one to open.
 *
 * Profile leads and is what Home opens on: rank, companion and spellbook are the
 * things a player comes back to look at, and the companion is a prerequisite for
 * playing at all, so a player with none sees the gap immediately.
 *
 * Progress and Run results used to be separate categories, but they reported the
 * same facts under different names — the citadel meter and the "Levels finished"
 * tile were both the backend's one finish rate. They are one category now, and
 * each number is stated exactly once.
 */
export type HomeView = 'profile' | 'progress' | 'skills'

export type HomeViewOption = {
  id: HomeView
  label: string
  blurb: string
  Icon: LucideIcon
}

export const HOME_VIEWS: readonly HomeViewOption[] = [
  {
    id: 'profile',
    label: 'Profile',
    blurb: 'Your rank, your companion, and the spells you have learned',
    Icon: UserRound,
  },
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
] as const

export const DEFAULT_HOME_VIEW: HomeView = 'profile'

/**
 * Categories that no longer exist, pointed at the one that absorbed them, so a
 * bookmarked link still lands where its facts moved rather than silently
 * falling back to the default view.
 */
const LEGACY_HOME_VIEWS: Readonly<Record<string, HomeView>> = {
  results: 'progress',
}

export function homeViewFromParam(value: string | null): HomeView {
  const match = HOME_VIEWS.find((option) => option.id === value)
  if (match) return match.id
  return (value && LEGACY_HOME_VIEWS[value]) || DEFAULT_HOME_VIEW
}

export function homeViewOption(view: HomeView): HomeViewOption {
  return HOME_VIEWS.find((option) => option.id === view) ?? HOME_VIEWS[0]
}
