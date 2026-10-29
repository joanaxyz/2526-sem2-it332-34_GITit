import { Smile, Target, TerminalSquare } from 'lucide-react'

import type { ChallengeRun } from '@/features/challenges/types'
import { DifficultyChip, StarTriplet } from '@/shared/level/components/LevelStatValues'
import { RookIcon, StarSolidIcon } from '@/shared/level/components/workspaceIcons'
import type { RepoGraphTrigger, WorkspaceStat } from '@/shared/level/workspace/types'
import { WorkspaceStatsBar } from '@/shared/level/workspace/WorkspaceStatsBar'
import { WorkspaceStatusHeader } from '@/shared/level/workspace/WorkspaceStatusHeader'
import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'

function challengeStats(run: ChallengeRun): WorkspaceStat[] {
  const starTarget = run.policy.min_counted_commands
  // The trial reward is paid once; every run after a clear is a replay.
  const rewardClaimed = run.replay || run.mastery_progress.cleared
  return [
    { label: 'Mode', icon: RookIcon, value: `Challenge Gate${run.replay ? ' · Replay' : ''}` },
    ...(run.difficulty
      ? [{ label: 'Difficulty', icon: Smile, value: <DifficultyChip difficulty={run.difficulty} /> }]
      : []),
    {
      label: run.status === 'started' ? 'Stars on clear' : 'Stars',
      icon: StarSolidIcon,
      iconClass: 'tier-stat-icon--amber',
      value: <StarTriplet count={run.status === 'started' ? run.star_breakdown?.available_stars ?? 0 : run.stars} mode="challenge" breakdown={run.star_breakdown} active={run.status === 'started'} savedStars={run.completion?.stars} />,
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
    ...(run.reward_coins
      ? [{
          label: 'Reward',
          icon: GitCoinIcon,
          value: rewardClaimed ? 'Claimed' : <span className="lvlctx-num">+{run.reward_coins} GitCoins</span>,
        }]
      : []),
  ]
}

/** The Challenge Gate trial's command bar, in the adventure workspace's shape. */
export function ChallengeStatusHeader({
  run,
  isExiting = false,
  isRetrying = false,
  onExit,
  onRetry,
  onStartOver,
  onReplay,
  repoGraph,
}: {
  run: ChallengeRun
  isExiting?: boolean
  isRetrying?: boolean
  onExit?: () => void
  onRetry?: () => void
  onStartOver?: () => void
  onReplay?: () => void
  repoGraph?: RepoGraphTrigger
}) {
  return (
    <WorkspaceStatusHeader
      label="Challenge command bar"
      missionLabel="Current challenge"
      title={run.challenge.title}
      stats={<WorkspaceStatsBar stats={challengeStats(run)} repoGraph={repoGraph} />}
      status={run.status}
      isExiting={isExiting}
      busy={isRetrying}
      onExit={onExit}
      onRetry={!run.replay && run.status === 'failed' ? onRetry : undefined}
      onStartOver={!run.replay && run.status === 'started' ? onStartOver : undefined}
      onReplay={run.replay ? onReplay : undefined}
    />
  )
}
