import { useState, type CSSProperties, type ReactNode } from 'react'

import {
  piecePointToCss,
  pieceSizeToCss,
} from '@/features/tower-map/components/towerPieceData'
import { backendUrl } from '@/shared/api/httpClient'
import type {
  AssetSpriteDescriptor,
  TowerArtifactAssetDescriptor,
  TowerPieceAssetDescriptor,
} from '@/shared/assets/types'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { SpriteAnimation } from '@/shared/sprites/types'
import { cn } from '@/shared/utils/cn'

type ArtifactBase = {
  id: number | string
  targetInstanceId?: string
  assetSlug: string
  x: number
  y: number
  scale: number
  width: number
  height: number
  rotation: number
  zIndex: number
}

export function TowerArtifact({
  artifact,
  descriptor,
  pieceDescriptor,
  pieceVariant,
  interactive,
  selected,
  locked,
  accent,
  label,
  children,
  onClick,
  onPointerDown,
  className,
}: {
  artifact: ArtifactBase
  descriptor: TowerArtifactAssetDescriptor | null
  pieceDescriptor: TowerPieceAssetDescriptor | null
  pieceVariant?: string
  interactive?: boolean
  selected?: boolean
  locked?: boolean
  accent?: string
  label?: string
  children?: ReactNode
  onClick?: () => void
  onPointerDown?: (event: React.PointerEvent<HTMLElement>) => void
  className?: string
}) {
  const [action, setAction] = useState<'default' | 'hover' | 'click'>('default')
  const sprite = pickSprite(descriptor, action)
  const style = {
    ...piecePointToCss(artifact.x, artifact.y, pieceDescriptor, pieceVariant),
    ...pieceSizeToCss(artifact.width, artifact.height, pieceDescriptor, pieceVariant),
    transform: `translate(-50%, -50%) scale(${artifact.scale}) rotate(${artifact.rotation}deg)`,
    zIndex: artifact.zIndex,
    '--artifact-accent': accent,
  } as CSSProperties
  const content = (
    <>
      <ArtifactVisual sprite={sprite} slug={artifact.assetSlug} />
      {children}
    </>
  )
  const common = {
    className: cn(
      'tower-artifact',
      interactive && 'tower-artifact--interactive',
      selected && 'is-selected',
      locked && 'is-locked',
      className,
    ),
    style,
    'data-selected': selected ? 'true' : undefined,
    'data-piece-id': artifact.targetInstanceId,
    onPointerEnter: () => {
      if (descriptor?.sprites.hover) setAction('hover')
    },
    onPointerLeave: () => setAction('default'),
    onPointerDown,
  }

  if (interactive) {
    return (
      <button
        type="button"
        {...common}
        aria-pressed={selected}
        aria-label={label}
        onClick={() => {
          if (descriptor?.sprites.click) setAction('click')
          onClick?.()
        }}
      >
        {content}
      </button>
    )
  }

  return (
    <span {...common} aria-hidden="true">
      {content}
    </span>
  )
}

function pickSprite(
  descriptor: TowerArtifactAssetDescriptor | null,
  action: 'default' | 'hover' | 'click',
) {
  if (!descriptor) return null
  return descriptor.sprites[action] ?? descriptor.sprites.default ?? Object.values(descriptor.sprites)[0] ?? null
}

function ArtifactVisual({
  sprite,
  slug,
}: {
  sprite: AssetSpriteDescriptor | null
  slug: string
}) {
  if (!sprite?.url) return null
  const src = backendUrl(sprite.url)
  if (sprite.frame_count <= 1 || sprite.url.toLowerCase().endsWith('.svg')) {
    return <img src={src} alt="" draggable={false} />
  }
  const animation: SpriteAnimation = {
    name: `${slug}.artifact`,
    src,
    frameWidth: sprite.frame_width || 1,
    frameHeight: sprite.frame_height || 1,
    columns: sprite.columns || 1,
    rows: sprite.rows || 1,
    frameCount: sprite.frame_count || 1,
    fps: sprite.fps || 12,
    loop: sprite.loops ?? true,
  }
  return <SpriteAnimator animation={animation} autoPlay scale={1} aria-label={slug} />
}
