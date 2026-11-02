import { Clock, GitBranch, Layers, Target, TerminalSquare } from 'lucide-react'

import {
  LevelStoryCard,
  RewardValue,
  StarTriplet,
  type LevelFact,
} from '@/shared/level/components/LevelContextPanel'
import { RookIcon, StarSolidIcon } from '@/shared/level/components/workspaceIcons'
import { normalizeLevelContext } from '@/shared/level/utils/levelContext'
import type { AdventureAttempt, AdventureRun } from '@/features/adventures/types'

/**
 * Scenario story for an adventure level. Reuses the challenge workspace's
 * {@link LevelStoryCard}, passing the attempt's live objective checklist -
 * the objective scaffold is adventure-only.
 */
export function AdventureContextPanel({
  run,
  attempt,
}: {
  run: AdventureRun
  attempt: AdventureAttempt
}) {
  const context = normalizeLevelContext(attempt.scenario_context)
  const rewardCoins = attempt.level.reward_coins ?? 0
  const facts: LevelFact[] = [
    {
      label: 'Level Type',
      icon: RookIcon,
      value: `Adventure${attempt.level.is_required ? '' : ' · Optional'}`,
    },
    {
      label: 'Wave',
      icon: Layers,
      value: (
        <span className="lvlctx-num">
          {attempt.wave + 1} / {run.total_waves}
        </span>
      ),
    },
    {
      label: 'Stars',
      icon: StarSolidIcon,
      iconClass: 'lvlctx-icon--amber',
      value: <StarTriplet count={run.stars || 0} />,
    },
    {
      label: 'Commands',
      icon: TerminalSquare,
      value: (
        <span className="lvlctx-num" data-tour-target="command-budget">
          {attempt.counts.counted_command_count} / {attempt.command_budget.max_counted_commands}
        </span>
      ),
    },
    {
      label: 'Star target',
      icon: Target,
      value: (
        <span className="lvlctx-num" data-tour-target="star-budget">
          ≤ {attempt.command_budget.min_counted_commands} {attempt.command_budget.min_counted_commands === 1 ? 'command' : 'commands'}
        </span>
      ),
    },
    ...(rewardCoins ? [{ label: 'Reward', icon: Clock, value: <RewardValue coins={rewardCoins} /> }] : []),
  ]

  return (
    <LevelStoryCard
      title={`Adventure: ${attempt.level.title}`}
      titleIcon={GitBranch}
      context={context}
      checks={attempt.objective_checks}
      facts={facts}
    />
  )
}
