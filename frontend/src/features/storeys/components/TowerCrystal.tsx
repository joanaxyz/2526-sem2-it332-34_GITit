// Purely decorative faceted crystal the whole tower floats on, at the very
// bottom of the last storey (aria-hidden). Ringed by drifting rock so the keep
// reads as a floating island. Full tower-width at the top so it flows straight
// out of the drum above it.
export function TowerCrystal() {
  return (
    <svg className="tower-crystal" viewBox="0 0 240 168" aria-hidden="true">
      {/* drifting rock */}
      <g>
        <path className="ta-rock" d="M30 40 L42 35 L47 47 L37 54 L26 48 Z" />
        <path className="ta-rock" d="M198 52 L210 48 L214 60 L204 66 L194 60 Z" />
        <path className="ta-rock" d="M18 96 L29 92 L33 103 L23 109 Z" />
        <path className="ta-rock" d="M212 104 L224 100 L228 113 L217 119 L208 112 Z" />
        <path className="ta-rock" d="M104 150 L114 147 L117 158 L107 161 Z" />
        <circle className="ta-rock" cx="46" cy="128" r="2.6" />
        <circle className="ta-rock" cx="196" cy="138" r="3" />
      </g>

      {/* girdle band flowing out of the drum, then the faceted point */}
      <path className="ta-crystal" d="M8 6 L232 6 L236 28 L4 28 Z" />
      <path className="ta-crystal" d="M4 28 L120 160 L236 28 Z" />
      <g className="ta-crystal-facet">
        <line x1="120" y1="28" x2="120" y2="160" />
        <line x1="58" y1="28" x2="120" y2="160" />
        <line x1="182" y1="28" x2="120" y2="160" />
        <line x1="4" y1="28" x2="86" y2="92" />
        <line x1="236" y1="28" x2="154" y2="92" />
        <line x1="60" y1="6" x2="58" y2="28" />
        <line x1="120" y1="6" x2="120" y2="28" />
        <line x1="180" y1="6" x2="182" y2="28" />
      </g>
    </svg>
  )
}
