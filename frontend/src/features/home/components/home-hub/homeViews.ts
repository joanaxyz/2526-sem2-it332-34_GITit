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
 * Progress combines recent activity, active-curriculum context, and the
 * Modules 1–4 practice record. Legacy Run results links land there too.
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
    blurb: 'Your recent activity and practice goals across Arcane Spire',
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
