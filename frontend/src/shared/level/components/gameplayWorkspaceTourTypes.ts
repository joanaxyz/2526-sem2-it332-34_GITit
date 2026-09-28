import type { LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'

import type { TourLayout, WorkspaceTourPlacement } from './gameplayWorkspaceTourLayout'

export type WorkspaceTourStep = {
  id: string
  selector: string
  icon: LucideIcon
  title: string
  body: ReactNode
  placement?: WorkspaceTourPlacement
  optional?: boolean
}

export type WorkspaceTourCloseReason = 'finish' | 'skip'

export type CollapseVector = {
  x: number
  y: number
  scale: number
}

/** A card inside the guide: the main card, and (wide screens) the one beside it. */
export type WorkspaceTourPane = 'main' | 'aside'

export type WorkspaceTourSize = { width: number; height: number }

export type WorkspaceTourPosition = { left: number; top: number }

/** Layout, plus the main card's measured size when the cards float separately. */
export type MeasuredWorkspaceTourLayout = TourLayout & { mainSize?: WorkspaceTourSize }

export type ResolvedWorkspaceTourStep = {
  step: WorkspaceTourStep
  target: HTMLElement
}
