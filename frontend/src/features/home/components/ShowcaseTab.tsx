import { Coins, Flame, Star, Swords } from 'lucide-react'

import { CharacterShowcase } from '@/features/home/components/CharacterShowcase'
import { RankEmblem } from '@/features/home/components/RankEmblem'
import { SpellbookPanel } from '@/features/skills/components/SpellbookPanel'
import { RANK_TIERS, deriveRank } from '@/features/home/rank'
import type { HomeSummary } from '@/features/home/types'
import { useCountUp } from '@/features/stats/useCountUp'
import { ProgressBar } from '@/shared/components/ProgressBar'

function StatChip({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: typeof Flame
  label: string
  value: string
  color: string
}) {
  return (
    <div className="flex items-center gap-2.5 border-b border-[rgba(125,211,252,0.08)] px-1 py-2.5">
      <Icon
        aria-hidden="true"
        className="size-4 shrink-0"
        style={{ color, filter: `drop-shadow(0 0 6px ${color}55)` }}
      />
      <div className="min-w-0">
        <p className="font-mono text-[0.56rem] font-semibold uppercase tracking-[0.14em] text-muted-foreground/85">
          {label}
        </p>
        <p className="truncate font-mono text-sm font-bold leading-tight" style={{ color }}>
          {value}
        </p>
      </div>
    </div>
  )
}

/**
 * Hero Showcase sub-tab: the agent on a glowing stage, flanked by the rank
 * crest + ladder on one side and rating progress + career chips on the
 * other. Pure player-identity eye candy.
 */
export function ShowcaseTab({
  home,
  playerName,
  gitcoins,
}: {
  home: HomeSummary
  playerName: string
  gitcoins: number | null
}) {
  const rank = deriveRank(home)
  const rating = useCountUp(rank.ratingInTier)
  const coins = useCountUp(gitcoins)
  const currentTierIndex = RANK_TIERS.findIndex((t) => t.name === rank.tier.name)

  return (
    <section className="animate-fade-in-up relative" aria-label="Hero showcase">
      <div className="pointer-events-none absolute -left-24 -top-24 h-80 w-80 rounded-full bg-aurora-cyan opacity-[0.05] blur-3xl" />
      <div
        className="pointer-events-none absolute -right-16 bottom-0 h-72 w-72 rounded-full opacity-[0.07] blur-3xl"
        style={{ background: 'radial-gradient(circle, #A78BFA, transparent 70%)' }}
      />
      <div className="hero-identity-grid" aria-hidden="true" />

      <div className="relative z-[1] grid grid-cols-[15rem_minmax(0,1fr)_19rem] items-center gap-8 px-6 py-7 max-xl:grid-cols-[minmax(0,1fr)_19rem] max-md:grid-cols-1 max-md:justify-items-center max-md:px-2 max-md:text-center">
        {/* Rank crest + tier ladder */}
        <div className="flex flex-col items-center gap-5 max-xl:order-2 max-xl:col-start-2 max-xl:row-span-2 max-xl:row-start-1 max-md:order-none max-md:col-auto max-md:row-auto">
          <RankEmblem tier={rank.tier} />
          <ol className="flex w-full flex-col gap-1.5" aria-label="Rank ladder">
            {[...RANK_TIERS].reverse().map((tier) => {
              const tierIndex = RANK_TIERS.indexOf(tier)
              const state =
                tierIndex === currentTierIndex ? 'current' : tierIndex < currentTierIndex ? 'cleared' : 'locked'
              return (
                <li
                  key={tier.name}
                  className="tier-rung"
                  data-state={state}
                  style={{ ['--tier-color' as string]: tier.color }}
                >
                  <span className="tier-diamond" aria-hidden="true" />
                  <span className="text-xs font-bold tracking-tight" style={{ color: state === 'locked' ? undefined : tier.color }}>
                    {tier.name}
                  </span>
                  <span className="ml-auto font-mono text-[0.58rem] text-muted-foreground/60">
                    {state === 'current' ? 'you' : `${tier.minScore}+`}
                  </span>
                </li>
              )
            })}
          </ol>
        </div>

        {/* The agent on stage */}
        <div className="flex flex-col items-center max-xl:order-1 max-xl:col-start-1 max-xl:row-start-1 max-md:order-none max-md:col-auto max-md:row-auto">
          <CharacterShowcase playerName={playerName} tier={rank.tier} scale={1.15} />
          <p
            className="mt-3 text-xs font-bold uppercase tracking-[0.18em]"
            style={{ color: rank.tier.color, textShadow: `0 0 14px ${rank.tier.color}55` }}
          >
            {rank.title}
          </p>
        </div>

        {/* Rating + career chips */}
        <div className="w-full max-xl:order-3 max-xl:col-start-1 max-xl:row-start-2 max-md:order-none max-md:col-auto max-md:row-auto">
          <p className="font-mono text-[0.62rem] font-semibold uppercase tracking-[0.26em] text-aurora-blue/80">
            Rank Rating
          </p>
          <div className="mt-2">
            <div className="mb-1.5 flex items-baseline justify-between font-mono text-[0.62rem] uppercase tracking-[0.14em]">
              <span className="text-foreground/85">
                <span style={{ color: rank.tier.color }}>{Math.round(rating)}</span>
                <span className="text-muted-foreground">/{rank.ratingForNext}</span>
              </span>
              <span className="text-aurora-blue/80">
                {rank.nextTier ? `→ ${rank.nextTier.name}` : 'Max tier'}
              </span>
            </div>
            <ProgressBar
              value={rank.progressPct}
              glow
              fillAnimate
              fillFrom={rank.tier.color}
              fillTo="#00B4D8"
              className="h-2.5"
            />
          </div>

          <div className="mt-5 grid grid-cols-2 gap-2 max-md:grid-cols-2">
            <StatChip icon={Swords} label="Levels Done" value={String(home.counts.completed)} color="#34D399" />
            <StatChip icon={Flame} label="Day Streak" value={`${home.streak.current} days`} color="#FB923C" />
            <StatChip icon={Star} label="First-Try Stars" value={String(home.first_attempt_stars)} color="#FBBF24" />
            <StatChip
              icon={Coins}
              label="GitCoins"
              value={gitcoins === null ? '—' : Math.round(coins).toLocaleString()}
              color="#c4b5fd"
            />
          </div>
        </div>
      </div>

      <SpellbookPanel />
    </section>
  )
}
