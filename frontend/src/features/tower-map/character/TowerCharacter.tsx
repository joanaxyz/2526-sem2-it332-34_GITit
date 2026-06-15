import { useRef } from 'react'

import { useCharacterController } from '@/features/tower-map/character/useCharacterController'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { CharacterDefinition, SpriteAnimatorHandle } from '@/shared/sprites/types'

/**
 * The player's companion on the tower page. Renders a pointer-transparent
 * layer over the tower stage; the controller hook listens for clicks on the
 * parent and drives the sprite around (walk the landings, fly, teleport).
 *
 * Must be a direct child of `.tower-stage-grid` - the controller anchors to
 * `parentElement` for coordinates and click capture, and living inside the
 * stage grid's stacking context is what lets the crenel parapets paint over
 * the companion's feet (see `.tower-character-layer` z-index).
 */
export function TowerCharacter({ character }: { character: CharacterDefinition }) {
  const layerRef = useRef<HTMLDivElement | null>(null)
  const bodyRef = useRef<HTMLDivElement | null>(null)
  const spriteRef = useRef<SpriteAnimatorHandle | null>(null)

  useCharacterController({ character, layerRef, bodyRef, spriteRef })

  return (
    <div className="tower-character-layer" ref={layerRef} aria-hidden="true">
      <div className="tower-character is-unspawned" ref={bodyRef}>
        <SpriteAnimator
          animation={character.sprites.idle}
          ref={spriteRef}
          scale={character.metrics.scale}
          aria-label="Your companion"
        />
      </div>
    </div>
  )
}
