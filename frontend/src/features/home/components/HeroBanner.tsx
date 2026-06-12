import { Award, GitBranch } from 'lucide-react'
import { Link } from 'react-router-dom'

import heroLoop from '@/assets/video/hub-hero-loop.mp4'
import type { Achievement } from '@/features/home/achievements'
import type { HomeSummary } from '@/features/home/types'

function getInitials(username: string) {
  return username.slice(0, 2).toUpperCase()
}

/**
 * Game-launcher hero, composed like the reference: the environment loop
 * fills the banner; a hatched glass band shelves its bottom edge; the
 * glass hexagon wordmark plate rises out of the band at center with the
 * emblem and stacked logotype inside; the streak / latest-achievement
 * readouts sit directly on the band at the far edges (the right one
 * mirrored, icon outward); the launcher CTAs sit below the hero.
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
        <video
          src={heroLoop}
          autoPlay
          loop
          muted
          playsInline
          aria-hidden="true"
          className="hub-hero-media"
        />
        <div className="hub-hero-veil" aria-hidden="true" />
        <div className="hub-hero-scan" aria-hidden="true" />
        <div className="hub-hero-band" aria-hidden="true" />

        {/* Bottom assembly: readout — glass hexagon plate — readout */}
        <div className="hub-hero-ledge">
          <div className="hub-stat animate-fade-in-up" style={{ animationDelay: '200ms' }}>
            <span className="hub-stat-icon" aria-hidden="true">
              {getInitials(playerName)}
            </span>
            <div className="min-w-0">
              <p className="hub-stat-label">Day Streak</p>
              <p className="hub-stat-value truncate">
                {streak.current} day{streak.current === 1 ? '' : 's'}
                <span className="hub-stat-divider" aria-hidden="true" />
                <span className="font-mono text-[0.66rem] font-semibold text-muted-foreground">
                  best {streak.longest}
                </span>
              </p>
            </div>
          </div>

          <div className="hub-logo-frame animate-fade-in-up">
            <div className="hub-logo-frame-body">
              <GitBranch aria-hidden="true" className="hub-logo-emblem" />
              <h1 className="hub-logo-stack">
                <span className="hub-logo-title">GIT</span>
                <span className="hub-logo-wordmark">IT!</span>
              </h1>
            </div>
          </div>

          <div className="hub-stat animate-fade-in-up" style={{ animationDelay: '260ms' }}>
            <div className="min-w-0 text-right">
              <p className="hub-stat-label">Latest Achievement</p>
              {latest ? (
                <p className="hub-stat-value truncate">
                  {latest.title}
                  <span className="hub-stat-divider" aria-hidden="true" />
                  <span className="font-mono text-[0.66rem] font-semibold text-[#FBBF24]">
                    ★ {latest.points}
                  </span>
                </p>
              ) : (
                <p className="hub-stat-value truncate text-muted-foreground">None yet — climb!</p>
              )}
            </div>
            <span
              className="hub-stat-icon"
              style={
                latest
                  ? {
                      borderColor: `${latest.color}66`,
                      color: latest.color,
                      boxShadow: `0 0 12px ${latest.color}33`,
                    }
                  : { borderColor: 'rgba(167,139,250,0.4)', color: '#A78BFA' }
              }
              aria-hidden="true"
            >
              {latest ? <latest.Icon className="size-5" /> : <Award className="size-5" />}
            </span>
          </div>
        </div>
      </section>

      {/* Launcher CTAs — identical steel slabs below the hero, per the reference */}
      <div className="hub-cta-row animate-fade-in-up" style={{ animationDelay: '120ms' }}>
        <Link className="hub-cta chamfer-frame" to="/tower">
          <span className="chamfer-body">Enter Tower</span>
        </Link>
        <button type="button" className="hub-cta chamfer-frame" onClick={onViewStats}>
          <span className="chamfer-body">View Stats</span>
        </button>
      </div>
    </>
  )
}
