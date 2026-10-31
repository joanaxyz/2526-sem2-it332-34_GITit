import type { RectSnapshot } from './gameplayWorkspaceTourLayout'

type SpotlightRect = Pick<RectSnapshot, 'left' | 'top' | 'width' | 'height'>

export function GameplayWorkspaceTourSpotlight({
  markerId,
  viewportWidth,
  viewportHeight,
  holes,
  spotlight,
  targetVisible,
  arrowPath,
}: {
  markerId: string
  viewportWidth: number
  viewportHeight: number
  holes: readonly SpotlightRect[]
  spotlight: SpotlightRect
  targetVisible: boolean
  arrowPath: string
}) {
  return (
    <>
      {/* One dimming layer with cut-outs: the spotlit target plus any revealed
          regions stay readable, since tours explain them rather than hide them. */}
      <svg
        className="workspace-tour__veil"
        width={viewportWidth}
        height={viewportHeight}
        aria-hidden="true"
      >
        <defs>
          <mask id={`${markerId}-veil`} maskUnits="userSpaceOnUse" x="0" y="0" width={viewportWidth} height={viewportHeight}>
            <rect width={viewportWidth} height={viewportHeight} fill="white" />
            {holes.map((hole, index) => (
              <rect
                key={index}
                x={hole.left}
                y={hole.top}
                width={hole.width}
                height={hole.height}
                rx="10"
                fill="black"
              />
            ))}
          </mask>
        </defs>
        <rect width={viewportWidth} height={viewportHeight} mask={`url(#${markerId}-veil)`} />
      </svg>

      {targetVisible ? <><div
        className="workspace-tour__spotlight"
        data-testid="workspace-tour-spotlight"
        aria-hidden="true"
        style={{
          left: spotlight.left,
          top: spotlight.top,
          width: spotlight.width,
          height: spotlight.height,
        }}
      />

      <svg className="workspace-tour__connector" aria-hidden="true">
        <defs>
          <marker
            id={markerId}
            markerHeight="8"
            markerWidth="8"
            markerUnits="userSpaceOnUse"
            viewBox="0 0 8 8"
            refX="4"
            refY="4"
          >
            <circle cx="4" cy="4" r="2.5" />
          </marker>
        </defs>
        <path
          className="workspace-tour__connector-line"
          d={arrowPath}
          markerEnd={`url(#${markerId})`}
        />
      </svg></> : null}
    </>
  )
}
