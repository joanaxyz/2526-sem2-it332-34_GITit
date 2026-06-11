import { Lock, Star } from 'lucide-react'

import type { Achievement } from '@/features/home/achievements'

function AchievementTile({ achievement, index }: { achievement: Achievement; index: number }) {
  const a = achievement
  const pct = Math.min(100, Math.round((a.current / a.target) * 100))
  return (
    <div
      className="achv-tile animate-fade-in-up"
      data-locked={!a.unlocked}
      style={{ ['--achv-accent' as string]: a.color, animationDelay: `${index * 40}ms` }}
    >
      <div className="flex items-start gap-3">
        <span className="achv-icon" aria-hidden="true">
          <a.Icon className="size-5" />
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm font-bold leading-tight tracking-tight">{a.title}</p>
            <span className="achv-points shrink-0">
              <Star aria-hidden="true" className="size-2.5 fill-current" />
              {a.points}
            </span>
          </div>
          <p className="mt-0.5 text-xs leading-snug text-muted-foreground">{a.desc}</p>
        </div>
      </div>

      <div className="mt-3">
        {a.unlocked ? (
          <p
            className="font-mono text-[0.6rem] font-bold uppercase tracking-[0.18em]"
            style={{ color: a.color, textShadow: `0 0 10px ${a.color}66` }}
          >
            ✓ Unlocked
          </p>
        ) : (
          <div>
            <div className="mb-1 flex items-center justify-between font-mono text-[0.58rem] uppercase tracking-[0.1em] text-muted-foreground/60">
              <span className="inline-flex items-center gap-1">
                <Lock aria-hidden="true" className="size-2.5" />
                Locked
              </span>
              <span>
                {a.current.toLocaleString()}/{a.target.toLocaleString()}
              </span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
              <div
                className="h-full rounded-full"
                style={{
                  width: `${pct}%`,
                  background: `linear-gradient(90deg, ${a.color}66, ${a.color})`,
                  boxShadow: pct > 0 ? `0 0 6px ${a.color}55` : 'none',
                  transition: 'width 1s cubic-bezier(0.16, 1, 0.3, 1)',
                }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Achievements sub-tab: gamerscore-style ledger header plus the full badge
 * grid — unlocked tiles glow in their accent color, locked ones show a
 * progress bar toward the unlock condition.
 */
export function AchievementsTab({ achievements }: { achievements: Achievement[] }) {
  const unlocked = achievements.filter((a) => a.unlocked)
  const earnedPoints = unlocked.reduce((sum, a) => sum + a.points, 0)
  const totalPoints = achievements.reduce((sum, a) => sum + a.points, 0)
  const pct = totalPoints > 0 ? Math.round((earnedPoints / totalPoints) * 100) : 0

  return (
    <div className="flex flex-col gap-6">
      {/* Open gamerscore readout — no panel; a hairline shelves it off the grid */}
      <div className="animate-fade-in-up flex flex-wrap items-center gap-x-10 gap-y-4 border-b border-[rgba(125,211,252,0.08)] pb-5">
        <div>
          <p className="font-mono text-[0.6rem] font-semibold uppercase tracking-[0.2em] text-aurora-blue/80">
            Badges Earned
          </p>
          <p className="mt-1 text-3xl font-extrabold leading-none tracking-tight text-aurora-cyan" style={{ textShadow: '0 0 24px rgba(0,245,212,0.4)' }}>
            {unlocked.length}
            <span className="text-base font-bold text-muted-foreground">/{achievements.length}</span>
          </p>
        </div>
        <span aria-hidden="true" className="h-10 w-px bg-white/[0.07] max-md:hidden" />
        <div>
          <p className="font-mono text-[0.6rem] font-semibold uppercase tracking-[0.2em] text-aurora-blue/80">
            Star Score
          </p>
          <p className="mt-1 inline-flex items-baseline gap-1.5 text-3xl font-extrabold leading-none tracking-tight text-[#FBBF24]" style={{ textShadow: '0 0 24px rgba(251,191,36,0.4)' }}>
            <Star aria-hidden="true" className="size-5 translate-y-0.5 fill-current" />
            {earnedPoints}
            <span className="text-base font-bold text-muted-foreground">/{totalPoints}</span>
          </p>
        </div>
        <div className="min-w-48 flex-1">
          <div className="mb-1.5 flex justify-between font-mono text-[0.6rem] uppercase tracking-[0.14em] text-muted-foreground">
            <span>Collection</span>
            <span className="text-aurora-cyan">{pct}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-white/[0.06]">
            <div
              className="h-full rounded-full"
              style={{
                width: `${pct}%`,
                background: 'linear-gradient(90deg, #00F5D4, #00B4D8)',
                boxShadow: '0 0 10px rgba(0,245,212,0.5)',
                transition: 'width 1.1s cubic-bezier(0.16, 1, 0.3, 1)',
              }}
            />
          </div>
        </div>
      </div>

      <section
        aria-label="Achievements"
        className="grid grid-cols-3 gap-3 max-xl:grid-cols-2 max-sm:grid-cols-1"
      >
        {achievements.map((a, i) => (
          <AchievementTile key={a.id} achievement={a} index={i} />
        ))}
      </section>
    </div>
  )
}
