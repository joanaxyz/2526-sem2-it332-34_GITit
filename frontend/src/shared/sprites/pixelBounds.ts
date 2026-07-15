import type { SpriteAnimation } from '@/shared/sprites/types'

export type PixelBounds = {
  left: number
  top: number
  right: number
  bottom: number
  width: number
  height: number
  alphaPixels: number
}

export type SpritePixelAnchor = {
  bounds: PixelBounds
  frameBounds: Array<PixelBounds | null>
  bottomOffset: number
  centerOffsetX: number
}

export type ImagePixelBounds = PixelBounds & {
  naturalWidth: number
  naturalHeight: number
  centerX: number
  centerY: number
  bottomOffset: number
  centerOffsetX: number
}

const DEFAULT_ALPHA_THRESHOLD = 8

export function scanAlphaRegion({
  data,
  sheetWidth,
  sourceX = 0,
  sourceY = 0,
  width,
  height,
  alphaThreshold = DEFAULT_ALPHA_THRESHOLD,
}: {
  data: ArrayLike<number>
  sheetWidth: number
  sourceX?: number
  sourceY?: number
  width: number
  height: number
  alphaThreshold?: number
}): PixelBounds | null {
  let left = width
  let top = height
  let right = -1
  let bottom = -1
  let alphaPixels = 0

  for (let y = 0; y < height; y += 1) {
    const row = sourceY + y
    for (let x = 0; x < width; x += 1) {
      const col = sourceX + x
      const alphaIndex = (row * sheetWidth + col) * 4 + 3
      if ((data[alphaIndex] ?? 0) <= alphaThreshold) continue

      if (x < left) left = x
      if (x > right) right = x
      if (y < top) top = y
      if (y > bottom) bottom = y
      alphaPixels += 1
    }
  }

  if (right < 0 || bottom < 0) return null

  return {
    left,
    top,
    right,
    bottom,
    width: right - left + 1,
    height: bottom - top + 1,
    alphaPixels,
  }
}

export function measureImagePixelBounds(
  data: ArrayLike<number>,
  naturalWidth: number,
  naturalHeight: number,
  alphaThreshold = DEFAULT_ALPHA_THRESHOLD,
): ImagePixelBounds | null {
  const bounds = scanAlphaRegion({
    data,
    sheetWidth: naturalWidth,
    width: naturalWidth,
    height: naturalHeight,
    alphaThreshold,
  })

  if (!bounds) return null

  const centerX = (bounds.left + bounds.right + 1) / 2
  const centerY = (bounds.top + bounds.bottom + 1) / 2

  return {
    ...bounds,
    naturalWidth,
    naturalHeight,
    centerX,
    centerY,
    bottomOffset: naturalHeight - 1 - bounds.bottom,
    centerOffsetX: naturalWidth / 2 - centerX,
  }
}

export function measureSpritePixelAnchor(
  data: ArrayLike<number>,
  sheetWidth: number,
  animation: Pick<SpriteAnimation, 'frameWidth' | 'frameHeight' | 'columns' | 'frameCount'>,
  alphaThreshold = DEFAULT_ALPHA_THRESHOLD,
): SpritePixelAnchor | null {
  const frameBounds: Array<PixelBounds | null> = []

  for (let frame = 0; frame < animation.frameCount; frame += 1) {
    const col = frame % animation.columns
    const row = Math.floor(frame / animation.columns)
    frameBounds.push(
      scanAlphaRegion({
        data,
        sheetWidth,
        sourceX: col * animation.frameWidth,
        sourceY: row * animation.frameHeight,
        width: animation.frameWidth,
        height: animation.frameHeight,
        alphaThreshold,
      }),
    )
  }

  const visibleFrames = frameBounds.filter((bounds): bounds is PixelBounds => Boolean(bounds))
  if (!visibleFrames.length) return null

  const bounds = visibleFrames.reduce<PixelBounds>(
    (acc, frame) => ({
      left: Math.min(acc.left, frame.left),
      top: Math.min(acc.top, frame.top),
      right: Math.max(acc.right, frame.right),
      bottom: Math.max(acc.bottom, frame.bottom),
      width: 0,
      height: 0,
      alphaPixels: acc.alphaPixels + frame.alphaPixels,
    }),
    {
      left: animation.frameWidth,
      top: animation.frameHeight,
      right: -1,
      bottom: -1,
      width: 0,
      height: 0,
      alphaPixels: 0,
    },
  )

  bounds.width = bounds.right - bounds.left + 1
  bounds.height = bounds.bottom - bounds.top + 1

  const visibleCenterX = (bounds.left + bounds.right + 1) / 2

  return {
    bounds,
    frameBounds,
    bottomOffset: animation.frameHeight - 1 - bounds.bottom,
    centerOffsetX: animation.frameWidth / 2 - visibleCenterX,
  }
}
