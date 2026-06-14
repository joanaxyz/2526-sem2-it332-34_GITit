import { useId } from 'react'

// The lectern is drawn as a single self-contained SVG so it reads as furniture
// standing in the room — grounded by its own floor shadow and lit by the open
// pages — rather than flat boxes against the wall. Inline (not an asset file)
// because hover/selected re-light the pages, aura, and motes via CSS classes.
// Gradient ids are namespaced per instance: a storey may render several tomes.
export function TomeLecternArt() {
  const uid = useId()
  const id = (name: string) => `${uid}-${name}`
  const ref = (name: string) => `url(#${id(name)})`
  return (
    <svg
      className="tome-lectern-art"
      viewBox="0 0 200 184"
      aria-hidden="true"
      focusable="false"
    >
      <defs>
        <radialGradient id={id('aura')} gradientUnits="userSpaceOnUse" cx="100" cy="48" r="60">
          <stop offset="0" stopColor="rgba(255, 205, 120, 0.5)" />
          <stop offset="0.55" stopColor="rgba(255, 180, 90, 0.16)" />
          <stop offset="1" stopColor="rgba(255, 180, 90, 0)" />
        </radialGradient>
        <radialGradient id={id('pages')} gradientUnits="userSpaceOnUse" cx="100" cy="50" r="54">
          <stop offset="0" stopColor="rgba(255, 222, 150, 0.92)" />
          <stop offset="0.45" stopColor="rgba(248, 186, 98, 0.6)" />
          <stop offset="0.8" stopColor="rgba(166, 106, 42, 0.22)" />
          <stop offset="1" stopColor="rgba(120, 70, 24, 0.08)" />
        </radialGradient>
        <linearGradient id={id('desk')} gradientUnits="userSpaceOnUse" x1="0" y1="40" x2="0" y2="94">
          <stop offset="0" stopColor="#0b2440" />
          <stop offset="1" stopColor="#04101f" />
        </linearGradient>
        <linearGradient id={id('stone')} gradientUnits="userSpaceOnUse" x1="0" y1="90" x2="0" y2="176">
          <stop offset="0" stopColor="#0c2238" />
          <stop offset="1" stopColor="#040e1b" />
        </linearGradient>
        <radialGradient id={id('shadow')} gradientUnits="userSpaceOnUse" cx="100" cy="173" r="58">
          <stop offset="0" stopColor="rgba(0, 0, 0, 0.55)" />
          <stop offset="0.7" stopColor="rgba(0, 0, 0, 0.26)" />
          <stop offset="1" stopColor="rgba(0, 0, 0, 0)" />
        </radialGradient>
      </defs>

      {/* Light rising off the pages — wakes on hover/selected. */}
      <ellipse className="tome-svg-aura" cx="100" cy="48" rx="60" ry="36" fill={ref('aura')} />

      {/* Floor shadow grounds the piece on the storey floor. */}
      <ellipse cx="100" cy="173" rx="58" ry="7.5" fill={ref('shadow')} />

      {/* Stepped plinth. */}
      <polygon
        points="46,174 154,174 147,161 53,161"
        fill={ref('stone')}
        stroke="rgba(45, 245, 255, 0.85)"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <polygon
        points="61,161 139,161 133,149 67,149"
        fill={ref('stone')}
        stroke="rgba(45, 245, 255, 0.6)"
        strokeWidth="2"
        strokeLinejoin="round"
      />

      {/* Tapered column with an engraved groove. */}
      <polygon
        points="93,149 107,149 104,99 96,99"
        fill={ref('stone')}
        stroke="rgba(45, 245, 255, 0.45)"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <path d="M100 106 V143" stroke="rgba(45, 245, 255, 0.16)" strokeWidth="1.2" />
      <rect
        x="86"
        y="90.5"
        width="28"
        height="9"
        rx="2"
        fill={ref('stone')}
        stroke="rgba(45, 245, 255, 0.55)"
        strokeWidth="2"
      />

      {/* Slanted reading desk: tilted face plus a front lip for thickness. */}
      <polygon
        points="36,84 164,84 160,93.5 40,93.5"
        fill="#04101f"
        stroke="rgba(45, 245, 255, 0.5)"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <polygon
        className="tome-svg-desk-face"
        points="52,40 148,40 164,84 36,84"
        fill={ref('desk')}
        stroke="rgba(45, 245, 255, 0.6)"
        strokeWidth="2.25"
        strokeLinejoin="round"
      />
      <polygon
        points="58,46 142,46 155,79 45,79"
        fill="none"
        stroke="rgba(45, 245, 255, 0.15)"
        strokeWidth="1.2"
      />

      {/* Open book: dim leaves at rest, page-stack edges below the curves. */}
      <path
        d="M100 75 C 85 78.5, 68 77, 57 71.5 L 62.5 48 C 73 52, 87 52.5, 100 49.5 Z"
        fill="#0d2540"
        stroke="rgba(45, 245, 255, 0.5)"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path
        d="M100 75 C 115 78.5, 132 77, 143 71.5 L 137.5 48 C 127 52, 113 52.5, 100 49.5 Z"
        fill="#0d2540"
        stroke="rgba(45, 245, 255, 0.5)"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path
        d="M57 74.5 C 68 80, 85 81.5, 100 78 C 115 81.5, 132 80, 143 74.5"
        fill="none"
        stroke="rgba(45, 245, 255, 0.3)"
        strokeWidth="1.2"
      />
      <path
        d="M59 77.5 C 70 82.5, 86 84, 100 80.5 C 114 84, 130 82.5, 141 77.5"
        fill="none"
        stroke="rgba(45, 245, 255, 0.3)"
        strokeWidth="1.2"
        opacity="0.55"
      />

      {/* The lit pages — window-amber belongs to book interiors, the one warm
          note the world allows outside windows and doors. */}
      <g className="tome-svg-pages">
        <path
          d="M100 75 C 85 78.5, 68 77, 57 71.5 L 62.5 48 C 73 52, 87 52.5, 100 49.5 Z"
          fill={ref('pages')}
        />
        <path
          d="M100 75 C 115 78.5, 132 77, 143 71.5 L 137.5 48 C 127 52, 113 52.5, 100 49.5 Z"
          fill={ref('pages')}
        />
        <g stroke="rgba(82, 46, 12, 0.6)" strokeWidth="1.4" strokeLinecap="round">
          <path d="M68 56.5 L91 54.5" />
          <path d="M69.5 61.5 L92 59.5" />
          <path d="M71 66.5 L91 64.5" />
          <path d="M109 54.5 L132 56.5" />
          <path d="M108 59.5 L130.5 61.5" />
          <path d="M109 64.5 L129 66.5" />
        </g>
      </g>
      <path d="M100 49.5 V75" stroke="rgba(45, 245, 255, 0.6)" strokeWidth="1.8" />

      {/* Arcane motes drifting off the pages — only while lit. */}
      <g className="tome-svg-motes" fill="#ffd98f">
        <circle className="tome-svg-mote" cx="87" cy="27" r="1.6" />
        <circle className="tome-svg-mote" cx="113" cy="20" r="2" />
        <circle className="tome-svg-mote" cx="99" cy="11" r="1.3" />
      </g>
    </svg>
  )
}
