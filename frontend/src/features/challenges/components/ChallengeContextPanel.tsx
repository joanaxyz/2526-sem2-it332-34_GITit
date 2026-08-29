import { Clock, Smile } from 'lucide-react'

import type { ChallengeRun } from '@/features/challenges/types'
import {
  DifficultyChip,
  type LevelFact,
  LevelStoryCard,
  RewardValue,
  StarTriplet,
} from '@/shared/level/components/LevelContextPanel'
import { BustIcon, RookIcon, StarSolidIcon } from '@/shared/level/components/workspaceIcons'
import { hasLevelContext, normalizeLevelContext } from '@/shared/level/utils/levelContext'

export function ChallengeContextPanel({ run }: { run: ChallengeRun }) {
  const context = contextForRun(run)
  const facts: LevelFact[] = [
    {
      label: 'Mode',
      icon: RookIcon,
      value: `Challenge${run.replay ? ' · Replay' : ''}`,
    },
    ...(run.difficulty
      ? [{ label: 'Difficulty', icon: Smile, value: <DifficultyChip difficulty={run.difficulty} /> }]
      : []),
    {
      label: 'Stars',
      icon: StarSolidIcon,
      iconClass: 'lvlctx-icon--amber',
      value: <StarTriplet count={run.stars || run.mastery_progress.stars || 0} />,
    },
    ...(run.reward_coins
      ? [{ label: 'Reward', icon: Clock, value: <RewardValue coins={run.reward_coins} /> }]
      : []),
    {
      label: 'Attempts',
      icon: BustIcon,
      value: <span className="lvlctx-num">{Math.max(1, run.counts.total_attempts)}</span>,
    },
  ]

  return (
    <LevelStoryCard
      title={run.challenge.title}
      context={context}
      facts={facts}
      labels={{
        story: 'Scenario',
        task: 'Objective',
        details: 'Required values',
        detailsAriaLabel: 'Values required by the challenge scenario and objective',
      }}
      showHeader={false}
      showDetailLabels
      tourTarget="challenge-brief"
    />
  )
}

function contextForRun(run: ChallengeRun) {
  const context = normalizeLevelContext(run.scenario_context)
  const fallback = normalizeLevelContext({
    story: run.challenge.narrative,
    task: run.challenge.summary,
  })

  return hasLevelContext(context) ? context : fallback
}
