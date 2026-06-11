import type { RankTier } from '@/features/home/rank'
import { CHARACTER1 } from '@/shared/sprites/characters'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'

/**
 * Game-client agent showcase: the player's animated character floating over
 * a glowing pedestal, with a name + rank caption. Uses the shared
 * SpriteAnimator (character1 idle sheet).
 */
export function CharacterShowcase({
  playerName,
  tier,
  scale = 0.8,
}: {
  playerName: string
  tier: RankTier
  /** Sprite display scale (0.8 = compact card, ~1.2 = showcase stage). */
  scale?: number
}) {
  return (
    <div className="flex flex-col items-center">
      <div className="sprite-stage">
        <span className="sprite-stage-aura" aria-hidden="true" />
        <div className="sprite-stage-float">
          <SpriteAnimator
            animation={CHARACTER1.idle}
            scale={scale}
            aria-label={`${playerName}'s character, idle animation`}
          />
        </div>
      </div>
      <div className="sprite-pedestal" aria-hidden="true" />
      <p className="mt-1 font-mono text-[0.6rem] uppercase tracking-[0.22em] text-aurora-blue/70">
        Active Agent
      </p>
      <p className="mt-0.5 text-sm font-bold tracking-tight">{playerName}</p>
      <span
        className="mt-1.5 inline-flex items-center rounded-full px-2.5 py-0.5 font-mono text-[0.6rem] font-semibold uppercase tracking-[0.14em]"
        style={{
          color: tier.color,
          border: `1px solid ${tier.color}55`,
          background: `${tier.color}14`,
          boxShadow: `0 0 10px ${tier.color}22`,
        }}
      >
        {tier.name}
      </span>
    </div>
  )
}
