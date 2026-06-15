import { useId } from 'react'

/**
 * Background art for a tower hall (Command Adventure / Challenges / Tome stage),
 * drawn as real inline SVG that replaces the old `.tower-*-stage` border, fill
 * and pseudo-element frame.
 *
 * Halls are the only **content-driven, variable-height** pieces, so the SVG
 * stretches to fill its box (`preserveAspectRatio="none"`) while
 * `vector-effect="non-scaling-stroke"` keeps the neon border + frame lines a
 * crisp constant width at any height. The outer glow is a CSS `drop-shadow` on
 * the SVG so it stays uniform instead of stretching with the box.
 *
 * The adventure hall also carries a foot-rail below it (the old `::after`).
 */
export function HallArt({ variant }: { variant: 'adventure' | 'challenge' | 'tome' }) {
  const uid = useId().replace(/[:]/g, '')
  const wall = `wall-${uid}`
  const foot = `foot-${uid}`
  // The challenge frame starts lower (its header band is taller).
  const frameTop = variant === 'challenge' ? 19.2 : 10.4

  return (
    <>
      <svg
        className="tower-hall-art"
        viewBox="0 0 368 200"
        preserveAspectRatio="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
        focusable="false"
      >
        <defs>
          <linearGradient id={wall} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#0a2236" />
            <stop offset="70%" stopColor="#081b2f" />
            <stop offset="100%" stopColor="#050f1d" />
          </linearGradient>
        </defs>
        {/* outer neon wall */}
        <rect x="1.25" y="1.25" width="365.5" height="197.5" fill={`url(#${wall})`} stroke="rgba(45,245,255,0.92)" strokeWidth="2.5" vectorEffect="non-scaling-stroke" />
        {/* dark inner edge (the old inset 2px shadow border) */}
        <rect x="3.25" y="3.25" width="361.5" height="193.5" fill="none" stroke="rgba(5,14,24,0.55)" strokeWidth="2" vectorEffect="non-scaling-stroke" />
        {/* inner frame lines */}
        <line x1="10.4" y1={frameTop} x2="10.4" y2="189.6" stroke="rgba(45,245,255,0.17)" strokeWidth="1" vectorEffect="non-scaling-stroke" />
        <line x1="357.6" y1={frameTop} x2="357.6" y2="189.6" stroke="rgba(45,245,255,0.17)" strokeWidth="1" vectorEffect="non-scaling-stroke" />
      </svg>

      {variant === 'adventure' ? (
        <svg
          className="tower-hall-foot"
          viewBox="0 0 100 20"
          preserveAspectRatio="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
          focusable="false"
        >
          <defs>
            <linearGradient id={foot} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="rgb(10,30,48)" stopOpacity="0.98" />
              <stop offset="100%" stopColor="rgb(4,16,29)" stopOpacity="0.98" />
            </linearGradient>
          </defs>
          <rect x="1.25" y="1.25" width="97.5" height="17.5" fill={`url(#${foot})`} stroke="rgba(45,245,255,0.9)" strokeWidth="2.5" vectorEffect="non-scaling-stroke" />
        </svg>
      ) : null}
    </>
  )
}
