import { Map, RefreshCcw, Repeat2, RotateCcw, ScanSearch, Sparkles, SquareTerminal, TriangleAlert, XCircle } from 'lucide-react'
import { useEffect } from 'react'
import type { CSSProperties } from 'react'

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
  isStartingNextLevel?: boolean
  isRetrying?: boolean
  nextDifficultyLabel?: string | null
}) {
  const isFailed = run.status === 'failed'
  const isReplay = run.replay
  const isNavigating = isStartingNextLevel || isRetrying
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
      : "Nice run. Free play doesn't touch your saved progress, so replay as often as you like."
    : isFailed
      ? hitActionLimit
        ? run.failure_reason ??
          'You used every counted action allowed for this attempt without reaching the target repository state. Start a fresh variant and try again.'
        : 'This attempt ended before the repository reached the target state. Start a fresh variant and try again.'
      : canAdvance
        ? 'Level cleared. The next difficulty is ready.'
        : 'Level cleared.'
  const Icon = isFailed ? XCircle : Sparkles
  const targetActionsMet =
    !isFailed &&
    run.counts.counted_action_total > 0 &&
    run.counts.counted_action_total <= run.counts.minimum_counted_commands

  // Hitting the target lights the stat gold, matching the star and wordmark art.
  const actionsAccent = targetActionsMet ? 'hsl(var(--warning))' : 'hsl(var(--primary))'

  const stats = [
    {
      label: 'Actions',
      numerator: run.counts.counted_action_total,
      denominator: run.counts.minimum_counted_commands,
      helper: `Max allowed: ${run.counts.maximum_counted_commands}`,
      icon: SquareTerminal,
      accentColor: actionsAccent,
      targetMet: targetActionsMet,
    },
    {
      label: 'Diagnostics',
      numerator: run.counts.non_counted_diagnostic_total,
      helper: 'Free inspections used',
      icon: ScanSearch,
      accentColor: 'hsl(var(--primary))',
    },
    {
      label: 'Attempts',
      numerator: run.counts.total_attempts,
      helper: isReplay ? 'Free-play attempt' : 'Saved attempt count',
      icon: Repeat2,
      accentColor: 'hsl(var(--primary))',
    },
  ]

  const badges = (
    <>
      <Badge
        variant={isFailed ? 'secondary' : 'default'}
        className="game-outcome-badge"
        style={{ animationDelay: '60ms' } as CSSProperties}
      >
        {isFailed ? <TriangleAlert className="size-3.5" aria-hidden="true" /> : null}
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

  const headerActions = (
    <>
      {onRetry ? (
        <button
          type="button"
          className="game-outcome-header-btn"
          disabled={isNavigating}
          onClick={onRetry}
          aria-label={isReplay ? 'Play again' : isFailed ? 'Start fresh variant' : 'Play again'}
          title={isReplay ? 'Play again' : isFailed ? 'Start fresh variant' : 'Play again'}
        >
          <RotateCcw className="size-3.5" />
        </button>
      ) : null}
      <button
        type="button"
        className="game-outcome-header-btn"
        disabled={isNavigating}
        onClick={onBackToMap}
        aria-label="Back to Map"
        title="Back to Map"
      >
        <Map className="size-3.5" />
      </button>
    </>
  )

  const actions = canAdvance ? (
    onNextLevel && nextDifficultyLabel ? (
      <Button type="button" disabled={isNavigating} onClick={onNextLevel}>
        {isStartingNextLevel ? 'Opening next level…' : 'Continue'}
      </Button>
    ) : (
      <Button type="button" variant="secondary" disabled={isNavigating} onClick={onClose}>
        Stay in workspace
      </Button>
    )
  ) : isFailed ? (
    onRetry ? (
      <Button type="button" disabled={isNavigating} onClick={onRetry}>
        <RefreshCcw data-icon="inline-start" />
        {isRetrying ? 'Starting fresh variant…' : 'Try again'}
      </Button>
    ) : null
  ) : isReplay ? (
    onRetry ? (
      <Button type="button" disabled={isNavigating} onClick={onRetry}>
        <RefreshCcw data-icon="inline-start" />
        {isRetrying ? 'Starting…' : 'Play again'}
      </Button>
    ) : null
  ) : run.status === 'completed' ? (
    <Button type="button" disabled={isNavigating} onClick={onBackToMap}>
      Continue
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
      level={{ label: 'Challenge gate', title: run.challenge.title }}
      badges={badges}
      headline={headline}
      message={message}
      stats={stats}
      actions={actions}
      headerActions={headerActions}
    />
  )
}
