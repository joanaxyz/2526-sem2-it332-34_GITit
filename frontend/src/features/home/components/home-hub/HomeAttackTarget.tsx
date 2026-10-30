import type { Ref } from 'react'

type HomeAttackTargetProps = {
  /** Wrapper the hit flinch animates; the bob lives on its parent. */
  bodyRef: Ref<HTMLDivElement>
  /** Invisible impact point at the crystal's heart. */
  anchorRef: Ref<HTMLDivElement>
}

/** The practice crystal the spellbook fires at. It floats over its own ground
 *  glow, so ground-planted spells bloom on the floor beneath it. */
export function HomeAttackTarget({ bodyRef, anchorRef }: HomeAttackTargetProps) {
  return (
    <div className="home-attack-target" aria-hidden="true">
      <div className="home-attack-target-float">
        <div className="home-attack-target-body" ref={bodyRef}>
          <svg className="home-attack-target-art" viewBox="0 0 120 120" focusable="false">
            <defs>
              <radialGradient id="home-attack-target-core" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#ffffff" />
                <stop offset="45%" stopColor="currentColor" stopOpacity="0.9" />
                <stop offset="100%" stopColor="currentColor" stopOpacity="0" />
              </radialGradient>
            </defs>
            <g className="home-attack-target-ring home-attack-target-ring--outer">
              <circle cx="60" cy="60" r="54" fill="none" stroke="currentColor" strokeOpacity="0.55" strokeWidth="1.5" strokeDasharray="10 6 2 6" />
            </g>
            <g className="home-attack-target-ring home-attack-target-ring--inner">
              <circle cx="60" cy="60" r="44" fill="none" stroke="currentColor" strokeOpacity="0.35" strokeWidth="1" />
              <path d="M60 10v9M60 101v9M10 60h9M101 60h9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </g>
            <g className="home-attack-target-crystal">
              <path d="M60 24 L82 58 L60 96 L38 58 Z" fill="currentColor" fillOpacity="0.16" />
              <path d="M60 24 L38 58 L60 64 Z" fill="currentColor" fillOpacity="0.55" />
              <path d="M60 24 L82 58 L60 64 Z" fill="currentColor" fillOpacity="0.32" />
              <path d="M38 58 L60 64 L60 96 Z" fill="currentColor" fillOpacity="0.24" />
              <path d="M82 58 L60 64 L60 96 Z" fill="currentColor" fillOpacity="0.12" />
              <path d="M60 24 L82 58 L60 96 L38 58 Z M38 58 L60 64 L82 58 M60 24 L60 96" fill="none" stroke="#e6f6ff" strokeOpacity="0.85" strokeWidth="1.25" strokeLinejoin="round" />
              <circle cx="60" cy="60" r="11" fill="url(#home-attack-target-core)" />
            </g>
          </svg>
          <div className="home-attack-anchor" ref={anchorRef} />
        </div>
      </div>
      <span className="home-attack-target-shadow" />
    </div>
  )
}
