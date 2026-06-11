import type { ComponentType } from 'react'
import { Crosshair, Flame, ShieldCheck, Sparkles, Star, Swords, TerminalSquare, Trophy } from 'lucide-react'

import { GitCoinIcon } from '@/features/wallet/components/GitCoinIcon'
import type { StatsSummary } from '@/features/stats/types'
import { useCountUp } from '@/features/stats/useCountUp'

type Highlight = {
  label: string
  value: number | null
  suffix?: string
  Icon: ComponentType<{ className?: string }>
  color: string
  note?: string
}

function StatTile({ item, index }: { item: Highlight; index: number }) {
  const hasData = item.value !== null
  const counted = useCountUp(item.value)
  const display = item.suffix === '%' ? counted.toFixed(0) : Math.round(counted).toString()

  return (
    <div
      className="stat-tile group animate-fade-in-up p-4"
      style={{ ['--tile-accent' as string]: item.color, animationDelay: `${index * 55}ms` }}
    >
      <div className="relative z-[1] flex items-start justify-between gap-2">
        <p className="font-mono text-[0.62rem] uppercase tracking-[0.12em] text-aurora-blue/80">{item.label}</p>
        <span
          className="game-chip size-8 transition-transform duration-200 group-hover:scale-110"
          style={{ borderColor: `${item.color}55` }}
        >
          <item.Icon className="size-4" />
        </span>
      </div>
      {hasData ? (
        <p
          className="relative z-[1] mt-2 text-[1.9rem] font-extrabold leading-none tracking-tight"
          style={{ color: item.color, textShadow: `0 0 22px ${item.color}66` }}
        >
          {display}
          {item.suffix && <span className="text-lg">{item.suffix}</span>}
        </p>
      ) : (
        <p className="relative z-[1] mt-2 font-mono text-sm leading-none text-muted-foreground/50">No data yet</p>
      )}
      {item.note && <p className="relative z-[1] mt-1.5 text-[0.68rem] leading-snug text-muted-foreground">{item.note}</p>}
    </div>
  )
}

export function StatHighlightCards({ summary }: { summary: StatsSummary }) {
  const h = summary.headline
  const coins = useCountUp(h.gitcoins)
  const items: Highlight[] = [
    { label: 'Quests Completed', value: h.quests_completed, Icon: Trophy, color: '#00F5D4' },
    { label: 'Finish Rate', value: h.finish_rate.value, suffix: '%', Icon: ShieldCheck, color: '#34D399' },
    { label: 'Accuracy', value: h.accuracy, suffix: '%', Icon: Crosshair, color: '#00B4D8' },
    { label: 'Commands Run', value: h.commands_run, Icon: TerminalSquare, color: '#7DD3FC' },
    { label: 'Perfect Clears', value: h.perfect_clears, Icon: Star, color: '#FBBF24' },
    { label: 'Day Streak', value: h.day_streak, Icon: Flame, color: '#FB923C' },
    {
      label: 'Boss Floors Cleared',
      value: h.boss_floors.value,
      Icon: Swords,
      color: '#A78BFA',
      note: 'Hard challenges beaten',
    },
    { label: 'Comebacks', value: h.comebacks.value, Icon: Sparkles, color: '#F472B6', note: 'Retries turned into wins' },
  ]

  return (
    <section className="grid grid-cols-4 gap-3 max-2xl:grid-cols-3 max-md:grid-cols-2">
      {items.map((item, index) => (
        <StatTile key={item.label} item={item} index={index} />
      ))}

      {/* GitCoins — the prize tile, slightly richer treatment */}
      <div
        className="stat-tile animate-fade-in-up flex items-center gap-3 p-4"
        style={{ ['--tile-accent' as string]: '#00F5D4', animationDelay: '440ms' }}
      >
        <span className="game-chip size-11 shrink-0">
          <GitCoinIcon className="size-7" />
        </span>
        <div className="relative z-[1]">
          <p className="font-mono text-[0.62rem] uppercase tracking-[0.12em] text-aurora-blue/80">GitCoins</p>
          <p
            className="text-[1.6rem] font-extrabold leading-none tracking-tight text-aurora-cyan"
            style={{ textShadow: '0 0 22px rgba(0,245,212,0.5)' }}
          >
            {Math.round(coins)}
          </p>
        </div>
      </div>
    </section>
  )
}
