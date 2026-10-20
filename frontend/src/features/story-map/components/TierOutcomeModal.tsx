import { Gem, Map, RefreshCcw, RotateCcw, Sparkles, WandSparkles, XCircle } from 'lucide-react'
import { useEffect } from 'react'
import type { CSSProperties } from 'react'

import bugIconImage from '@/assets/images/battle-outcome/bug.png'
import skullIconImage from '@/assets/images/battle-outcome/skull.png'
import terminalIconImage from '@/assets/images/battle-outcome/terminal.png'
import warnIconImage from '@/assets/images/battle-outcome/warn.png'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { GameOutcomeModal } from '@/shared/level/components/game-outcome/GameOutcomeModal'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'
import { playGameOverSound, playVictorySound } from '@/shared/audio/battleAudio'
import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'

function difficultyLabel(run: TierRun) {
  if (!run.difficulty) return 'Adventure'
  return run.difficulty.charAt(0).toUpperCase() + run.difficulty.slice(1)
}

/** Mirrors ChallengeOutcomeModal. Tiers have no sibling-level navigator - a
 * tier's only lateral move is next_difficulty (easy -> medium -> hard),
 * already surfaced via the "Next" action below. */
export function TierOutcomeModal({
  open,
  run,
  onClose,
  onBackToMap,
  onNextLevel,
  onRetry,
  onContinue,
  nextDifficultyLabel,
}: {
  open: boolean
  run: TierRun
  onClose: () => void
  onBackToMap: () => void
  onNextLevel?: () => void
  onRetry?: () => void
  /** Starts a fresh run on the same tier after a partial clear (progress not
   * yet at required_successful_attempts) - passes prior_run_id so
   * TierVariantSelectionService rotates to a different variant. */
  onContinue?: () => void
  nextDifficultyLabel?: string | null
}) {
  const isFailed = run.status === 'failed'
  const isReplay = run.replay
  const isTransfer = Boolean(run.transfer)
  const canAdvance = !isTransfer && !isReplay && run.status === 'completed' && Boolean(run.next_difficulty)
  const isPartialClear = !isTransfer && !isReplay && run.status === 'completed' && !canAdvance && !run.progress.cleared
  // A tier with several authored waves names the wave just cleared and the next one;
  // a single wave that needs several clears keeps the clear count.
  const nextWave = run.wave.total > 1 ? run.progress.next_wave : null
  const rewardHint =
    run.reward.coins > 0 && !run.reward.claimed ? ` Clear it to earn ${run.reward.coins} GitCoins.` : ''

  useEffect(() => {
    if (!open) return
    if (isFailed) {
      playGameOverSound()
    } else {
      playVictorySound()
    }
  }, [isFailed, open])

  const headline = isTransfer
    ? isFailed ? 'Transfer checkpoint not cleared' : 'Transfer checkpoint cleared'
    : isReplay
    ? isFailed
      ? 'Replay ended'
      : 'Replay complete'
    : isFailed
      ? 'Attempt limit reached'
      : canAdvance
        ? 'Level ready'
        : isPartialClear
          ? nextWave
            ? 'Wave cleared'
            : 'Scenario cleared'
          : 'Level cleared'

  const hitActionLimit = isFailed && run.counts.max_reached
  const message = isTransfer
    ? 'Your first transfer result is recorded. You can continue free practice; later runs cannot change this checkpoint result.'
    : isReplay
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
        : isPartialClear
          ? nextWave
            ? `Wave ${run.wave.index ?? nextWave.index - 1} of ${run.wave.total} cleared — next: ${nextWave.title}.${rewardHint}`
            : `Nice work. ${run.progress.completed} of ${run.progress.total} clears done for this difficulty - continue with a new scenario to finish it.`
          : 'Level cleared.'
  const Icon = isFailed ? XCircle : Sparkles
  const targetActionsMet =
    !isTransfer && !isFailed &&
    run.counts.counted_action_total > 0 &&
    run.counts.counted_action_total <= run.counts.minimum_counted_commands

  // Bar fills as actions approach the target; green when at/under target, amber otherwise.
  const actionsAccent = targetActionsMet ? 'hsl(142 70% 55%)' : '#f59e0b'

  const stats = [
    {
      label: 'Actions',
      numerator: run.counts.counted_action_total,
      denominator: isTransfer ? run.counts.maximum_counted_commands : run.counts.minimum_counted_commands,
      helper: `Max allowed: ${run.counts.maximum_counted_commands}`,
      iconSrc: terminalIconImage,
      accentColor: actionsAccent,
      targetMet: targetActionsMet,
    },
    {
      label: 'Diagnostics',
      numerator: run.counts.non_counted_diagnostic_total,
      helper: 'Free inspections used',
      iconSrc: bugIconImage,
      accentColor: 'hsl(var(--primary))',
    },
    {
      label: 'Attempts',
      numerator: run.counts.total_attempts,
      helper: isReplay ? 'Free-play attempt' : 'Saved attempt count',
      iconSrc: skullIconImage,
      accentColor: 'hsl(var(--primary))',
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
        {isTransfer ? 'Transfer checkpoint' : `${difficultyLabel(run)} ${isFailed ? 'failed' : 'complete'}`}
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
      {!isFailed && !isReplay && run.rewards?.coins_awarded ? (
        <Badge variant="secondary" className="game-outcome-badge">
          <GitCoinIcon className="size-3.5" />
          +{run.rewards.coins_awarded} GitCoins
        </Badge>
      ) : null}
      {!isFailed && !isReplay && run.rewards?.mastery_advanced.length ? (
        <Badge variant="secondary" className="game-outcome-badge">
          <WandSparkles className="size-3.5" />
          {run.rewards.mastery_advanced.length} skill {run.rewards.mastery_advanced.length === 1 ? 'advanced' : 'advances'}
        </Badge>
      ) : null}
      {!isFailed && !isReplay && run.rewards?.chapter_chests_awarded.length ? (
        <Badge variant="secondary" className="game-outcome-badge">
          <Gem className="size-3.5" />
          {run.rewards.chapter_chests_awarded.length} progress {run.rewards.chapter_chests_awarded.length === 1 ? 'chest' : 'chests'}
        </Badge>
      ) : null}
    </>
  )

  const headerActions = (
    <>
      {onRetry && !isTransfer ? (
        <button
          type="button"
          className="game-outcome-header-btn"
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
        onClick={onBackToMap}
        aria-label="Back to Map"
        title="Back to Map"
      >
        <Map className="size-3.5" />
      </button>
    </>
  )

  const actions = isTransfer ? (
    <Button type="button" onClick={onRetry ?? onBackToMap}>Continue free practice</Button>
  ) : canAdvance ? (
    onNextLevel && nextDifficultyLabel ? (
      <Button type="button" onClick={onNextLevel}>
        Continue
      </Button>
    ) : (
      <Button type="button" variant="secondary" onClick={onClose}>
        Stay in workspace
      </Button>
    )
  ) : isPartialClear ? (
    onContinue ? (
      <Button type="button" onClick={onContinue}>
        Continue
      </Button>
    ) : null
  ) : isFailed ? (
    onRetry ? (
      <Button type="button" onClick={onRetry}>
        <RefreshCcw data-icon="inline-start" />
        Try again
      </Button>
    ) : null
  ) : isReplay ? (
    onRetry ? (
      <Button type="button" onClick={onRetry}>
        <RefreshCcw data-icon="inline-start" />
        Play again
      </Button>
    ) : null
  ) : run.status === 'completed' ? null : null

  return (
    <GameOutcomeModal
      open={open}
      onClose={onClose}
      title={isTransfer ? 'Transfer result recorded' : isFailed ? 'Level failed' : 'Level complete'}
      tone={isFailed ? 'failure' : 'success'}
      icon={Icon}
      resultLabel={isFailed ? 'Game Over' : 'You Won'}
      stars={isTransfer ? undefined : run.stars}
      showStars={!isTransfer}
      badges={badges}
      headline={headline}
      message={message}
      stats={stats}
      actions={actions}
      headerActions={headerActions}
    />
  )
}
