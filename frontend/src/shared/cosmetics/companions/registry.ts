import type { CompanionDef } from '@/shared/cosmetics/types'

import blackData from './data/black.json'
import blueData from './data/blue.json'
import whiteData from './data/white.json'

/** The default companion everyone owns. The visible name remains Blue. */
export const DEFAULT_COMPANION_SLUG = 'blue'

/**
 * Every companion, keyed by slug. Code-defined, no DB. The shop lists these;
 * ownership + active selection are the only things the backend stories.
 */
export const COMPANIONS: Record<string, CompanionDef> = {
  [DEFAULT_COMPANION_SLUG]: blueData as unknown as CompanionDef,
  white: whiteData as unknown as CompanionDef,
  black: blackData as unknown as CompanionDef,
}

export function getCompanion(slug: string | null | undefined): CompanionDef {
  return (slug && COMPANIONS[slug]) || COMPANIONS[DEFAULT_COMPANION_SLUG]
}

export function listCompanions(): CompanionDef[] {
  return Object.values(COMPANIONS)
}
