import { useRef } from 'react'

import { useCharacterController } from '@/features/tower-map/character/useCharacterController'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { CharacterDefinition, SpriteAnimatorHandle } from '@/shared/sprites/types'

/**
 * The player's companion on the tower page. Renders a pointer-transparent
 * layer over the whole page shell; the controller hook listens for shell
 * clicks and drives the sprite around (walk the landings, fly, teleport).
 *
 * Must be a direct child of `.tower-page-shell` - the controller anchors to
 * `parentElement` for coordinates and click capture.
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
