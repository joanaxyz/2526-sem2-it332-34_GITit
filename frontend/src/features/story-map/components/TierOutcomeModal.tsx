import { CommandComparison } from '@/shared/level/components/CommandComparison'
import { Gem, Map, RefreshCcw, Repeat2, RotateCcw, ScanSearch, Sparkles, SquareTerminal, TriangleAlert, WandSparkles, XCircle } from 'lucide-react'
import { useEffect } from 'react'
import type { CSSProperties } from 'react'

import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { GameOutcomeModal } from '@/shared/level/components/game-outcome/GameOutcomeModal'
import { Badge } from '@/shared/components/Badge'
import { playGameOverSound, playVictorySound } from '@/shared/audio/battleAudio'
import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'
import { difficultyLabel, tierOutcomeState } from '@/features/story-map/components/tierOutcome'
import { StarScoreChecklist } from '@/shared/level/components/StarScoreChecklist'

/** Mirrors ChallengeOutcomeModal. Tiers have no sibling-level navigator - a
 * tier's only lateral move is next_difficulty (easy -> medium -> hard), which
 * tierOutcomeNextStep offers once the modal is dismissed. */
export function TierOutcomeModal({
  open,
  run,
  onClose,
  onBackToMap,
  onRetry,
  onContinue,
}: {
  open: boolean
  run: TierRun
  onClose: () => void
  onBackToMap: () => void
  onContinue?: () => void
  onRetry?: () => void
}) {
  const { isFailed, isReplay, isTransfer, canAdvance, isPartialClear } = tierOutcomeState(run)
  // A cleared scenario that is not the tier's last names itself and the next scenario.
  const nextScenario = run.progress.next_scenario

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
          ? 'Scenario cleared'
          : 'Level cleared'

  const hitActionLimit = isFailed && run.counts.max_reached
  const message = isTransfer
    ? 'Your first transfer result is recorded. You can continue free practice; later runs cannot change this checkpoint result.'
    : isReplay
    ? isFailed
      ? "This free-play run ended before reaching the target state. It doesn't affect your saved progress. Play again whenever you like."
      : 'Replays can improve your saved star score. Lower scores never replace your best, and rewards are paid only once.'
    : isFailed
      ? hitActionLimit
        ? run.failure_reason ??
          'You used every counted action allowed for this attempt without reaching the target repository state. Start a fresh variant and try again.'
        : 'This attempt ended before the repository reached the target state. Start a fresh variant and try again.'
      : canAdvance
        ? 'Level cleared. The next difficulty is ready.'
        : isPartialClear && nextScenario
          ? `Next: ${nextScenario.title}`
          : 'Level cleared.'
  const Icon = isFailed ? XCircle : Sparkles
  const targetActionsMet =
    !isTransfer && !isFailed &&
    run.counts.counted_action_total > 0 &&
    run.counts.counted_action_total <= run.counts.minimum_counted_commands

  // Hitting the target lights the stat gold, matching the star and wordmark art.
  const actionsAccent = targetActionsMet ? 'hsl(var(--warning))' : 'hsl(var(--primary))'

  const stats = [
    {
      label: 'Actions',
      numerator: run.counts.counted_action_total,
      denominator: isTransfer ? run.counts.maximum_counted_commands : run.counts.minimum_counted_commands,
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
      label: 'Submissions',
      numerator: run.counts.total_attempts,
      helper: 'All commands submitted, including free checks',
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
        {isTransfer
          ? 'Transfer checkpoint'
          : isPartialClear && nextScenario
            ? `${difficultyLabel(run)} scenario ${run.scenario.index ?? nextScenario.index - 1} of ${run.scenario.total}`
            : `${difficultyLabel(run)} ${isFailed ? 'failed' : 'complete'}`}
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

  return (
    <GameOutcomeModal
      open={open}
      onClose={onClose}
      title={isTransfer ? 'Transfer result recorded' : isFailed ? 'Level failed' : isPartialClear ? 'Scenario complete' : 'Level complete'}
      tone={isFailed ? 'failure' : 'success'}
      icon={Icon}
      resultLabel={isFailed ? 'Game Over' : 'You Won'}
      stars={isTransfer ? undefined : run.stars}
      showStars={!isTransfer}
      level={{ label: `Level ${run.tier.adventure_level_number}`, title: run.tier.adventure_level_title }}
      badges={badges}
      headline={headline}
      message={!isFailed && !isReplay && !isTransfer && nextScenario && onContinue ? <button type="button" className="outcome-next-button" onClick={(event) => { event.stopPropagation(); onContinue() }}>Next: {nextScenario.title}</button> : message}
      stats={stats}
      headerActions={headerActions}
    >
      {!isTransfer && !isFailed ? <CommandComparison comparison={run.command_comparison} /> : null}
      {!isTransfer && run.star_breakdown ? (
        <StarScoreChecklist variant="result" breakdown={run.star_breakdown} tier multiScenario={run.scenario.total > 1} savedStars={run.completion?.stars} />
      ) : null}
    </GameOutcomeModal>
  )
}
