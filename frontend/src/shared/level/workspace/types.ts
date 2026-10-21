import type { QueryKey } from '@tanstack/react-query'
import type { ComponentType, ReactNode, RefObject } from 'react'

import type { LevelScenarioContext, RepositorySnapshot } from '@/shared/level/types'

/** Mirrors RESULT_TARGET_MATCHED in common/constants.py. */
export const RESULT_TARGET_MATCHED = 'TargetMatched'

/** One logged turn, as the contextual feedback panel reads it. */
type WorkspaceStep = {
  id: number
  command_text: string
  result_category: string
  contextual_feedback?: string | null
  created_at: string
}

/**
 * What the gameplay workspace reads from a run. Adventure tier runs and
 * Challenge Gate runs both satisfy it; anything that differs between the two
 * travels in a WorkspaceScene.
 */
export type WorkspaceRun = {
  id: number
  status: string
  scenario_context: LevelScenarioContext
  story: { slug: string; world_slug: string } | null
  variant: { id: number; label: string }
  counts: {
    counted_action_total: number
    maximum_counted_commands: number
    remaining_counted_commands: number
  }
  scaffolding: {
    live_dag: boolean
    expected_state: boolean
    contextual_feedback: boolean
  }
  repository_state: RepositorySnapshot
  expected_state: RepositorySnapshot | null
  steps: readonly WorkspaceStep[]
}

/** The facts the workspace needs about where a run belongs. */
export type WorkspaceScene = {
  /** Shown when the variant has no label of its own. */
  title: string
  /** Root folder name of the project tree. */
  rootName: string
  /** The run's query; the terminal's working directory is cached beside it. */
  runQueryKey: QueryKey
  /**
   * Seeds the battle. `stageKey` names the playable unit (a tier or a trial),
   * `levelKey` the level that picks the monster.
   */
  battle: { stageKey: string; levelKey: string }
}

/** One row of the Objectives card. `failed` is reserved for objectives a run can break. */
export type WorkspaceObjectiveStatus = 'pending' | 'done' | 'failed'

export type WorkspaceObjective = {
  id: string
  text: string
  status: WorkspaceObjectiveStatus
}

/** One fact in the stats bar under the command bar. */
export type WorkspaceStat = {
  label: string
  icon: ComponentType<{ className?: string }>
  iconClass?: string
  value: ReactNode
}

/** The drawer trigger, present only while the layout puts the graph in a drawer. */
export type RepoGraphTrigger = {
  open: boolean
  hasUpdate: boolean
  controls: string
  buttonRef: RefObject<HTMLButtonElement | null>
  onOpen: () => void
}

/** Set while the layout shows the graph as a slide-over drawer (700-1099px). */
export type RepoGraphDrawer = {
  open: boolean
  /** Increments on every opening, so the diagrams refit as they appear. */
  openCount: number
  onClose: () => void
}
