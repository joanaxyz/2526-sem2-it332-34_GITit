import { ArrowRight, Castle, RefreshCcw, Sparkles, XCircle } from 'lucide-react'
import { useEffect } from 'react'
import type { CSSProperties } from 'react'

import bugIconImage from '@/assets/images/battle-outcome/bug.png'
import skullIconImage from '@/assets/images/battle-outcome/skull.png'
import terminalIconImage from '@/assets/images/battle-outcome/terminal.png'
import warnIconImage from '@/assets/images/battle-outcome/warn.png'
import { ChallengeLevelNav } from '@/features/challenges/components/ChallengeLevelNav'
import type { ChallengeRun } from '@/features/challenges/types'
import { GameOutcomeModal } from '@/shared/level/components/game-outcome/GameOutcomeModal'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'
import { playGameOverSound, playVictorySound } from '@/shared/audio/battleAudio'

function difficultyLabel(run: ChallengeRun) {
  if (!run.difficulty) return 'Challenge'
  return run.difficulty.charAt(0).toUpperCase() + run.difficulty.slice(1)
}

export function ChallengeOutcomeModal({
  open,
  run,
  onClose,
  onBackToMap,
  onNextLevel,
  onRetry,
  onSelectLevel,
  busyLevelId,
  isStartingNextLevel = false,
  isRetrying = false,
  nextDifficultyLabel,
}: {
  open: boolean
  run: ChallengeRun
  onClose: () => void
  onBackToMap: () => void
  onNextLevel?: () => void
  onRetry?: () => void
  /** Start a fresh run on an arbitrary sibling level from the level navigator. */
  onSelectLevel?: (levelId: number) => void
  busyLevelId?: number | null
  isStartingNextLevel?: boolean
  isRetrying?: boolean
  nextDifficultyLabel?: string | null
}) {
  const isFailed = run.status === 'failed'
  const isReplay = run.replay
  const isNavigating = isStartingNextLevel || isRetrying || Boolean(busyLevelId)
  const canAdvance = !isReplay && run.status === 'completed' && Boolean(run.next_difficulty)

  useEffect(() => {
    if (!open) return
    if (isFailed) {
      playGameOverSound()
    } else {
      playVictorySound()
    }
  }, [isFailed, open])

  const headline = isReplay
    ? isFailed
      ? 'Replay ended'
      : 'Replay complete'
    : isFailed
      ? 'Attempt limit reached'
      : canAdvance
        ? 'Level ready'
        : 'Level cleared'

  const hitActionLimit = isFailed && run.counts.max_reached
  const message = isReplay
    ? isFailed
      ? "This free-play run ended before reaching the target state. It doesn't affect your saved progress. Play again whenever you like."
      : "Free play complete. This run is just a replay and doesn't change your saved progress."
    : isFailed
      ? hitActionLimit
        ? run.failure_reason ??
          'You used every counted action allowed for this attempt without reaching the target repository state. Start a fresh variant and try again.'
        : 'This attempt ended before the repository reached the target state. Start a fresh variant and try again.'
      : canAdvance
        ? 'Level cleared. The next difficulty is ready.'
        : 'Level cleared.'
  const Icon = isFailed ? XCircle : Sparkles
  const stats = [
    {
      label: 'Actions',
      numerator: run.counts.counted_action_total,
      denominator: run.counts.maximum_counted_commands,
      helper: `Full stars target: ${run.counts.minimum_counted_commands}`,
      iconSrc: terminalIconImage,
    },
    {
      label: 'Diagnostics',
      numerator: run.counts.non_counted_diagnostic_total,
      helper: 'Free inspections used',
      iconSrc: bugIconImage,
    },
    {
      label: 'Attempts',
      numerator: run.counts.total_attempts,
      helper: isReplay ? 'Free-play attempt' : 'Saved attempt count',
      iconSrc: skullIconImage,
    },
  ]

  const badges = (
    <>
      <Badge
        variant={isFailed ? 'destructive' : 'default'}
        className="game-outcome-badge"
        style={{ animationDelay: '60ms' } as CSSProperties}
      >
        {isFailed ? <img className="game-outcome-badge-icon" src={warnIconImage} alt="" aria-hidden="true" /> : null}
        {difficultyLabel(run)} {isFailed ? 'failed' : 'complete'}
      </Badge>
      {isReplay ? (
        <Badge
          variant="secondary"
          className="game-outcome-badge"
          style={{ animationDelay: '140ms' } as CSSProperties}
        >
          <RefreshCcw className="size-3.5" />
          Replay
        </Badge>
      ) : null}
    </>
  )

  const actions = isReplay ? (
    <>
      {onRetry ? (
        <Button type="button" disabled={isNavigating} onClick={onRetry}>
          <RefreshCcw data-icon="inline-start" />
          {isRetrying ? 'Starting fresh run' : 'Play again'}
        </Button>
      ) : null}
      <Button type="button" variant="ghost" disabled={isNavigating} onClick={onBackToMap}>
        <Castle data-icon="inline-start" />
        Back to Map
      </Button>
    </>
  ) : isFailed ? (
    <>
      {onRetry ? (
        <Button type="button" disabled={isNavigating} onClick={onRetry}>
          <RefreshCcw data-icon="inline-start" />
          {isRetrying ? 'Starting fresh variant' : 'Start fresh variant'}
        </Button>
      ) : null}
      <Button type="button" variant="ghost" disabled={isNavigating} onClick={onBackToMap}>
        <Castle data-icon="inline-start" />
        Back to Map
      </Button>
    </>
  ) : canAdvance ? (
    <>
      {onNextLevel && nextDifficultyLabel ? (
        <Button type="button" disabled={isNavigating} onClick={onNextLevel}>
          <ArrowRight data-icon="inline-start" />
          {isStartingNextLevel ? 'Opening next level' : `Next: ${nextDifficultyLabel}`}
        </Button>
      ) : null}
      <Button type="button" variant="secondary" disabled={isNavigating} onClick={onClose}>
        Stay in workspace
      </Button>
    </>
  ) : run.status === 'completed' ? (
    <Button type="button" variant="ghost" disabled={isNavigating} onClick={onBackToMap}>
      <Castle data-icon="inline-start" />
      Back to Map
    </Button>
  ) : null

  return (
    <GameOutcomeModal
      open={open}
      onClose={onClose}
      title={isFailed ? 'Level failed' : 'Level complete'}
      tone={isFailed ? 'failure' : 'success'}
      icon={Icon}
      resultLabel={isFailed ? 'Game Over' : 'You Won'}
      stars={run.stars}
      badges={badges}
      headline={headline}
      message={message}
      stats={stats}
      actions={actions}
    >
      {/* Level navigation is challenge-only - the adventure modal omits it. */}
      {!isReplay && onSelectLevel && run.sibling_levels && run.difficulty ? (
        <ChallengeLevelNav
          levels={run.sibling_levels}
          currentLevelId={run.challenge.level_id}
          onSelectLevel={onSelectLevel}
          busyLevelId={busyLevelId}
          disabled={isNavigating}
        />
      ) : null}
    </GameOutcomeModal>
  )
}
