import { HeroBand } from '@/features/dashboard/components/HeroBand'
import { KpiStrip } from '@/features/dashboard/components/KpiStrip'
import { RecentRuns } from '@/features/dashboard/components/RecentRuns'
import { StoreyProgress } from '@/features/dashboard/components/StoreyProgress'
import { StreakPanel } from '@/features/dashboard/components/StreakPanel'
import type { DashboardSummary } from '@/features/dashboard/types'

/**
 * Pure player-hub composition: hero identity band, KPI strip, then match
 * history flanked by streak + tower record. Data arrives via props so the
 * same view powers both the live page and the dev design previews.
 */
export function DashboardView({
  data,
  playerName,
  gitcoins,
}: {
  data: DashboardSummary
  playerName: string
  gitcoins: number | null
}) {
  return (
    <div className="flex flex-col gap-4">
      {/* Animated background — slow-drifting aurora orbs, dashboard-only */}
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div
          className="absolute"
          style={{
            width: '55%', height: '60%', left: '-8%', top: '15%',
            background: 'radial-gradient(ellipse at center, rgba(0,245,212,0.045) 0%, transparent 70%)',
            filter: 'blur(50px)',
            animation: 'bg-drift 18s ease-in-out infinite alternate',
          }}
        />
        <div
          className="absolute"
          style={{
            width: '45%', height: '50%', right: '-5%', bottom: '10%',
            background: 'radial-gradient(ellipse at center, rgba(0,180,216,0.035) 0%, transparent 70%)',
            filter: 'blur(50px)',
            animation: 'bg-drift 24s ease-in-out infinite alternate-reverse',
          }}
        />
      </div>

      <div className="animate-fade-in-up">
        <HeroBand summary={data} playerName={playerName} gitcoins={gitcoins} />
      </div>

      <div className="animate-fade-in-up" style={{ animationDelay: '90ms' }}>
        <KpiStrip summary={data} />
      </div>

      <div
        className="animate-fade-in-up grid grid-cols-[minmax(0,1fr)_24rem] items-start gap-4 max-xl:grid-cols-1"
        style={{ animationDelay: '170ms' }}
      >
        <RecentRuns summary={data} />
        <div className="flex flex-col gap-4">
          <StreakPanel summary={data} />
          <StoreyProgress summary={data} />
        </div>
      </div>
    </div>
  )
}
