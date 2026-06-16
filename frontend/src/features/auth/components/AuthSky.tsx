import { useMemo } from 'react'

import { computeSky } from '@/features/tower-map/sky/useTowerSky'

type AuthSkyProps = {
  /**
   * Hour (0..24) the sky is frozen at. The brand North Star is "a wizard's
   * tower at night", so the front door is deliberately fixed to a dusk-into-
   * night sky: violet horizon, moon high, stars out. A constant time also keeps
   * the form legible at any real-world hour (a dark sky never washes the glass).
   */
  hour?: number
}

/**
 * The living-sky atmosphere behind the auth screens. Reuses the real
 * {@link computeSky} day-night engine and the shared `.tower-sun/.tower-moon/
 * .tower-starfield` vocabulary (so the starfield twinkle inherits the global
 * `prefers-reduced-motion` fallback for free), but renders fixed and
 * scroll-free — none of the tower's storey/parallax machinery comes along.
 */
export function AuthSky({ hour = 21 }: AuthSkyProps) {
  const vars = useMemo(() => computeSky(hour).vars, [hour])

  return (
    <div className="auth-sky" style={vars} aria-hidden="true">
      <span className="tower-moon">
        <span className="tower-moon-crater tower-moon-crater--a" />
        <span className="tower-moon-crater tower-moon-crater--b" />
        <span className="tower-moon-crater tower-moon-crater--c" />
      </span>
      <div className="tower-starfield tower-starfield--far" />
      <div className="tower-starfield tower-starfield--near" />
      <div className="auth-sky-scrim" />
    </div>
  )
}
