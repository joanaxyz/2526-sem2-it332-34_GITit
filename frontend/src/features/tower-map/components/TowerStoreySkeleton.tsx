import type { CSSProperties } from 'react'

/** One neutral outline skeleton while real tower assets load. */
function delay(seconds: number): CSSProperties {
  return { animationDelay: `${seconds}s` }
}

function StoreySkeleton({ isFirst }: { isFirst: boolean }) {
  const wallTop = isFirst ? 188 : 38
  return (
    <svg
      className="tower-skel-art tower-skel-fill"
      style={delay(0)}
      viewBox="0 0 560 420"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      {isFirst ? (
        <>
          <path d="M280 32 L462 118 L535 118 L504 170 L56 170 L25 118 L98 118 Z" />
          <line x1="280" y1="62" x2="280" y2="16" />
          <polygon points="280,2 296,18 280,34 264,18" />
        </>
      ) : null}
      <rect x="80" y={wallTop} width="400" height="184" rx="9" />
      <path className="skel-faint" d={`M128 ${wallTop + 42} H432`} />
      <path className="skel-faint" d={`M128 ${wallTop + 86} H432`} />
      <path className="skel-faint" d={`M128 ${wallTop + 130} H432`} />
      <path d={`M230 ${wallTop + 172} V${wallTop + 98} A50 50 0 0 1 330 ${wallTop + 98} V${wallTop + 172}`} />
    </svg>
  )
}

export function TowerStoreySkeleton({ isFirst = false }: { isFirst?: boolean }) {
  return (
    <div className="tower-skel" aria-hidden="true">
      <div className="tower-skel-stage">
        <StoreySkeleton isFirst={isFirst} />
      </div>
    </div>
  )
}
