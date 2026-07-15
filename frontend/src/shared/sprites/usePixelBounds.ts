import { useEffect, useMemo, useState } from 'react'

import {
  measureImagePixelBounds,
  measureSpritePixelAnchor,
  type ImagePixelBounds,
  type SpritePixelAnchor,
} from '@/shared/sprites/pixelBounds'
import type { SpriteAnimation } from '@/shared/sprites/types'

const spriteAnchorCache = new Map<string, SpritePixelAnchor | null>()
const spriteAnchorPromises = new Map<string, Promise<SpritePixelAnchor | null>>()
const imageBoundsCache = new Map<string, ImagePixelBounds | null>()
const imageBoundsPromises = new Map<string, Promise<ImagePixelBounds | null>>()

const DEFAULT_ALPHA_THRESHOLD = 8

function animationKey(animation: SpriteAnimation, alphaThreshold: number): string {
  return [
    animation.src,
    animation.frameWidth,
    animation.frameHeight,
    animation.columns,
    animation.rows,
    animation.frameCount,
    alphaThreshold,
  ].join('|')
}

async function loadImage(src: string): Promise<HTMLImageElement> {
  const image = new Image()
  image.decoding = 'async'
  image.src = src

  if (typeof image.decode === 'function') {
    await image.decode()
    return image
  }

  if (image.complete && image.naturalWidth > 0) return image

  await new Promise<void>((resolve, reject) => {
    image.onload = () => resolve()
    image.onerror = () => reject(new Error(`Could not read pixels for ${src}`))
  })

  return image
}

function imageDataFor(image: HTMLImageElement): ImageData | null {
  const width = image.naturalWidth
  const height = image.naturalHeight
  if (!width || !height) return null

  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const ctx = canvas.getContext('2d', { willReadFrequently: true })
  if (!ctx) return null

  ctx.drawImage(image, 0, 0)
  return ctx.getImageData(0, 0, width, height)
}

export function loadSpritePixelAnchor(
  animation: SpriteAnimation,
  alphaThreshold = DEFAULT_ALPHA_THRESHOLD,
): Promise<SpritePixelAnchor | null> {
  const key = animationKey(animation, alphaThreshold)
  if (spriteAnchorCache.has(key)) return Promise.resolve(spriteAnchorCache.get(key) ?? null)

  const cachedPromise = spriteAnchorPromises.get(key)
  if (cachedPromise) return cachedPromise

  const promise = loadImage(animation.src)
    .then((image) => {
      const imageData = imageDataFor(image)
      const anchor = imageData ? measureSpritePixelAnchor(imageData.data, imageData.width, animation, alphaThreshold) : null
      spriteAnchorCache.set(key, anchor)
      return anchor
    })
    .catch(() => {
      spriteAnchorCache.set(key, null)
      return null
    })
    .finally(() => {
      spriteAnchorPromises.delete(key)
    })

  spriteAnchorPromises.set(key, promise)
  return promise
}

export function loadImagePixelBounds(src: string, alphaThreshold = DEFAULT_ALPHA_THRESHOLD): Promise<ImagePixelBounds | null> {
  const key = `${src}|${alphaThreshold}`
  if (imageBoundsCache.has(key)) return Promise.resolve(imageBoundsCache.get(key) ?? null)

  const cachedPromise = imageBoundsPromises.get(key)
  if (cachedPromise) return cachedPromise

  const promise = loadImage(src)
    .then((image) => {
      const imageData = imageDataFor(image)
      const bounds = imageData
        ? measureImagePixelBounds(imageData.data, imageData.width, imageData.height, alphaThreshold)
        : null
      imageBoundsCache.set(key, bounds)
      return bounds
    })
    .catch(() => {
      imageBoundsCache.set(key, null)
      return null
    })
    .finally(() => {
      imageBoundsPromises.delete(key)
    })

  imageBoundsPromises.set(key, promise)
  return promise
}

export function useSpritePixelAnchor(
  animation: SpriteAnimation | null | undefined,
  alphaThreshold = DEFAULT_ALPHA_THRESHOLD,
): SpritePixelAnchor | null {
  const key = useMemo(() => (animation ? animationKey(animation, alphaThreshold) : null), [animation, alphaThreshold])
  const [anchor, setAnchor] = useState<SpritePixelAnchor | null>(() =>
    key ? (spriteAnchorCache.get(key) ?? null) : null,
  )

  useEffect(() => {
    if (!animation || !key || typeof document === 'undefined') {
      setAnchor(null)
      return undefined
    }

    let active = true
    setAnchor(spriteAnchorCache.get(key) ?? null)
    void loadSpritePixelAnchor(animation, alphaThreshold).then((next) => {
      if (active) setAnchor(next)
    })

    return () => {
      active = false
    }
  }, [animation, alphaThreshold, key])

  return anchor
}

export function useImagePixelBounds(src: string | null | undefined, alphaThreshold = DEFAULT_ALPHA_THRESHOLD) {
  const key = src ? `${src}|${alphaThreshold}` : null
  const [bounds, setBounds] = useState<ImagePixelBounds | null>(() =>
    key ? (imageBoundsCache.get(key) ?? null) : null,
  )

  useEffect(() => {
    if (!src || !key || typeof document === 'undefined') {
      setBounds(null)
      return undefined
    }

    let active = true
    setBounds(imageBoundsCache.get(key) ?? null)
    void loadImagePixelBounds(src, alphaThreshold).then((next) => {
      if (active) setBounds(next)
    })

    return () => {
      active = false
    }
  }, [src, alphaThreshold, key])

  return bounds
}
