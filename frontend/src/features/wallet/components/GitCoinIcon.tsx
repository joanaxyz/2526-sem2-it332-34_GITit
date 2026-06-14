import { useId } from 'react'

import { cn } from '@/shared/utils/cn'

const REEDED_EDGE_TICKS = Array.from({ length: 28 }, (_, i) => (i * 360) / 28)

/**
 * The GitCoin: a minted coin in the tower's aurora palette - cyan-to-ocean
 * rim with a reeded edge, dark navy face, and an embossed git-branch emblem.
 */
export function GitCoinIcon({ className }: { className?: string }) {
  const id = useId()
  const rimId = `${id}-rim`
  const faceId = `${id}-face`
  const emblemId = `${id}-emblem`

  return (
    <svg viewBox="0 0 48 48" className={cn('shrink-0', className)} role="img" aria-label="GitCoin">
      <defs>
        <linearGradient id={rimId} x1="10" y1="6" x2="40" y2="44" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#8dfff0" />
          <stop offset="0.45" stopColor="#00f5d4" />
          <stop offset="1" stopColor="#0090c0" />
        </linearGradient>
        <radialGradient id={faceId} cx="0.38" cy="0.28" r="0.9">
          <stop offset="0" stopColor="#13405a" />
          <stop offset="0.55" stopColor="#0a2238" />
          <stop offset="1" stopColor="#061325" />
        </radialGradient>
        <linearGradient id={emblemId} x1="4" y1="2" x2="20" y2="20" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#86fcec" />
          <stop offset="0.55" stopColor="#00f5d4" />
          <stop offset="1" stopColor="#00b4d8" />
        </linearGradient>
      </defs>

      {/* rim with reeded (notched) edge */}
      <circle cx="24" cy="24" r="22" fill={`url(#${rimId})`} />
      <g stroke="#06303c" strokeWidth="1.5" opacity="0.5">
        {REEDED_EDGE_TICKS.map((angle) => (
          <line key={angle} x1="24" y1="2.6" x2="24" y2="5.4" transform={`rotate(${angle} 24 24)`} />
        ))}
      </g>

      {/* bevel step + face */}
      <circle cx="24" cy="24" r="17.4" fill="#04212e" />
      <circle cx="24" cy="24" r="16.4" fill={`url(#${faceId})`} />
      <circle
        cx="24"
        cy="24"
        r="14.4"
        fill="none"
        stroke="rgba(0,245,212,0.32)"
        strokeWidth="0.9"
        strokeDasharray="2.3 3.1"
        strokeLinecap="round"
      />

      {/* git-branch emblem, dark relief copy underneath for the minted look */}
      <g
        transform="translate(15 15.2) scale(0.78)"
        fill="none"
        stroke="#02101c"
        strokeWidth="4"
        strokeLinecap="round"
        opacity="0.9"
      >
        <line x1="6" y1="3" x2="6" y2="15" />
        <path d="M18 9a9 9 0 0 1-9 9" />
        <circle cx="18" cy="6" r="3" />
        <circle cx="6" cy="18" r="3" />
      </g>
      <g
        transform="translate(14.6 14.6) scale(0.78)"
        fill="none"
        stroke={`url(#${emblemId})`}
        strokeWidth="2.6"
        strokeLinecap="round"
      >
        <line x1="6" y1="3" x2="6" y2="15" />
        <path d="M18 9a9 9 0 0 1-9 9" />
        <circle cx="18" cy="6" r="3" fill="#07202f" />
        <circle cx="6" cy="18" r="3" fill="#07202f" />
      </g>

      {/* shine: specular arc on the rim + sparkle on the face */}
      <path
        d="M11.6 16.4 A 14.6 14.6 0 0 1 19.6 9.7"
        fill="none"
        stroke="rgba(255,255,255,0.4)"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M32.4 12.2 l0.85 2 2 0.85 -2 0.85 -0.85 2 -0.85 -2 -2 -0.85 2 -0.85 z"
        fill="#c2fff6"
        opacity="0.95"
      />
    </svg>
  )
}
