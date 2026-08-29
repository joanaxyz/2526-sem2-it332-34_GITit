import type { SVGProps } from 'react'

// Hand-drawn line icons matching the reference mock's iconography where the
// stock set has no close match. Same 24×24 / 1.75-stroke grammar as lucide so
// they sit beside it seamlessly.

type IconProps = SVGProps<SVGSVGElement>

function base(props: IconProps): IconProps {
  return {
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.75,
    strokeLinecap: 'round',
    strokeLinejoin: 'round',
    'aria-hidden': true,
    ...props,
  }
}

/** Single rook icon — the mock's "Level Type" glyph. */
export function RookIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M7 21h10" />
      <path d="M8.5 21v-3.5h7V21" />
      <path d="M9 17.5 8 9h8l-1 8.5" />
      <path d="M6.5 9V4.5h2.4V7h2.2V4.5h1.8V7h2.2V4.5h2.4V9Z" />
    </svg>
  )
}

/** Filled five-point star for the stars fact row. */
export function StarSolidIcon(props: IconProps) {
  return (
    <svg {...base({ ...props, fill: 'currentColor', strokeWidth: 1 })}>
      <path d="M12 3.2 14.7 8.8 20.8 9.7 16.4 14 17.4 20.1 12 17.2 6.6 20.1 7.6 14 3.2 9.7 9.3 8.8 Z" />
    </svg>
  )
}

/** Circled check with a spark — the mock's TASK glyph. */
export function TaskSealIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <circle cx="11.4" cy="12.6" r="7.4" />
      <path d="m8.4 12.8 2.1 2.1 4-4.4" />
      <path d="M18.6 3.6v3.2M17 5.2h3.2" strokeWidth={1.4} />
    </svg>
  )
}

/** Bust silhouette for the Attempts row. */
export function BustIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <circle cx="12" cy="8" r="3.6" />
      <path d="M5.5 20c.9-4 3.4-6 6.5-6s5.6 2 6.5 6" />
    </svg>
  )
}
