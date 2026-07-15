import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react'

import { useSpritePixelAnchor } from '@/shared/sprites/usePixelBounds'
import { cn } from '@/shared/utils/cn'
import type { FrameSegment, SpriteAnimation, SpriteAnimatorHandle } from '@/shared/sprites/types'

/**
 * Zero-dependency spritesheet animator.
 *
 * Steps frames with requestAnimationFrame and paints them by shifting the
 * sheet's background-position - no per-frame React re-renders. Exposes an
 * imperative handle (play/pause/setAnimation/setFlipX) so the character can
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
  const spriteRef = useRef<HTMLDivElement>(null)
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
  }, [animation])

  function clampSegment(segment: FrameSegment, frameCount: number): FrameSegment {
    const to = Math.max(0, Math.min(frameCount - 1, segment.to))
    const from = Math.max(0, Math.min(to, segment.from))
    return { from, to, loop: segment.loop }
  }

  useEffect(() => {
    setFlipped(flipX)
  }, [flipX])

  function paintFrame(frame: number) {
    const node = spriteRef.current
    const a = animRef.current
    if (!node) return
    // Percentage positioning: p% aligns the p% point of the oversized sheet
    // with the p% point of the frame box, so column c maps to c/(cols-1)-100%.
    const col = frame % a.columns
    const row = Math.floor(frame / a.columns)
    const x = a.columns > 1 ? (col * 100) / (a.columns - 1) : 0
    const y = a.rows > 1 ? (row * 100) / (a.rows - 1) : 0
    node.style.backgroundPosition = `${x}% ${y}%`
  }

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
      paintFrame(frameRef.current)
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
    if (typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      paintFrame(0)
      return
    }
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
    rafId = requestAnimationFrame(step)
    return () => cancelAnimationFrame(rafId)
  }, [anim])

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
      <div
        ref={spriteRef}
        style={{
          width: '100%',
          height: '100%',
          backgroundImage: `url(${anim.src})`,
          backgroundRepeat: 'no-repeat',
          backgroundSize: `${anim.columns * 100}% ${anim.rows * 100}%`,
          backgroundPosition: '0% 0%',
          imageRendering: pixelated ? 'pixelated' : 'auto',
        }}
      />
    </div>
  )
})
