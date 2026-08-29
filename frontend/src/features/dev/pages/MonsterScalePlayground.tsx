import { useEffect, useMemo, useState } from 'react'

import type { SpriteDef } from '@/shared/cosmetics/types'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { SpritePixelAnchor } from '@/shared/sprites/pixelBounds'
import type { SpriteAnimation } from '@/shared/sprites/types'
import { loadSpritePixelAnchor } from '@/shared/sprites/usePixelBounds'
import { listStoryWorldMonsters, listStoryWorlds, type StoryWorldMonsterEntry } from '@/shared/story-worlds/registry'

import './MonsterScalePlayground.css'

function idleAnimation(monster: StoryWorldMonsterEntry): SpriteAnimation {
  const sprite: SpriteDef = monster.skin.sprites.idle
  return {
    name: `${monster.slug}.scale-preview`,
    src: sprite.src,
    frameWidth: sprite.frameWidth,
    frameHeight: sprite.frameHeight,
    columns: sprite.columns,
    rows: sprite.rows,
    frameCount: sprite.frameCount,
    fps: sprite.fps,
    loop: sprite.loops,
    displayScale: sprite.displayScale,
  }
}

function MonsterScaleCell({
  anchor,
  monster,
  worldSlug,
}: {
  anchor: SpritePixelAnchor | null | undefined
  monster: StoryWorldMonsterEntry
  worldSlug: string
}) {
  const animation = idleAnimation(monster)
  const visibleHeight = anchor
    ? Math.round(anchor.bounds.height * (animation.displayScale ?? 1) * monster.skin.scale)
    : null
  const anchorScale = (animation.displayScale ?? 1) * monster.skin.scale
  const bottomOffset = (anchor?.bottomOffset ?? monster.skin.metrics.foot_offset ?? 0) * anchorScale
  const centerOffsetX = (anchor?.centerOffsetX ?? 0) * anchorScale

  return (
    <article
      className="monster-scale-card"
      data-monster={monster.slug}
      data-world={worldSlug}
      data-visible-height={visibleHeight ?? undefined}
    >
      <div className="monster-scale-card__stage">
        <span aria-hidden="true" className="monster-scale-card__baseline" />
        <div
          className="monster-scale-card__actor"
          style={{ transform: `translate(calc(-50% + ${centerOffsetX}px), ${bottomOffset}px)` }}
        >
          <SpriteAnimator
            animation={animation}
            scale={monster.skin.scale}
            layoutAnimation={animation}
            autoPlay={false}
            pixelated
            aria-label={monster.label}
          />
        </div>
      </div>
      <div className="monster-scale-card__meta">
        <strong>{monster.label}</strong>
        <span>{visibleHeight ? `${visibleHeight}px` : 'measuring'}</span>
      </div>
    </article>
  )
}

function MonsterScalePlayground() {
  const worlds = useMemo(
    () => listStoryWorlds().map((world) => ({ world, monsters: listStoryWorldMonsters(world.slug) })),
    [],
  )
  const entries = useMemo(
    () => worlds.flatMap(({ world, monsters }) => monsters.map((monster) => ({ worldSlug: world.slug, monster }))),
    [worlds],
  )
  const [anchors, setAnchors] = useState<Record<string, SpritePixelAnchor | null>>({})

  useEffect(() => {
    let active = true

    async function measureInOrder() {
      for (const { worldSlug, monster } of entries) {
        const key = `${worldSlug}:${monster.slug}`
        let anchor = await loadSpritePixelAnchor(idleAnimation(monster))

        if (!anchor) {
          await new Promise((resolve) => window.setTimeout(resolve, 50))
          anchor = await loadSpritePixelAnchor(idleAnimation(monster))
        }

        if (!active) return
        setAnchors((current) => ({ ...current, [key]: anchor }))
      }
    }

    void measureInOrder()
    return () => {
      active = false
    }
  }, [entries])

  return (
    <main className="workspace-bg monster-scale-gallery">
      <header className="monster-scale-gallery__header">
        <h1>Monster scale gallery</h1>
        <p>Real idle sprites, visible-pixel height, one neutral baseline.</p>
      </header>

      <div className="monster-scale-gallery__worlds">
        {worlds.map(({ world, monsters }) => (
          <section key={world.slug} aria-labelledby={`${world.slug}-title`}>
            <div className="monster-scale-gallery__section-header">
              <h2 id={`${world.slug}-title`}>{world.label}</h2>
              <span>
                {monsters.length} monsters
              </span>
            </div>
            <div className="monster-scale-gallery__grid">
              {monsters.map((monster) => (
                <MonsterScaleCell
                  key={monster.slug}
                  anchor={anchors[`${world.slug}:${monster.slug}`]}
                  monster={monster}
                  worldSlug={world.slug}
                />
              ))}
            </div>
          </section>
        ))}
      </div>
    </main>
  )
}

export const Component = MonsterScalePlayground
