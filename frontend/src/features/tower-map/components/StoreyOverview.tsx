import { Layers3, ListChecks, Swords, type LucideIcon } from 'lucide-react'
import { motion } from 'motion/react'

import { StoreyBookCard } from '@/features/tower-map/book/StoreyBookCard'
import { chestRewards, nextReward } from '@/features/tower-map/challengeUi'
import type { LearningStorey } from '@/features/tower-map/types'
import { GitCoinIcon } from '@/features/wallet/components/GitCoinIcon'
import { ProgressBar } from '@/shared/components/ProgressBar'

const STOREY_EASE = [0.16, 1, 0.3, 1] as const

function OverviewStat({ icon: Icon, label, value }: { icon: LucideIcon; label: string; value: string | number }) {
  return (
    <div className="tower-overview-stat">
      <span className="tower-overview-stat-icon">
        <Icon className="size-4" />
      </span>
      <span className="text-sm text-muted-foreground">{label}</span>
      <strong className="ml-auto text-sm text-foreground">{value}</strong>
    </div>
  )
}

// Rich storey overview that lives in the top-left dock: storey stats, the chest
// reward rail, the next-reward payout, and the field-guide book. Always visible
// for the active storey, independent of any artifact selection (which the
// bottom dock's ArtifactOverview handles). Coins stand in for the old chest art
// the seed media drop removed.
export function StoreyOverview({ storey }: { storey: LearningStorey }) {
  const title = storey.title
  const progress = storey.level_completion?.value ?? 0
  const rewards = chestRewards(storey)
  const reward = nextReward(rewards, progress)
  const levels = storey.challenge_count * 3

  return (
    <motion.aside
      className="storey-overview"
      initial={{ opacity: 0, x: -16 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ amount: 0.28, once: true, margin: '-4% 0px -4% 0px' }}
      transition={{ duration: 0.48, ease: STOREY_EASE }}
    >
      <div className="storey-overview-heading">
        <span className="storey-overview-kicker">Storey {storey.number}</span>
        <div className="tower-heading-row">
          <h2 className="storey-overview-title">{title}</h2>
        </div>
        <p className="mt-4 max-w-xs text-base leading-7 text-muted-foreground">
          Storey overview for this Command Adventure and Challenges set.
        </p>
      </div>

      <section className="tower-side-panel storey-overview-card" aria-label={`${title} storey overview`}>
        <div className="grid gap-4">
          <OverviewStat icon={ListChecks} label="Command skills" value={storey.command_skill_count} />
          <OverviewStat icon={Swords} label="Challenges" value={storey.challenge_count} />
          <OverviewStat icon={Layers3} label="Total levels" value={levels} />
        </div>
        <div className="tower-progress-block">
          <div className="flex items-center justify-between gap-3">
            <span className="text-sm text-muted-foreground">Storey Progress</span>
            <strong className="font-mono text-sm text-foreground">{Math.round(progress)}%</strong>
          </div>
          <div className="tower-reward-rail">
            <ProgressBar value={progress} className="h-3 bg-secondary/70" glow fillAnimate />
            <div className="tower-reward-markers" aria-hidden="true">
              {rewards.map((chest) => (
                <span
                  className={chest.threshold <= progress ? 'is-earned' : undefined}
                  key={chest.threshold}
                  style={{ left: `${chest.threshold}%` }}
                >
                  <GitCoinIcon className="size-5" />
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="stage-reward-panel" aria-label={`${title} progress reward`}>
        <div>
          <p className="text-sm text-muted-foreground">Progress Reward</p>
          <p className="mt-2 text-sm font-semibold text-foreground">Next chest at {reward.threshold}% storey progress</p>
          <p
            className="mt-3 inline-flex items-center gap-2 text-2xl font-black"
            style={{
              color: '#00F5D4',
              textShadow: '0 0 16px rgba(0, 245, 212, 0.45)',
            }}
          >
            +{reward.coins} coins
            <GitCoinIcon className="size-6 drop-shadow-[0_0_6px_rgba(0,245,212,0.4)]" />
          </p>
        </div>
        <span className="stage-reward-icon">
          <GitCoinIcon className="stage-reward-chest" />
        </span>
      </section>

      <StoreyBookCard storeyId={storey.id} storeyTitle={title} commandCount={storey.command_skill_count} />
    </motion.aside>
  )
}
