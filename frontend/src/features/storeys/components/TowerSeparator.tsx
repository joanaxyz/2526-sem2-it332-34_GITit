// Decorative widening band that bridges the narrow Command Adventure drum into
// the wider GIT Challenged drum (aria-hidden). Drawn as SVG so its outline reads
// identically to the crown + crystal — a corbelled cornice with a gem medallion.
export function TowerSeparator() {
  return (
    <svg className="tower-sep" viewBox="0 0 240 74" aria-hidden="true">
      {/* widening corbelled cornice */}
      <path className="ta-stroke" d="M30 8 L210 8 L232 48 L8 48 Z" />
      <g className="ta-line">
        <path d="M42 10 L36 47" /><path d="M64 10 L60 47" /><path d="M86 10 L84 47" />
        <path d="M156 10 L158 47" /><path d="M178 10 L182 47" /><path d="M200 10 L206 47" />
      </g>
      {/* full-width base ledge that meets the challenge drum */}
      <path className="ta-stroke" d="M2 50 L238 50 L238 62 L2 62 Z" />
      <line className="ta-line" x1="2" y1="56" x2="238" y2="56" />
      {/* gem medallion */}
      <g transform="translate(120 28) rotate(45)">
        <rect className="ta-stroke" x="-11" y="-11" width="22" height="22" />
        <rect className="ta-crystal" x="-5" y="-5" width="10" height="10" />
      </g>
    </svg>
  )
}
