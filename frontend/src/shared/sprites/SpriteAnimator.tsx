import { forwardRef, useCallback, useEffect, useImperativeHandle, useRef, useState } from 'react'

import { useSpritePixelAnchor } from '@/shared/sprites/usePixelBounds'
import { getWarmedImage, warmImage } from '@/shared/sprites/preload'
import { cn } from '@/shared/utils/cn'
import type { FrameSegment, SpriteAnimation, SpriteAnimatorHandle } from '@/shared/sprites/types'

function paintCanvasFrame(canvas: HTMLCanvasElement, animation: SpriteAnimation, frame: number) {
  const image = getWarmedImage(animation.src)
  if (!image) return
  const context = canvas.getContext('2d')
  if (!context) return

  if (canvas.width !== animation.frameWidth) canvas.width = animation.frameWidth
  if (canvas.height !== animation.frameHeight) canvas.height = animation.frameHeight
  const col = frame % animation.columns
  const row = Math.floor(frame / animation.columns)
  context.clearRect(0, 0, canvas.width, canvas.height)
  context.imageSmoothingEnabled = false
  context.drawImage(
    image,
    col * animation.frameWidth, row * animation.frameHeight,
    animation.frameWidth, animation.frameHeight,
    0, 0, canvas.width, canvas.height,
  )
}

/**
 * Zero-dependency spritesheet animator.
 *
 * Steps frames with requestAnimationFrame and crops them into a fixed canvas,
 * so transformed scenes never resample a moving atlas. No per-frame React
 * re-renders. Exposes an imperative handle (play/pause/setAnimation/setFlipX) so the character can
 * later be driven around the story map page.
 *
 * Honors `prefers-reduced-motion` by holding the first frame.
 */
export const SpriteAnimator = forwardRef<
  SpriteAnimatorHandle,
  {
    animation: SpriteAnimation
    /** Display scale relative to source frame size (1 = native pixels). */
    scale?: number
    /** Override the animation's default fps. */
    fps?: number
    /** Start playing on mount. */
    autoPlay?: boolean
    /** Initial horizontal facing (true = flipped / facing left). */
    flipX?: boolean
    /** Nearest-neighbour upscaling for chunky pixel art. */
    pixelated?: boolean
    /** Align visible alpha pixels, not the transparent frame canvas, to the layout anchor. */
    anchorToPixelBounds?: boolean
    /** Keep the rendered frame box stable while swapping animations. */
    layoutAnimation?: SpriteAnimation
    /** Keep the pixel anchor stable while swapping animations, e.g. monster poses keyed to idle feet. */
    pixelAnchorAnimation?: SpriteAnimation
    pixelAnchorFallback?: {
      bottomOffset?: number
      centerOffsetX?: number
    }
    className?: string
    'aria-label'?: string
  }
>(function SpriteAnimator(
  {
    animation,
    scale = 1,
    fps,
    autoPlay = true,
    flipX = false,
    pixelated = false,
    anchorToPixelBounds = false,
    layoutAnimation,
    pixelAnchorAnimation,
    pixelAnchorFallback,
    className,
    'aria-label': ariaLabel,
  },
  ref,
) {
  const spriteRef = useRef<HTMLCanvasElement>(null)
  const frameRef = useRef(0)
  const playingRef = useRef(autoPlay)
  const [anim, setAnim] = useState(animation)
  const [flipped, setFlipped] = useState(flipX)
  const animRef = useRef(anim)
  animRef.current = anim
  const fpsRef = useRef(fps)
  fpsRef.current = fps
  // Pending completion callback for the current non-looping animation.
  // Replaced (not fired) whenever a new animation is swapped in.
  const completeRef = useRef<(() => void) | null>(null)
  // Active frame range within the current sheet; null = whole sheet. Battle
  // one-shot phases (windup / hold-loop / release) are segments of one sheet.
  const segmentRef = useRef<FrameSegment | null>(null)
  const pixelAnchor = useSpritePixelAnchor(anchorToPixelBounds ? (pixelAnchorAnimation ?? anim) : null)

  // Keep internal animation in sync when the prop changes.
  useEffect(() => {
    setAnim(animation)
    frameRef.current = 0
    segmentRef.current = null
    completeRef.current = null
    // A completed one-shot pauses playback. Each new prop-driven pose must
    // start again, just like an imperative setAnimation call does.
    playingRef.current = autoPlay
  }, [animation, autoPlay])

  function clampSegment(segment: FrameSegment, frameCount: number): FrameSegment {
    const to = Math.max(0, Math.min(frameCount - 1, segment.to))
    const from = Math.max(0, Math.min(to, segment.from))
    return { from, to, loop: segment.loop }
  }

  useEffect(() => {
    setFlipped(flipX)
  }, [flipX])

  const paintFrame = useCallback((frame: number) => {
    const node = spriteRef.current
    if (!node) return
    paintCanvasFrame(node, animRef.current, frame)
  }, [])

  function paintAnimation(a: SpriteAnimation, frame: number) {
    const node = spriteRef.current
    if (!node) return
    // Source, dimensions and pixels change together, before React commits.
    paintCanvasFrame(node, a, frame)
  }

  useEffect(() => {
    let active = true
    void warmImage(anim.src).then(() => {
      // A slower sheet must never paint over a newer pose or an unmounted actor.
      if (active && animRef.current.src === anim.src) paintFrame(frameRef.current)
    })
    return () => { active = false }
  }, [anim, paintFrame])

  useImperativeHandle(ref, () => ({
    play: () => {
      playingRef.current = true
    },
    pause: () => {
      playingRef.current = false
    },
    isPlaying: () => playingRef.current,
    goToFrame: (frame: number) => {
      frameRef.current = Math.max(0, Math.min(animRef.current.frameCount - 1, frame))
      paintFrame(frameRef.current)
    },
    getFrame: () => frameRef.current,
    setAnimation: (next: SpriteAnimation, opts?: { onComplete?: () => void; segment?: FrameSegment }) => {
      completeRef.current = opts?.onComplete ?? null
      const segment = opts?.segment ? clampSegment(opts.segment, next.frameCount) : null
      segmentRef.current = segment
      frameRef.current = segment?.from ?? 0
      playingRef.current = true
      animRef.current = next
      paintAnimation(next, frameRef.current)
      setAnim(next)
    },
    playSegment: (segment: FrameSegment, opts?: { onComplete?: () => void }) => {
      completeRef.current = opts?.onComplete ?? null
      const clamped = clampSegment(segment, animRef.current.frameCount)
      segmentRef.current = clamped
      frameRef.current = clamped.from
      playingRef.current = true
      paintFrame(clamped.from)
    },
    setFlipX: (next: boolean) => {
      setFlipped(next)
    },
  }))

  // The rAF frame-stepper. One loop per mounted animator; advances by
  // elapsed time so dropped frames never slow the walk cycle down.
  useEffect(() => {
    const media = window.matchMedia?.('(prefers-reduced-motion: reduce)')
    let rafId = 0
    let lastTick = performance.now()
    paintFrame(frameRef.current)
    const step = (now: number) => {
      const a = animRef.current
      const interval = 1000 / (fpsRef.current ?? a.fps)
      if (playingRef.current && now - lastTick >= interval) {
        lastTick = now - ((now - lastTick) % interval)
        const segment = segmentRef.current
        const end = segment ? segment.to + 1 : a.frameCount
        const loop = segment ? Boolean(segment.loop) : a.loop
        const start = segment ? segment.from : 0
        const next = frameRef.current + 1
        if (next >= end) {
          if (loop) {
            frameRef.current = start
            paintFrame(start)
          } else {
            playingRef.current = false
            const onComplete = completeRef.current
            completeRef.current = null
            onComplete?.()
          }
        } else {
          frameRef.current = next
          paintFrame(next)
        }
      }
      rafId = requestAnimationFrame(step)
    }
    const syncMotion = () => {
      cancelAnimationFrame(rafId)
      if (media?.matches) {
        frameRef.current = segmentRef.current?.from ?? 0
        paintFrame(frameRef.current)
      } else {
        lastTick = performance.now()
        rafId = requestAnimationFrame(step)
      }
    }
    media?.addEventListener('change', syncMotion)
    syncMotion()
    return () => {
      cancelAnimationFrame(rafId)
      media?.removeEventListener('change', syncMotion)
    }
  }, [anim, paintFrame])

  const displayScale = anim.displayScale ?? 1
  const layout = layoutAnimation ?? anim
  const layoutDisplayScale = layout.displayScale ?? 1
  const anchorSource = pixelAnchorAnimation ?? anim
  const anchorScale = (anchorSource.displayScale ?? displayScale) * scale
  const rawAnchorOffsetX = anchorToPixelBounds
    ? (pixelAnchor?.centerOffsetX ?? pixelAnchorFallback?.centerOffsetX ?? 0) * anchorScale
    : 0
  const anchorOffsetX = flipped ? -rawAnchorOffsetX : rawAnchorOffsetX
  const anchorOffsetY =
    anchorToPixelBounds ? (pixelAnchor?.bottomOffset ?? pixelAnchorFallback?.bottomOffset ?? 0) * anchorScale : 0
  const transforms = [
    anchorOffsetX || anchorOffsetY ? `translate(${anchorOffsetX}px, ${anchorOffsetY}px)` : '',
    flipped ? 'scaleX(-1)' : '',
  ].filter(Boolean)

  return (
    <div
      role="img"
      aria-label={ariaLabel ?? 'Animated character'}
      className={cn('pointer-events-none select-none', className)}
      style={{
        width: layout.frameWidth * layoutDisplayScale * scale,
        height: layout.frameHeight * layoutDisplayScale * scale,
        transform: transforms.length ? transforms.join(' ') : undefined,
      }}
    >
      <canvas
        ref={spriteRef}
        aria-hidden="true"
        style={{
          display: 'block',
          width: '100%',
          height: '100%',
          imageRendering: pixelated ? 'pixelated' : 'auto',
        }}
      />
    </div>
  )
})
