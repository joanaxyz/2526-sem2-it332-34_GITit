import { useEffect, useRef, useState } from 'react'
import { MascotSprite, type MascotPose } from './MascotSprite'
import { mascotPlatforms, mascotTilt, platformNear } from './mascotPlatforms'
import { warmImages } from '@/shared/sprites/preload'
import './mascot.css'

type Point = { x: number; y: number }
type Phase = 'rest' | 'ground' | 'takeoff' | 'flight' | 'landing'

/** A persistent character whose feet follow the real tops of page containers. */
export function WorldMascot({ surface }: { surface: 'home' | 'track' }) {
  const hostRef = useRef<HTMLDivElement>(null)
  const actorRef = useRef<HTMLButtonElement>(null)
  const artRef = useRef<HTMLSpanElement>(null)
  const commandRef = useRef<((x: number, y: number) => void) | null>(null)
  const [pose, setPose] = useState<MascotPose>('float')
  const [flip, setFlip] = useState(false)

  useEffect(() => {
    const host = hostRef.current
    const parent = host?.parentElement
    const actor = actorRef.current
    if (!host || !parent || !actor) return
    void warmImages(['idle', 'float', 'fly', 'walk', 'run', 'land', 'take-off'].map((name) => `/mascot/${name}.png`))
    const media = window.matchMedia?.('(prefers-reduced-motion: reduce)')
    let reduced = media?.matches ?? false
    let currentPose: MascotPose = 'float'
    let phase: Phase = 'rest'
    let phaseSince = 0
    let point: Point = { x: 85, y: 190 }
    let destination = { ...point }
    let grounded: HTMLElement | null = null
    let landingOn: HTMLElement | null = null
    let sprinting = false
    let rotation = 0
    let frame = 0
    let last = 0
    let placed = false

    function changePose(next: MascotPose) {
      if (currentPose !== next) { currentPose = next; setPose(next) }
    }
    function paint() {
      actor!.style.transform = `translate(${point.x}px, ${point.y}px) translate(-50%, -100%)`
      if (artRef.current) artRef.current.style.transform = `rotate(${reduced ? 0 : rotation}deg)`
    }
    function visibleBounds() {
      const bounds = host!.getBoundingClientRect()
      return { bounds, top: Math.max(135, bounds.top + 115) - bounds.top,
        bottom: Math.min(innerHeight - 45, bounds.bottom - 25) - bounds.top }
    }
    function keepVisible() {
      const { bounds, top, bottom } = visibleBounds()
      if (bottom < top || bounds.width < 120) return
      if (!placed) {
        point = { x: Math.max(45, bounds.width - 100), y: surface === 'home' ? bottom - 40 : (top + bottom) / 2 }
        destination = { ...point }
        placed = true
      } else if (point.y < top || point.y > bottom || point.x > bounds.width - 35) {
        point = { x: Math.max(35, Math.min(bounds.width - 35, point.x)), y: Math.max(top, Math.min(bottom, point.y)) }
        destination = { ...point }
        grounded = landingOn = null
        phase = 'rest'
        rotation = 0
        changePose('float')
      }
      paint()
    }
    function command(x: number, y: number) {
      const { bounds, top, bottom } = visibleBounds()
      const platform = platformNear(mascotPlatforms(parent!, bounds), x, y)
      landingOn = platform?.element ?? null
      destination = {
        x: platform ? Math.max(platform.left + 18, Math.min(platform.right - 18, x)) : Math.max(40, Math.min(bounds.width - 40, x)),
        y: platform ? platform.y : Math.max(top, Math.min(bottom, y)),
      }
      setFlip(destination.x < point.x)
      rotation = 0
      phaseSince = performance.now()
      if (reduced) {
        point = { ...destination }; grounded = landingOn; phase = 'rest'
        changePose(grounded ? 'idle' : 'float'); paint(); return
      }
      if (grounded && grounded === landingOn) {
        phase = 'ground'; sprinting = Math.abs(destination.x - point.x) > 180
        changePose(sprinting ? 'run' : 'walk')
      } else if (grounded) {
        grounded = null; phase = 'takeoff'; changePose('take-off')
      } else { phase = 'flight'; changePose('fly') }
    }
    commandRef.current = command
    function move(event: PointerEvent) {
      const target = event.target
      if (!(target instanceof Element) || target.closest('.world-mascot, input, textarea, select, [role="dialog"]') || !parent!.contains(target)) return
      const bounds = host!.getBoundingClientRect()
      command(event.clientX - bounds.left, event.clientY - bounds.top)
    }
    function tick(now: number) {
      const dt = last ? Math.min((now - last) / 1000, 0.04) : 0
      last = now
      if (!document.hidden) {
        const bounds = host!.getBoundingClientRect()
        if (grounded) {
          const edge = grounded.getBoundingClientRect()
          if (!grounded.isConnected || edge.width < 1) {
            grounded = null; phase = 'rest'; changePose('float')
          } else point.y = edge.top - bounds.top
        }
        if (landingOn && (phase === 'flight' || phase === 'ground' || phase === 'landing')) {
          const edge = landingOn.getBoundingClientRect()
          if (!landingOn.isConnected || edge.width < 1) {
            landingOn = grounded = null; phase = 'rest'; changePose('float')
          } else {
            destination.y = edge.top - bounds.top
            destination.x = Math.max(edge.left - bounds.left + 20, Math.min(edge.right - bounds.left - 20, destination.x))
          }
        }
        if (phase === 'takeoff') {
          rotation += (-12 - rotation) * Math.min(1, dt * 8)
          if (now - phaseSince > 1000) point.y -= dt * 60
          if (now - phaseSince >= 1350) { phase = 'flight'; changePose('fly') }
        } else if (phase === 'flight' || phase === 'ground') {
          const dx = destination.x - point.x
          const dy = phase === 'ground' ? 0 : destination.y - point.y
          const distance = Math.hypot(dx, dy)
          const step = Math.min(distance, (phase === 'ground' ? sprinting ? 230 : 95 : 430) * dt)
          if (distance > 1) { point.x += dx / distance * step; point.y += dy / distance * step }
          rotation += ((phase === 'flight' ? mascotTilt(dx, dy) : 0) - rotation) * Math.min(1, dt * 9)
          if (distance <= 2) {
            point = { ...destination }; rotation = 0
            if (phase === 'ground') { phase = 'rest'; changePose('idle') }
            else if (landingOn) { phase = 'landing'; phaseSince = now; changePose('land') }
            else { phase = 'rest'; changePose('float') }
          }
        } else if (phase === 'landing') {
          point = { ...destination }
          if (now - phaseSince >= 1350) { grounded = landingOn; phase = 'rest'; changePose('idle') }
        }
        paint()
      }
      frame = requestAnimationFrame(tick)
    }
    const syncMotion = () => {
      reduced = media?.matches ?? false
      rotation = 0
      if (reduced) {
        point = { ...destination }
        grounded = landingOn
        phase = 'rest'
        changePose(grounded ? 'idle' : 'float')
        paint()
      }
    }
    media?.addEventListener('change', syncMotion)
    document.addEventListener('pointerup', move)
    window.addEventListener('scroll', keepVisible, true)
    window.addEventListener('resize', keepVisible)
    const observer = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(keepVisible)
    observer?.observe(parent)
    keepVisible()
    frame = requestAnimationFrame(tick)
    return () => {
      commandRef.current = null
      cancelAnimationFrame(frame)
      media?.removeEventListener('change', syncMotion)
      document.removeEventListener('pointerup', move)
      window.removeEventListener('scroll', keepVisible, true)
      window.removeEventListener('resize', keepVisible)
      observer?.disconnect()
    }
  }, [surface])

  return <div ref={hostRef} className="world-mascot" data-surface={surface}>
    <button ref={actorRef} type="button" className="world-mascot-actor" data-pose={pose}
      aria-label="Git-It mascot. Click a container edge to land, or open space to fly."
      title="Click a container edge to land · Nearby clicks walk · Distant clicks run"
      onClick={() => {
        const actor = actorRef.current
        const host = hostRef.current
        if (actor && host) {
          const bounds = host.getBoundingClientRect()
          const current = actor.getBoundingClientRect()
          commandRef.current?.(current.left + current.width / 2 - bounds.left + 90, current.bottom - bounds.top - 90)
        }
      }}>
      <span ref={artRef} className="world-mascot-art"><MascotSprite pose={pose} size={144} flip={flip} /></span>
    </button>
  </div>
}
