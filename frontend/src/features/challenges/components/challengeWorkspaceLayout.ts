import { WORKSPACE_BATTLE_COLLAPSED_ROW, WORKSPACE_BATTLE_STAGE_ROW } from '@/shared/level/workspaceLayout'
import { storyPathWithQuery } from '@/shared/navigation/routes'
import type { ChallengeRun } from '@/features/challenges/types'

export const DEFAULT_TERMINAL_RATIO = 0.28
export const DEFAULT_TARGET_DIAGRAM_RATIO = 0.5
export const DEFAULT_TERMINAL_PANE_RATIO = 0.60
export const RESIZE_HANDLE_WIDTH = 6
export const BATTLE_STAGE_OPEN_ROW = WORKSPACE_BATTLE_STAGE_ROW
export const BATTLE_STAGE_COLLAPSED_ROW = WORKSPACE_BATTLE_COLLAPSED_ROW
export const TERMINAL_RATIO_KEY = 'workspace:terminal-ratio'
export const TARGET_DIAGRAM_RATIO_KEY = 'workspace:target-diagram-ratio'
export const TERMINAL_PANE_RATIO_KEY = 'workspace:terminal-pane-ratio'
export const DAG_ZOOM_KEY = 'workspace:challenge-dag-zoom-horizontal'
export const BATTLE_OPEN_KEY = 'workspace:battle-open'

const MIN_TERMINAL_PANE_WIDTH = 544
const MIN_FEEDBACK_PANE_WIDTH = 288
const MAX_FEEDBACK_PANE_WIDTH = 480

export function ratioSanitizer(min: number, max: number, fallback: number) {
  return (value: number) =>
    typeof value === 'number' && Number.isFinite(value) ? clamp(value, min, max) : fallback
}

export function stringList(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : []
}

export function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max)
}

export function mapUrlForRun(run: Pick<ChallengeRun, 'chapter'>) {
  return storyPathWithQuery(undefined, `chapter=${run.chapter.id}`)
}

export function constrainedTerminalPaneRatio(clientX: number, bounds: DOMRect) {
  const usableWidth = Math.max(bounds.width - RESIZE_HANDLE_WIDTH, 1)
  const rawRatio = (clientX - bounds.left) / bounds.width
  const minRatio = Math.max(
    MIN_TERMINAL_PANE_WIDTH / usableWidth,
    1 - MAX_FEEDBACK_PANE_WIDTH / usableWidth,
  )
  const maxRatio = 1 - MIN_FEEDBACK_PANE_WIDTH / usableWidth

  if (minRatio > maxRatio) {
    return clamp(rawRatio, 0.58, 0.86)
  }

  return clamp(rawRatio, minRatio, maxRatio)
}
