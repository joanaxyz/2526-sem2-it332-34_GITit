import { Clock, Smile, Swords } from 'lucide-react'

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
      label: 'Level Type',
      icon: RookIcon,
      value: `Challenge Trial${run.replay ? ' · Replay' : ''}`,
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
      title={`Challenge: ${run.challenge.title}`}
      titleIcon={Swords}
      context={context}
      facts={facts}
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
