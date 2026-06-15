import type { CSSProperties } from 'react'

/**
 * Outline-only wireframe of a storey, shown while its real art + content load.
 *
 * The tower used to flash its *finished* fallback SVGs (CrownArt/HallArt) during
 * loading — and the crowned fallback even drew its own window band, doubling the
 * separate `WindowStorey` until the fetch resolved. This draws the storey as a
 * stroked "blueprint" instead: a true skeleton (no fills, dashed neon outlines)
 * that the real, painted pieces animate in over once they arrive. Geometry
 * mirrors the real pieces so the swap barely shifts layout.
 */
function delay(seconds: number): CSSProperties {
  return { animationDelay: `${seconds}s` }
}

function RoofSkeleton() {
  return (
    <svg
      className="tower-skel-art tower-skel-roof"
      style={delay(0)}
      viewBox="0 0 560 250"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <path d="M280 38 L462 132 L535 132 L504 191 L56 191 L25 132 L98 132 Z" />
      <line x1="280" y1="70" x2="280" y2="22" />
      <polygon points="280,2 296,18 280,34 264,18" />
      <circle cx="280" cy="38" r="6.5" />
      <path d="M48 193 H512 L493 221 H67 Z" />
      <path d="M82 220 H478 V236 H82 Z" />
      <path className="skel-faint" d="M111 116 H449" />
      <path className="skel-faint" d="M83 148 H477" />
      <path className="skel-faint" d="M62 179 H498" />
    </svg>
  )
}

function WindowSkeleton() {
  return (
    <svg
      className="tower-skel-art tower-skel-window"
      style={delay(0.12)}
      viewBox="0 0 480 148"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <rect x="36" y="0" width="408" height="104" />
      <path d="M162,42.8 A18.8 18.8 0 0 1 199.6,42.8 L199.6,84 Q199.6,87.2 196.4,87.2 L165.2,87.2 Q162,87.2 162,84 Z" />
      <path d="M221.2,42.8 A18.8 18.8 0 0 1 258.8,42.8 L258.8,84 Q258.8,87.2 255.6,87.2 L224.4,87.2 Q221.2,87.2 221.2,84 Z" />
      <path d="M280.4,42.8 A18.8 18.8 0 0 1 318,42.8 L318,84 Q318,87.2 314.8,87.2 L283.6,87.2 Q280.4,87.2 280.4,84 Z" />
      <rect x="20" y="101.6" width="440" height="25.6" />
      <path d="M31.5 124.8 H448.5 V138.2 H31.5 Z" />
    </svg>
  )
}

function AdventureSkeleton() {
  return (
    <svg
      className="tower-skel-art tower-skel-fill"
      style={delay(0.24)}
      viewBox="0 0 368 220"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <rect x="4" y="4" width="360" height="212" rx="9" />
      <path d="M140 206 V118 A44 44 0 0 1 228 118 V206" />
      <line className="skel-faint" x1="184" y1="80" x2="184" y2="206" />
      <path className="skel-faint" d="M152 206 V120 A32 32 0 0 1 216 120 V206" />
    </svg>
  )
}

function ChallengeSkeleton() {
  const doors = [40, 149, 258]
  return (
    <svg
      className="tower-skel-art tower-skel-fill"
      style={delay(0.42)}
      viewBox="0 0 368 250"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <rect x="4" y="4" width="360" height="242" rx="9" />
      {doors.map((x) => (
        <path key={x} d={`M${x} 232 V128 A35 35 0 0 1 ${x + 70} 128 V232`} />
      ))}
    </svg>
  )
}

function LandingSkeleton({ delaySeconds }: { delaySeconds: number }) {
  return (
    <svg
      className="tower-skel-art tower-skel-fill"
      style={delay(delaySeconds)}
      viewBox="0 0 480 44"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <rect x="14" y="9" width="452" height="22" rx="4" />
      <path className="skel-faint" d="M70 9 V31 M170 9 V31 M270 9 V31 M370 9 V31" />
    </svg>
  )
}

export function TowerStoreySkeleton({ isFirst = false }: { isFirst?: boolean }) {
  return (
    <div className="tower-skel" aria-hidden="true">
      {isFirst ? (
        <div className="tower-roof-stage">
          <RoofSkeleton />
        </div>
      ) : null}
      <div className="tower-window-stage">
        <WindowSkeleton />
      </div>
      <div className="tower-skel-stage tower-skel-stage--adventure">
        <AdventureSkeleton />
      </div>
      <div className="tower-skel-landing">
        <LandingSkeleton delaySeconds={0.3} />
      </div>
      <div className="tower-skel-stage tower-skel-stage--challenge">
        <ChallengeSkeleton />
      </div>
      <div className="tower-skel-landing">
        <LandingSkeleton delaySeconds={0.5} />
      </div>
    </div>
  )
}
