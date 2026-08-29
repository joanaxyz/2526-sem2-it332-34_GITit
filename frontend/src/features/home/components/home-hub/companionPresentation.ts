import type { CompanionDef } from '@/shared/cosmetics/types'

export type CompanionPresentation =
  | { status: 'loading' | 'error' | 'empty' }
  | { status: 'ready'; definition: CompanionDef; slug: string }

export type UnresolvedCompanionPresentation = Exclude<
  CompanionPresentation,
  { status: 'ready' }
>
