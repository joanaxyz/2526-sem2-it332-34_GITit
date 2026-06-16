import { type CSSProperties } from 'react'
import { BookOpen, Crosshair, Lock, Swords, Target, Trophy } from 'lucide-react'

import { ProgressBar } from '@/shared/components/ProgressBar'
import {
  accuracyLabel,
  challengeLevelAccent,
  difficultyLabel,
  levelProgress,
} from '@/features/tower-map/challengeUi'
import { useTowerSelection } from '@/features/tower-map/hooks/useTowerSelection'

const ADVENTURE_ACCENT = '0, 245, 212'

function Stat({ icon: Icon, label, value }: { icon: typeof Target; label: string; value: string }) {
  return (
    <div className="artifact-overview-stat">
      <Icon className="size-3.5" />
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

export function ArtifactOverview({ storeyId }: { storeyId: number }) {
  const selected = useTowerSelection((state) => state.selected)

  if (!selected || selected.storeyId !== storeyId) {
    return (
      <div className="artifact-overview is-empty" aria-hidden="true">
        <p className="artifact-overview-hint">Pick an artifact to preview this stage.</p>
      </div>
    )
  }

  if (selected.kind === 'adventure') {
    const { adventure } = selected
    const { progress } = adventure
    return (
      <section
        className="artifact-overview"
        aria-label="Selected artifact"
        style={{ '--artifact-overview-accent': ADVENTURE_ACCENT } as CSSProperties}
      >
        <span className="artifact-overview-kind">
          <Swords className="size-3.5" />
          Command Adventure
        </span>
        <h3 className="artifact-overview-title">{adventure.title}</h3>
        <div className="artifact-overview-progress-meta">
          <span>{progress.numerator}/{progress.denominator} solved</span>
          <strong>{progress.value}%</strong>
        </div>
        <ProgressBar value={progress.value} className="h-2.5 bg-secondary/60" glow fillAnimate />
      </section>
    )
  }

  if (selected.kind === 'tome') {
    const { tome } = selected
    return (
      <section
        className="artifact-overview"
        aria-label="Selected artifact"
        style={{ '--artifact-overview-accent': ADVENTURE_ACCENT } as CSSProperties}
      >
        <span className="artifact-overview-kind">
          <BookOpen className="size-3.5" />
          Tome
        </span>
        <h3 className="artifact-overview-title">{tome.title}</h3>
        {tome.summary ? <p className="artifact-overview-summary">{tome.summary}</p> : null}
      </section>
    )
  }

  const { challenge, challengeIndex, level, locked } = selected
  const accent = challengeLevelAccent(level)
  return (
    <section
      className="artifact-overview"
      aria-label="Selected artifact"
      style={{ '--artifact-overview-accent': accent } as CSSProperties}
    >
      <span className="artifact-overview-kind is-challenge">
        <Trophy className="size-3.5" />
        Challenges - Trial {challengeIndex + 1}
      </span>
      <h3 className="artifact-overview-title">{challenge.title}</h3>
      <span className="artifact-overview-difficulty">{difficultyLabel(level)}</span>

      {locked ? (
        <p className="artifact-overview-locked">
          <Lock className="size-3.5" />
          Clear the Command Adventure to unlock.
        </p>
      ) : null}

      <div className="artifact-overview-stats">
        <Stat icon={Target} label="Accuracy" value={accuracyLabel(level)} />
        <Stat
          icon={Crosshair}
          label="Cleared"
          value={`${level.successful_attempts.count}/${level.successful_attempts.required}`}
        />
      </div>
      <div className="artifact-overview-progress-meta">
        <span>{difficultyLabel(level)} progress</span>
        <strong>{levelProgress(level)}%</strong>
      </div>
      <ProgressBar
        value={levelProgress(level)}
        className="h-2.5 bg-secondary/55"
        fillFrom={`rgb(${accent})`}
        fillTo="rgb(234, 255, 252)"
        glow
      />
    </section>
  )
}
