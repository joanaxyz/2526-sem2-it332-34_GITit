import { Trophy } from 'lucide-react'

import { RingGauge } from '@/features/stats/components/RingGauge'
import type { StatsSummary } from '@/features/stats/types'
import { useCountUp } from '@/features/stats/useCountUp'
import { GitCoinIcon } from '@/features/wallet/components/GitCoinIcon'
import { GamePanel } from '@/shared/components/GamePanel'

function RingStat({ label, value, color, sub }: { label: string; value: number | null; color: string; sub?: string }) {
  return (
    <div className="flex items-center gap-3">
      <RingGauge value={value} color={color} label={label} size={64} strokeWidth={5.5} />
      <div>
        <p className="font-mono text-[0.62rem] font-semibold uppercase tracking-[0.16em] text-aurora-blue/80">
          {label}
        </p>
        {sub && <p className="mt-1 font-mono text-[0.62rem] text-muted-foreground/70">{sub}</p>}
      </div>
    </div>
  )
}

/**
 * Headline band: the four marquee numbers — quests completed, finish-rate
 * ring, accuracy ring, and the GitCoin purse — in one dense HUD strip.
 */
export function HeadlineBand({ summary }: { summary: StatsSummary }) {
  const h = summary.headline
  const quests = useCountUp(h.quests_completed)
  const coins = useCountUp(h.gitcoins)

  return (
    <GamePanel className="p-0">
      <div className="pointer-events-none absolute -left-16 -top-20 h-64 w-64 rounded-full bg-aurora-cyan opacity-[0.05] blur-3xl" />
      <div
        className="pointer-events-none absolute -right-12 -bottom-16 h-56 w-56 rounded-full opacity-[0.07] blur-3xl"
        style={{ background: 'radial-gradient(circle, #A78BFA, transparent 70%)' }}
      />

      <div className="relative z-[1] flex flex-wrap items-center gap-x-10 gap-y-5 p-6 max-md:gap-x-6">
        {/* Quests completed — the headline number */}
        <div className="flex items-center gap-4">
          <span className="game-chip size-12 shrink-0">
            <Trophy aria-hidden="true" className="size-6 text-aurora-cyan" />
          </span>
          <div>
            <p
              className="text-[2.6rem] font-extrabold leading-none tracking-tight text-aurora-cyan"
              style={{ textShadow: '0 0 28px rgba(0,245,212,0.45), 0 0 56px rgba(0,180,216,0.2)' }}
            >
              {Math.round(quests)}
            </p>
            <p className="mt-1 font-mono text-[0.62rem] font-semibold uppercase tracking-[0.16em] text-aurora-blue/80">
              Quests Completed
            </p>
          </div>
        </div>

        <span aria-hidden="true" className="h-12 w-px bg-white/[0.07] max-md:hidden" />

        <RingStat
          label="Finish Rate"
          value={h.finish_rate.value}
          color="#34D399"
          sub={
            h.finish_rate.value === null
              ? 'no sessions yet'
              : `${h.finish_rate.numerator}/${h.finish_rate.denominator} sessions`
          }
        />

        <RingStat
          label="Accuracy"
          value={h.accuracy}
          color="#00B4D8"
          sub={h.accuracy === null ? 'no commands yet' : 'commands accepted'}
        />

        {/* GitCoins — the purse, purple+cyan minted treatment */}
        <div
          className="ml-auto flex items-center gap-3 rounded-xl py-2.5 pl-3 pr-5 max-md:ml-0"
          style={{
            border: '1px solid rgba(167,139,250,0.38)',
            background: 'linear-gradient(135deg, rgba(167,139,250,0.13), rgba(0,245,212,0.07))',
            boxShadow: '0 0 18px rgba(167,139,250,0.14), inset 0 1px 0 rgba(167,139,250,0.2)',
          }}
        >
          <GitCoinIcon className="size-9 drop-shadow-[0_0_8px_rgba(0,245,212,0.45)]" />
          <div>
            <p
              className="text-2xl font-extrabold leading-none tracking-tight text-[#c4b5fd]"
              style={{ textShadow: '0 0 18px rgba(167,139,250,0.5)' }}
            >
              {Math.round(coins).toLocaleString()}
            </p>
            <p className="mt-0.5 font-mono text-[0.6rem] font-semibold uppercase tracking-[0.16em] text-aurora-blue/80">
              GitCoins
            </p>
          </div>
        </div>
      </div>
    </GamePanel>
  )
}
