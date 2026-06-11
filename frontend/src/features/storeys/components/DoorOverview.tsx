import { type CSSProperties } from 'react'
import { Crosshair, Lock, Swords, Target, Trophy } from 'lucide-react'

import { ProgressBar } from '@/shared/components/ProgressBar'
import {
  accuracyLabel,
  challengeQuestAccent,
  difficultyLabel,
  questProgress,
} from '@/features/storeys/challengeUi'
import { useTowerSelection } from '@/features/storeys/hooks/useTowerSelection'

const ADVENTURE_ACCENT = '0, 245, 212'

function Stat({ icon: Icon, label, value }: { icon: typeof Target; label: string; value: string }) {
  return (
    <div className="door-overview-stat">
      <Icon className="size-3.5" />
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

// Shows the details of the door selected within THIS storey. Lives in the sticky
// storey rail (next to the storey overview); the action itself is the lower-left
// dock. Renders nothing unless the active selection belongs to this storey.
export function DoorOverview({ storeyId }: { storeyId: number }) {
  const selected = useTowerSelection((state) => state.selected)

  if (!selected || selected.storeyId !== storeyId) {
    return (
      <div className="door-overview is-empty" aria-hidden="true">
        <p className="door-overview-hint">Pick a door to preview this stage.</p>
      </div>
    )
  }

  if (selected.kind === 'adventure') {
    const { adventure } = selected
    const { progress } = adventure
    return (
      <section
        className="door-overview"
        aria-label="Selected stage"
        style={{ '--door-overview-accent': ADVENTURE_ACCENT } as CSSProperties}
      >
        <span className="door-overview-kind">
          <Swords className="size-3.5" />
          Command Adventure
        </span>
        <h3 className="door-overview-title">{adventure.title}</h3>
        <div className="door-overview-progress-meta">
          <span>{progress.numerator}/{progress.denominator} solved</span>
          <strong>{progress.value}%</strong>
        </div>
        <ProgressBar value={progress.value} className="h-2.5 bg-secondary/60" glow fillAnimate />
      </section>
    )
  }

  const { challenge, challengeIndex, quest, locked } = selected
  const accent = challengeQuestAccent(quest)
  return (
    <section
      className="door-overview"
      aria-label="Selected stage"
      style={{ '--door-overview-accent': accent } as CSSProperties}
    >
      <span className="door-overview-kind is-challenge">
        <Trophy className="size-3.5" />
        GIT Challenged · Trial {challengeIndex + 1}
      </span>
      <h3 className="door-overview-title">{challenge.title}</h3>
      <span className="door-overview-difficulty">{difficultyLabel(quest)}</span>

      {locked ? (
        <p className="door-overview-locked">
          <Lock className="size-3.5" />
          Clear the Command Adventure to unlock.
        </p>
      ) : null}

      <div className="door-overview-stats">
        <Stat icon={Target} label="Accuracy" value={accuracyLabel(quest)} />
        <Stat
          icon={Crosshair}
          label="Cleared"
          value={`${quest.successful_attempts.count}/${quest.successful_attempts.required}`}
        />
      </div>
      <div className="door-overview-progress-meta">
        <span>{difficultyLabel(quest)} progress</span>
        <strong>{questProgress(quest)}%</strong>
      </div>
      <ProgressBar
        value={questProgress(quest)}
        className="h-2.5 bg-secondary/55"
        fillFrom={`rgb(${accent})`}
        fillTo="rgb(234, 255, 252)"
        glow
      />
    </section>
  )
}
