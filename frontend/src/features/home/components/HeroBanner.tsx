import { Award, GitBranch } from 'lucide-react'
import { Link } from 'react-router-dom'

import type { Achievement } from '@/features/home/achievements'
import type { HomeSummary } from '@/features/home/types'

/**
 * ⚠ PLACEHOLDER environment loop — swap this URL for the real looped
 * backdrop when it's ready. Everything else (veil, tint, scanlines)
 * already grades whatever plays here into the aurora palette.
 */
const HERO_ENVIRONMENT_SRC = 'https://media.giphy.com/media/xT9IgzoKnwFNmISR8I/giphy.gif'

function getInitials(username: string) {
  return username.slice(0, 2).toUpperCase()
}

/**
 * Game-launcher hero, composed like the reference: the environment loop
 * fills the banner; a hatched glass band shelves its bottom edge; the
 * glass GIT IT! plate straddles that edge at center, flanked by the
 * streak and latest-achievement plaques; the launcher CTAs sit below
 * the hero on the page itself.
 */
export function HeroBanner({
  summary,
  playerName,
  latest,
  onViewStats,
}: {
  summary: HomeSummary
  playerName: string
  latest: Achievement | null
  onViewStats: () => void
}) {
  const streak = summary.streak

  return (
    <>
      <section className="full-bleed hub-hero" aria-label="Player hub">
        <img
          src={HERO_ENVIRONMENT_SRC}
          alt=""
          aria-hidden="true"
          className="hub-hero-media"
        />
        <div className="hub-hero-veil" aria-hidden="true" />
        <div className="hub-hero-scan" aria-hidden="true" />
        <div className="hub-hero-band" aria-hidden="true" />

        {/* Bottom assembly: plaque — glass wordmark plate — plaque */}
        <div className="hub-hero-ledge">
          <div className="hub-info-card chamfer-frame animate-fade-in-up" style={{ animationDelay: '200ms' }}>
            <div className="chamfer-body">
              <span
                className="grid size-10 shrink-0 place-items-center rounded-md text-xs font-bold"
                style={{
                  background: 'linear-gradient(135deg, #0c1e38 0%, #091428 100%)',
                  border: '1.5px solid rgba(0,245,212,0.4)',
                  color: 'rgba(0,245,212,0.88)',
                }}
                aria-hidden="true"
              >
                {getInitials(playerName)}
              </span>
              <div className="min-w-0">
                <p className="font-mono text-[0.58rem] font-semibold uppercase tracking-[0.2em] text-aurora-blue/80">
                  Day Streak
                </p>
                <p className="mt-0.5 truncate text-sm font-bold text-foreground">
                  {streak.current} day{streak.current === 1 ? '' : 's'}
                  <span className="ml-2 font-mono text-[0.66rem] font-semibold text-muted-foreground">
                    best {streak.longest}
                  </span>
                </p>
              </div>
            </div>
          </div>

          <div className="hub-logo-frame animate-fade-in-up">
            <span className="hub-logo-glyph">
              <GitBranch aria-hidden="true" className="size-4 text-aurora-cyan" />
            </span>
            <div className="hub-logo-frame-body">
              <h1 className="hub-logo-wordmark">
                GIT <span className="text-primary">it!</span>
              </h1>
              <p className="hub-logo-tagline">Tower of Version Control</p>
            </div>
          </div>

          <div className="hub-info-card hub-info-card--end chamfer-frame animate-fade-in-up" style={{ animationDelay: '260ms' }}>
            <div className="chamfer-body">
              <span
                className="grid size-10 shrink-0 place-items-center rounded-md"
                style={{
                  background: 'linear-gradient(135deg, #1a1238 0%, #0d0a24 100%)',
                  border: `1.5px solid ${latest ? `${latest.color}66` : 'rgba(167,139,250,0.4)'}`,
                  color: latest?.color ?? '#A78BFA',
                  boxShadow: latest ? `0 0 12px ${latest.color}33` : 'none',
                }}
                aria-hidden="true"
              >
                {latest ? <latest.Icon className="size-5" /> : <Award className="size-5" />}
              </span>
              <div className="min-w-0">
                <p className="font-mono text-[0.58rem] font-semibold uppercase tracking-[0.2em] text-aurora-blue/80">
                  Latest Achievement
                </p>
                {latest ? (
                  <p className="mt-0.5 truncate text-sm font-bold text-foreground">
                    {latest.title}
                    <span className="ml-2 font-mono text-[0.66rem] font-semibold text-[#FBBF24]">
                      ★ {latest.points}
                    </span>
                  </p>
                ) : (
                  <p className="mt-0.5 truncate text-sm font-bold text-muted-foreground">None yet — climb!</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Launcher CTAs — below the hero, clearing the straddling plate */}
      <div className="hub-cta-row animate-fade-in-up" style={{ animationDelay: '120ms' }}>
        <Link className="hub-cta chamfer-frame" to="/tower">
          <span className="chamfer-body">Enter Tower</span>
        </Link>
        <button type="button" className="hub-cta hub-cta--ghost chamfer-frame" onClick={onViewStats}>
          <span className="chamfer-body">View Stats</span>
        </button>
      </div>
    </>
  )
}
