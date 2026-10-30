import { Layers, Smile, TerminalSquare } from 'lucide-react'

import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { DifficultyChip, StarTriplet } from '@/shared/level/components/LevelStatValues'
import { RookIcon, StarSolidIcon } from '@/shared/level/components/workspaceIcons'
import type { RepoGraphTrigger, WorkspaceStat } from '@/shared/level/workspace/types'
import { WorkspaceStatsBar } from '@/shared/level/workspace/WorkspaceStatsBar'
import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'

const HIDDEN_FOR_TRANSFER = new Set(['Stars', 'Reward'])

/** The adventure tier's facts in the shared stats strip under the command bar. */
export function TierStatsBar({ run, repoGraph }: { run: TierRun; repoGraph?: RepoGraphTrigger }) {
  const rewardClaimed = run.reward.claimed || Boolean(run.rewards?.coins_awarded)
  const stats: WorkspaceStat[] = [
    { label: 'Mode', icon: RookIcon, value: run.transfer ? 'Transfer checkpoint' : `Adventure${run.replay ? ' · Replay' : ''}` },
    ...(run.difficulty
      ? [{ label: 'Difficulty', icon: Smile, value: <DifficultyChip difficulty={run.difficulty} /> }]
      : []),
    ...(run.scenario.total > 1 && run.scenario.index
      ? [
          {
            label: 'Scenario',
            icon: Layers,
            value: (
              <span className="lvlctx-num" title={run.scenario.title || undefined}>
                {run.scenario.index} / {run.scenario.total}
              </span>
            ),
          },
        ]
      : []),
    {
      label: 'Stars',
      icon: StarSolidIcon,
      iconClass: 'tier-stat-icon--amber',
      value: <span data-tour-target="star-budget"><StarTriplet count={run.status === 'started' ? run.star_breakdown?.available_stars ?? 0 : run.stars} breakdown={run.star_breakdown} active={run.status === 'started'} savedStars={run.completion?.stars} multiScenario={run.scenario.total > 1} /></span>,
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
      label: 'Reward',
      icon: GitCoinIcon,
      value: rewardClaimed ? (
        'Claimed'
      ) : (
        <span className="lvlctx-num">+{run.reward.coins} GitCoins</span>
      ),
    },
  ]

  return (
    <WorkspaceStatsBar
      stats={stats.filter((stat) => !run.transfer || !HIDDEN_FOR_TRANSFER.has(stat.label))}
      compactLabels={['Mode', 'Difficulty']}
      repoGraph={repoGraph}
    />
  )
}
