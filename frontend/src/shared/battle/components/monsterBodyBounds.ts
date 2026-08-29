export type MonsterBodyBounds = {
  left: number
  top: number
  right: number
  bottom: number
  width: number
  height: number
}

/** Project source-frame alpha bounds into a rendered (and optionally flipped) sprite box. */
export function projectMonsterBodyBounds(
  frameBox: Pick<DOMRect, 'left' | 'top' | 'width' | 'height'>,
  frameSize: { width: number; height: number },
  pixelBounds: { left: number; top: number; right: number; bottom: number },
  flipped: boolean,
): MonsterBodyBounds | null {
  if (frameSize.width <= 0 || frameSize.height <= 0 || frameBox.width <= 0 || frameBox.height <= 0) return null

  const scaleX = frameBox.width / frameSize.width
  const scaleY = frameBox.height / frameSize.height
  const sourceLeft = pixelBounds.left * scaleX
  const sourceRight = (pixelBounds.right + 1) * scaleX
  const left = flipped ? frameBox.left + frameBox.width - sourceRight : frameBox.left + sourceLeft
  const right = flipped ? frameBox.left + frameBox.width - sourceLeft : frameBox.left + sourceRight
  const top = frameBox.top + pixelBounds.top * scaleY
  const bottom = frameBox.top + (pixelBounds.bottom + 1) * scaleY

  return { left, top, right, bottom, width: right - left, height: bottom - top }
}
