import { type CSSProperties } from 'react'
import { BookOpen, Crosshair, Lock, Swords, Target, Trophy } from 'lucide-react'

import { ProgressBar } from '@/shared/components/ProgressBar'
import {
  accuracyLabel,
  challengeLevelAccent,
  chestRewards,
  difficultyLabel,
  levelProgress,
  nextReward,
} from '@/features/tower-map/challengeUi'
import { useTowerSelection } from '@/features/tower-map/hooks/useTowerSelection'
import type { LearningStorey } from '@/features/tower-map/types'

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

export function ArtifactOverview({ storeyId, storey }: { storeyId: number; storey?: LearningStorey | null }) {
  const selected = useTowerSelection((state) => state.selected)

  if (!selected || selected.storeyId !== storeyId) {
    if (storey) {
      const progress = storey.level_completion?.value ?? 0
      const rewards = chestRewards(storey)
      const reward = nextReward(rewards, progress)
      return (
        <section className="artifact-overview artifact-overview--storey" aria-label="Current storey">
          <span className="artifact-overview-kind">Storey {storey.number}</span>
          <h3 className="artifact-overview-title">{storey.title}</h3>
          {storey.description ? <p className="artifact-overview-summary">{storey.description}</p> : null}
          <div className="artifact-overview-progress-meta">
            <span>Progress</span>
            <strong>{Math.round(progress)}%</strong>
          </div>
          <ProgressBar value={progress} className="h-2.5 bg-secondary/60" glow fillAnimate />
          <div className="artifact-overview-storey-meta">
            <span>{storey.command_skill_count} commands</span>
            <span>{storey.challenge_count} trials</span>
            {reward ? <strong>{reward.coins} coins at {reward.threshold}%</strong> : null}
          </div>
        </section>
      )
    }
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
