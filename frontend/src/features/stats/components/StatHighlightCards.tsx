import type { ComponentType } from 'react'
import { Crosshair, Flame, ShieldCheck, Sparkles, Star, Swords, TerminalSquare, Trophy } from 'lucide-react'

import { GitCoinIcon } from '@/features/wallet/components/GitCoinIcon'
import type { StatsSummary } from '@/features/stats/types'
import { useCountUp } from '@/features/stats/useCountUp'
import { Card, CardContent } from '@/shared/components/Card'

type Highlight = {
  label: string
  value: number | null
  suffix?: string
  Icon: ComponentType<{ className?: string }>
  color: string
  note?: string
}

function HighlightCard({ item, index }: { item: Highlight; index: number }) {
  const hasData = item.value !== null
  const counted = useCountUp(item.value)
  const display = item.suffix === '%' ? counted.toFixed(0) : Math.round(counted).toString()

  return (
    <Card
      className="stat-card-hover group shadow-none animate-fade-in-up"
      style={{ borderTop: `2px solid ${item.color}55`, animationDelay: `${index * 60}ms` }}
    >
      <CardContent className="p-4">
        <div className="mb-1.5 flex items-center gap-1.5">
          <item.Icon className="size-3.5 transition-colors group-hover:drop-shadow-[0_0_6px_currentColor]" />
          <p className="font-mono text-[0.62rem] uppercase tracking-[0.11em] text-aurora-blue/80">{item.label}</p>
        </div>
        {hasData ? (
          <p
            className="text-[1.85rem] font-extrabold leading-none tracking-tight"
            style={{ color: item.color, textShadow: `0 0 20px ${item.color}55` }}
          >
            {display}
            {item.suffix && <span className="text-lg">{item.suffix}</span>}
          </p>
        ) : (
          <p className="mt-1 font-mono text-sm leading-none text-muted-foreground/50">No data</p>
        )}
        {item.note && <p className="mt-1.5 text-[0.68rem] leading-snug text-muted-foreground">{item.note}</p>}
      </CardContent>
    </Card>
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
        <HighlightCard key={item.label} item={item} index={index} />
      ))}
      <Card className="stat-card-hover shadow-none animate-fade-in-up" style={{ borderTop: '2px solid rgba(0,245,212,0.45)', animationDelay: '480ms' }}>
        <CardContent className="flex items-center gap-3 p-4">
          <GitCoinIcon className="size-9" />
          <div>
            <p className="font-mono text-[0.62rem] uppercase tracking-[0.11em] text-aurora-blue/80">GitCoins</p>
            <p className="text-[1.6rem] font-extrabold leading-none tracking-tight text-aurora-cyan" style={{ textShadow: '0 0 20px rgba(0,245,212,0.4)' }}>
              {Math.round(coins)}
            </p>
          </div>
        </CardContent>
      </Card>
    </section>
  )
}
