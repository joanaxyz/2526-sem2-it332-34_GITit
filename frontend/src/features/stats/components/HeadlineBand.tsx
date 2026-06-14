import { Activity, CheckCircle2, Trophy } from 'lucide-react'

import { RingGauge } from '@/features/stats/components/RingGauge'
import type { StatsSummary } from '@/features/stats/types'
import { useCountUp } from '@/features/stats/useCountUp'
import { GitCoinIcon } from '@/features/wallet/components/GitCoinIcon'

const CYAN = '#00F5D4'
const BLUE = '#00B4D8'

function RingStat({ label, value, color, sub }: { label: string; value: number | null; color: string; sub?: string }) {
  return (
    <div className="stats-readout-item">
      <RingGauge value={value} color={color} label={label} size={56} strokeWidth={5} />
      <div className="min-w-0">
        <p className="font-mono text-[0.6rem] font-semibold uppercase tracking-[0.16em] text-aurora-blue/80">
          {label}
        </p>
        {sub && <p className="mt-1 truncate font-mono text-[0.6rem] text-muted-foreground/70">{sub}</p>}
      </div>
    </div>
  )
}

/**
 * Headline readout for the stats tab's primary performance numbers -
 * a chamfered glass slat in the hero plaques' vocabulary; the only
 * glass element of the deck.
 */
export function HeadlineBand({ summary }: { summary: StatsSummary }) {
  const h = summary.headline
  const levels = useCountUp(h.levels_completed)
  const coins = useCountUp(h.gitcoins)

  return (
    <div className="chamfer-frame stats-glass-band stats-readout">
      <div className="chamfer-body grid grid-cols-[minmax(14rem,0.9fr)_minmax(20rem,1.35fr)_auto] items-center gap-6 p-5 max-xl:grid-cols-2 max-md:grid-cols-1">
        <div className="stats-readout-primary">
          <span className="game-chip size-11 shrink-0">
            <Trophy aria-hidden="true" className="size-5 text-aurora-cyan" />
          </span>
          <div>
            <p
              className="text-[2.45rem] font-extrabold leading-none tracking-tight text-aurora-cyan"
              style={{ textShadow: '0 0 28px rgba(0,245,212,0.45), 0 0 56px rgba(0,180,216,0.2)' }}
            >
              {Math.round(levels)}
            </p>
            <p className="mt-1 font-mono text-[0.6rem] font-semibold uppercase tracking-[0.18em] text-aurora-blue/80">
              Levels Completed
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 max-sm:grid-cols-1">
          <RingStat
            label="Finish Rate"
            value={h.finish_rate.value}
            color={CYAN}
            sub={
              h.finish_rate.value === null
                ? 'no sessions yet'
                : `${h.finish_rate.numerator}/${h.finish_rate.denominator} sessions`
            }
          />

          <RingStat
            label="Accuracy"
            value={h.accuracy}
            color={BLUE}
            sub={h.accuracy === null ? 'no commands yet' : 'commands accepted'}
          />
        </div>

        <div className="stats-readout-wallet">
          <GitCoinIcon className="size-9 drop-shadow-[0_0_8px_rgba(0,245,212,0.45)]" />
          <div>
            <p
              className="text-2xl font-extrabold leading-none tracking-tight text-aurora-cyan"
              style={{ textShadow: '0 0 18px rgba(0,245,212,0.42)' }}
            >
              {Math.round(coins).toLocaleString()}
            </p>
            <p className="mt-0.5 font-mono text-[0.6rem] font-semibold uppercase tracking-[0.16em] text-aurora-blue/80">
              GitCoins
            </p>
          </div>
        </div>

        <div className="stats-readout-footer col-span-full grid grid-cols-2 gap-3 max-md:grid-cols-1">
          <span>
            <CheckCircle2 className="size-3.5" aria-hidden="true" />
            {h.perfect_clears} no-retry clears
          </span>
          <span>
            <Activity className="size-3.5" aria-hidden="true" />
            {h.commands_run.toLocaleString()} commands logged
          </span>
        </div>
      </div>
    </div>
  )
}
