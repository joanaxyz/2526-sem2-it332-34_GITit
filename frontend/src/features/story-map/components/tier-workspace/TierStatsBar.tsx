import { GitBranch, Smile, Target, TerminalSquare } from 'lucide-react'
import type { ComponentType, ReactNode, RefObject } from 'react'

import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { DifficultyChip, StarTriplet } from '@/shared/level/components/LevelContextPanel'
import { RookIcon, StarSolidIcon } from '@/shared/level/components/workspaceIcons'
import { cn } from '@/shared/utils/cn'

type TierStat = {
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

/**
 * Full-width run status strip under the command bar: the level facts that used
 * to close the context card. The command budget and star target keep their
 * tour anchors here.
 */
export function TierStatsBar({ run, repoGraph }: { run: TierRun; repoGraph?: RepoGraphTrigger }) {
  const starTarget = run.policy.min_counted_commands
  const stats: TierStat[] = [
    { label: 'Mode', icon: RookIcon, value: `Adventure${run.replay ? ' · Replay' : ''}` },
    ...(run.difficulty
      ? [{ label: 'Difficulty', icon: Smile, value: <DifficultyChip difficulty={run.difficulty} /> }]
      : []),
    {
      label: 'Stars',
      icon: StarSolidIcon,
      iconClass: 'tier-stat-icon--amber',
      value: <StarTriplet count={run.stars || 0} />,
    },
    {
      label: 'Commands',
      icon: TerminalSquare,
      value: (
        <span className="lvlctx-num" data-tour-target="command-budget">
          {run.counts.counted_action_total} / {run.policy.max_counted_commands}
        </span>
      ),
    },
    {
      label: 'Star target',
      icon: Target,
      value: (
        <span className="lvlctx-num" data-tour-target="star-budget">
          ≤ {starTarget} {starTarget === 1 ? 'command' : 'commands'}
        </span>
      ),
    },
  ]

  return (
    <div className="tier-stats-bar" role="group" aria-label="Level status">
      <dl className="tier-stats">
        {stats.map((stat) => (
          <div className="tier-stat" key={stat.label}>
            <dt>
              <stat.icon aria-hidden="true" className={cn('tier-stat-icon', stat.iconClass)} />
              {stat.label}
            </dt>
            <dd>{stat.value}</dd>
          </div>
        ))}
      </dl>
      {repoGraph ? (
        <button
          ref={repoGraph.buttonRef}
          type="button"
          className="tier-repo-graph-button"
          aria-haspopup="dialog"
          aria-expanded={repoGraph.open}
          aria-controls={repoGraph.controls}
          data-tour-target="live-dag"
          onClick={repoGraph.onOpen}
        >
          <GitBranch aria-hidden="true" />
          Repo graph
          {repoGraph.hasUpdate ? (
            <>
              <span className="tier-repo-graph-dot" aria-hidden="true" />
              <span className="sr-only">, updated</span>
            </>
          ) : null}
        </button>
      ) : null}
    </div>
  )
}
