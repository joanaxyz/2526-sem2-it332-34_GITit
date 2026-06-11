import type { RankTier } from '@/features/dashboard/rank'

/**
 * CSS-art rank crest: a beveled hexagon in the tier's color with a glowing
 * mini tower (lit door, spire) inside. Pulses slowly; tilts in 3D on hover.
 */
export function RankEmblem({ tier, className }: { tier: RankTier; className?: string }) {
  return (
    <div
      className={`rank-emblem ${className ?? ''}`}
      style={{
        ['--rank-color' as string]: tier.color,
        ['--rank-color-rgb' as string]: tier.colorRgb,
      }}
      role="img"
      aria-label={`Rank emblem: ${tier.name}`}
    >
      <span className="rank-emblem-halo" aria-hidden="true" />
      <div className="rank-emblem-frame" aria-hidden="true">
        <div className="rank-emblem-face">
          <span className="rank-emblem-pip rank-emblem-pip--left" />
          <span className="rank-emblem-pip rank-emblem-pip--right" />
          <div className="rank-emblem-tower">
            <span className="rank-emblem-tower-spire" />
            <span className="rank-emblem-tower-roof" />
            <span className="rank-emblem-tower-body">
              <span className="rank-emblem-tower-door" />
            </span>
            <span className="rank-emblem-tower-base" />
          </div>
        </div>
      </div>
    </div>
  )
}
