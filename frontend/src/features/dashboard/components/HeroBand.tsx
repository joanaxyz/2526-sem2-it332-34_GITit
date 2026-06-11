import { ArrowRight, Star } from 'lucide-react'
import { Link } from 'react-router-dom'

import { CharacterShowcase } from '@/features/dashboard/components/CharacterShowcase'
import { RankEmblem } from '@/features/dashboard/components/RankEmblem'
import { deriveRank } from '@/features/dashboard/rank'
import type { DashboardSummary } from '@/features/dashboard/types'
import { useCountUp } from '@/features/stats/useCountUp'
import { GitCoinIcon } from '@/features/wallet/components/GitCoinIcon'
import { Button } from '@/shared/components/Button'
import { GamePanel } from '@/shared/components/GamePanel'
import { ProgressBar } from '@/shared/components/ProgressBar'

function InlineStat({ value, label, color = '#00F5D4' }: { value: number; label: string; color?: string }) {
  const counted = useCountUp(value)
  return (
    <span className="inline-flex items-baseline gap-1.5">
      <span className="font-mono text-base font-bold leading-none" style={{ color }}>
        {Math.round(counted)}
      </span>
      <span className="text-[0.68rem] font-medium uppercase tracking-[0.1em] text-muted-foreground">{label}</span>
    </span>
  )
}

/**
 * Identity hero band — the player-profile centerpiece: rank emblem + ladder
 * progress on the left, animated character showcase on the right.
 */
export function HeroBand({
  summary,
  playerName,
  gitcoins,
}: {
  summary: DashboardSummary
  playerName: string
  gitcoins: number | null
}) {
  const rank = deriveRank(summary)
  const coins = useCountUp(gitcoins)
  const rating = useCountUp(rank.ratingInTier)

  return (
    <GamePanel className="p-0">
      {/* Atmosphere: aurora glows + HUD grid fading from the identity side */}
      <div className="pointer-events-none absolute -left-24 -top-24 h-80 w-80 rounded-full bg-aurora-cyan opacity-[0.05] blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 right-40 h-64 w-64 rounded-full bg-aurora-deep opacity-[0.06] blur-3xl" />
      <div
        className="pointer-events-none absolute -right-10 -top-10 h-72 w-72 rounded-full opacity-[0.07] blur-3xl"
        style={{ background: 'radial-gradient(circle, #A78BFA, transparent 70%)' }}
      />
      <div className="hero-identity-grid" aria-hidden="true" />

      <div className="relative z-[1] grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-x-8 gap-y-6 p-6 max-xl:grid-cols-[auto_minmax(0,1fr)] max-md:grid-cols-1 max-md:justify-items-center max-md:text-center">
        <RankEmblem tier={rank.tier} />

        <div className="min-w-0 max-md:w-full">
          <p className="font-mono text-[0.62rem] font-semibold uppercase tracking-[0.26em] text-aurora-blue/80">
            Player Profile · Student Track
          </p>
          <h1
            className="mt-1 truncate text-4xl font-extrabold leading-tight tracking-tight"
            style={{ textShadow: '0 0 36px rgba(0,245,212,0.30), 0 0 72px rgba(0,180,216,0.16)' }}
          >
            {playerName}
          </h1>
          <p
            className="mt-1 text-sm font-bold uppercase tracking-[0.16em]"
            style={{ color: rank.tier.color, textShadow: `0 0 18px ${rank.tier.color}55` }}
          >
            {rank.title}
          </p>

          {/* Ranked ladder progress toward the next tier */}
          <div className="mt-4 max-w-md max-md:mx-auto">
            <div className="mb-1.5 flex items-baseline justify-between font-mono text-[0.62rem] uppercase tracking-[0.14em]">
              <span className="text-muted-foreground">Rank rating</span>
              <span className="text-foreground/85">
                <span style={{ color: rank.tier.color }}>{Math.round(rating)}</span>
                <span className="text-muted-foreground">/{rank.ratingForNext}</span>
                {rank.nextTier && <span className="ml-2 text-aurora-blue/80">→ {rank.nextTier.name}</span>}
                {!rank.nextTier && <span className="ml-2 text-aurora-blue/80">Max tier</span>}
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

          {/* Session stats + GitCoins */}
          <div
            className="mt-4 flex flex-wrap items-center gap-x-6 gap-y-2.5 border-t pt-3.5 max-md:justify-center"
            style={{ borderColor: 'rgba(255,255,255,0.07)' }}
          >
            <InlineStat value={summary.counts.started} label="Started" color="#7DD3FC" />
            <InlineStat value={summary.counts.completed} label="Completed" color="#34D399" />
            <InlineStat value={summary.streak.current} label="Day streak" color="#FB923C" />
            <span className="inline-flex items-baseline gap-1.5">
              <Star aria-hidden="true" className="size-3.5 translate-y-0.5 fill-[#FBBF24] text-[#FBBF24]" />
              <span className="font-mono text-base font-bold leading-none text-[#FBBF24]">
                {summary.first_attempt_stars}
              </span>
              <span className="text-[0.68rem] font-medium uppercase tracking-[0.1em] text-muted-foreground">
                First-try stars
              </span>
            </span>
            <span
              className="inline-flex items-center gap-1.5 rounded-full py-1 pl-1.5 pr-3"
              style={{
                border: '1px solid rgba(167,139,250,0.4)',
                background: 'linear-gradient(135deg, rgba(167,139,250,0.12), rgba(0,245,212,0.08))',
                boxShadow: '0 0 12px rgba(167,139,250,0.16)',
              }}
              title="GitCoins — earned from storey-progress chests"
            >
              <GitCoinIcon className="size-5" />
              <span className="font-mono text-sm font-bold leading-none text-[#c4b5fd]">
                {gitcoins === null ? '—' : Math.round(coins).toLocaleString()}
              </span>
            </span>
          </div>

          <div className="mt-4 max-md:flex max-md:justify-center">
            <Button asChild className="btn-pulse">
              <Link to="/tower">
                Open Tower
                <ArrowRight data-icon="inline-end" />
              </Link>
            </Button>
          </div>
        </div>

        <div className="max-xl:col-span-2 max-xl:justify-self-center max-md:col-span-1">
          <CharacterShowcase playerName={playerName} tier={rank.tier} />
        </div>
      </div>
    </GamePanel>
  )
}
