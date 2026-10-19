import { useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { MascotSprite, type MascotPose } from './MascotSprite'
import { mascotPerch, mascotPlatform, mascotPlatforms, mascotTilt, platformNear, type MascotPlatform } from './mascotPlatforms'
import { warmImages } from '@/shared/sprites/preload'
import { MascotKnowledgeBubble } from './MascotKnowledgeBubble'
import { INTRODUCTORY_TIPS, mascotSpeechPosition, type MascotKnowledgeTip } from './mascotKnowledge'
import './mascot.css'

type Point = { x: number; y: number }
type Phase = 'rest' | 'ground' | 'takeoff' | 'flight' | 'landing'
type Attachment = { element: HTMLElement; ratio: number }

/** A persistent character whose feet follow the real tops of page containers. */
export function WorldMascot({ surface, knowledge = [], contextKey = surface }: {
  surface: 'home' | 'track'
  knowledge?: readonly MascotKnowledgeTip[]
  contextKey?: string
}) {
  const scopeRef = useRef<HTMLSpanElement>(null)
  const hostRef = useRef<HTMLDivElement>(null)
  const actorRef = useRef<HTMLButtonElement>(null)
  const artRef = useRef<HTMLSpanElement>(null)
  const bubbleRef = useRef<HTMLDivElement>(null)
  const paintRef = useRef<(() => void) | null>(null)
  const bubbleId = useId()
  const [speech, setSpeech] = useState<{ context: string; id: string | null; open: boolean }>({ context: contextKey, id: null, open: false })
  const tips = knowledge.length ? knowledge : INTRODUCTORY_TIPS
  const selectedTip = speech.context === contextKey
    ? tips.find((entry) => entry.id === speech.id) ?? INTRODUCTORY_TIPS.find((entry) => entry.id === speech.id)
    : undefined
  const tip = speech.open ? selectedTip : undefined
  if (speech.context !== contextKey || (speech.id != null && !selectedTip)) {
    setSpeech({ context: contextKey, id: null, open: false })
  }
  const nextTip = () => {
    const index = selectedTip ? tips.findIndex((entry) => entry.id === selectedTip.id) : -1
    setSpeech({ context: contextKey, id: tips[(index + 1) % tips.length].id, open: true })
  }
  const dismissTip = useCallback((restoreFocus = false) => {
    setSpeech((current) => ({ ...current, open: false }))
    if (restoreFocus) actorRef.current?.focus({ preventScroll: true })
  }, [])
  const [pose, setPose] = useState<MascotPose>('float')
  const [flip, setFlip] = useState(false)

  useLayoutEffect(() => { paintRef.current?.() }, [tip])

  useEffect(() => {
    const host = hostRef.current
    const parent = scopeRef.current?.parentElement
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
    let grounded: Attachment | null = null
    let landingOn: Attachment | null = null
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
      // Topmost ledges have less headroom than the sprite's natural height.
      const scale = Math.min(1, Math.max(0.6, (point.y - 8) / 90))
      if (artRef.current) artRef.current.style.transform = `rotate(${reduced ? 0 : rotation}deg) scale(${scale})`
      const bubble = bubbleRef.current
      if (bubble) {
        const { bounds } = visibleBounds()
        const position = mascotSpeechPosition(point.x, point.y, bubble.offsetWidth, bubble.offsetHeight, bounds.width, bounds.height)
        bubble.style.left = `${position.left}px`
        bubble.style.top = `${position.top}px`
        bubble.style.setProperty('--mascot-tail-x', `${bounds.left + position.left + position.tail}px`)
        bubble.style.setProperty('--mascot-tail-y', `${bounds.top + position.top + (position.below ? 0 : bubble.offsetHeight)}px`)
        bubble.toggleAttribute('data-below', position.below)
      }
    }
    paintRef.current = paint
    function visibleBounds() {
      const bounds = host!.getBoundingClientRect()
      return { bounds, top: 110, bottom: Math.max(110, bounds.height - 30) }
    }
    function attachedPoint(attachment: Attachment): Point | null {
      const { element, ratio } = attachment
      const bounds = host!.getBoundingClientRect()
      const edge = element.getBoundingClientRect()
      if (!element.isConnected || edge.width < 1 || edge.top < 65 || edge.top > bounds.height - 35 ||
        element.closest('[hidden], [inert], [aria-hidden="true"]')) return null
      return { x: Math.max(40, Math.min(bounds.width - 40, edge.left - bounds.left + edge.width * ratio)), y: edge.top - bounds.top }
    }
    function keepVisible() {
      const { bounds, top, bottom } = visibleBounds()
      if ((grounded && !mascotPlatform(grounded.element, parent!, bounds)) ||
        (landingOn && !mascotPlatform(landingOn.element, parent!, bounds))) {
        grounded = landingOn = null
        phase = 'rest'
        rotation = 0
        changePose('float')
      }
      const anchor = grounded && phase === 'rest' ? attachedPoint(grounded) : null
      if (bottom < top || bounds.width < 120) { paint(); return }
      if (!placed) {
        point = { x: Math.max(45, bounds.width - 100), y: surface === 'home' ? bottom - 40 : (top + bottom) / 2 }
        destination = { ...point }
        placed = true
      } else if (anchor) {
        point = anchor
      } else if (point.y < top || point.y > bottom || point.x < 35 || point.x > bounds.width - 35) {
        point = { x: Math.max(35, Math.min(bounds.width - 35, point.x)), y: Math.max(top, Math.min(bottom, point.y)) }
        destination = { ...point }
        grounded = landingOn = null
        phase = 'rest'
        rotation = 0
        changePose('float')
      }
      paint()
    }
    function command(x: number, y: number, perch?: MascotPlatform | null) {
      const { bounds, top, bottom } = visibleBounds()
      const platform = perch ?? platformNear(mascotPlatforms(parent!, bounds), x, y)
      destination = {
        x: perch ? (perch.left + perch.right) / 2 : platform ? Math.max(platform.left + 18, Math.min(platform.right - 18, x)) : Math.max(40, Math.min(bounds.width - 40, x)),
        y: platform ? platform.y : Math.max(top, Math.min(bottom, y)),
      }
      const edge = platform?.element.getBoundingClientRect()
      landingOn = platform && edge ? { element: platform.element, ratio: (destination.x + bounds.left - edge.left) / edge.width } : null
      setFlip(destination.x < point.x)
      rotation = 0
      phaseSince = performance.now()
      if (reduced) {
        point = { ...destination }; grounded = landingOn; phase = 'rest'
        changePose(grounded ? 'idle' : 'float'); paint(); return
      }
      if (grounded && grounded.element === landingOn?.element) {
        phase = 'ground'; sprinting = Math.abs(destination.x - point.x) > 180
        changePose(sprinting ? 'run' : 'walk')
      } else if (grounded) {
        grounded = null; phase = 'takeoff'; changePose('take-off')
      } else { phase = 'flight'; changePose('fly') }
    }
    function move(event: PointerEvent | MouseEvent) {
      const target = event.target
      if (event.button !== 0 || !(target instanceof Element) || target.closest('.world-mascot, input, textarea, select, [role="dialog"]') || !parent!.contains(target)) return
      const bounds = host!.getBoundingClientRect()
      const perch = mascotPerch(mascotPlatforms(parent!, bounds), target)
      command(event.clientX - bounds.left, event.clientY - bounds.top, perch)
    }
    function activateNode(event: MouseEvent) {
      if (event.detail === 0 && event.target instanceof Element && event.target.closest('[data-mascot-perch]')) move(event)
    }
    function tick(now: number) {
      const dt = last ? Math.min((now - last) / 1000, 0.04) : 0
      last = now
      if (!document.hidden) {
        if (grounded) {
          const anchor = attachedPoint(grounded)
          if (!anchor) {
            grounded = null; phase = 'rest'; changePose('float')
            keepVisible()
          } else {
            point.y = anchor.y
            if (phase === 'rest') point.x = anchor.x
          }
        }
        if (landingOn && phase !== 'rest') {
          const anchor = attachedPoint(landingOn)
          if (!anchor) {
            landingOn = grounded = null; phase = 'rest'; changePose('float')
            keepVisible()
          } else {
            destination = anchor
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
            if (phase === 'ground') { grounded = landingOn; phase = 'rest'; changePose('idle') }
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
    // Panel interactions must not swallow the mascot's page-wide movement.
    document.addEventListener('pointerup', move, true)
    document.addEventListener('click', activateNode, true)
    window.addEventListener('scroll', keepVisible, true)
    window.addEventListener('resize', keepVisible)
    const observer = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(keepVisible)
    observer?.observe(parent)
    keepVisible()
    frame = requestAnimationFrame(tick)
    return () => {
      paintRef.current = null
      cancelAnimationFrame(frame)
      media?.removeEventListener('change', syncMotion)
      document.removeEventListener('pointerup', move, true)
      document.removeEventListener('click', activateNode, true)
      window.removeEventListener('scroll', keepVisible, true)
      window.removeEventListener('resize', keepVisible)
      observer?.disconnect()
    }
  }, [surface])

  return <><span ref={scopeRef} hidden />{createPortal(<div ref={hostRef} className="world-mascot" data-surface={surface}>
    <button ref={actorRef} type="button" className="world-mascot-actor" data-pose={pose}
      aria-label="Git-It mascot: share a Git tip"
      aria-expanded={Boolean(tip)} aria-controls={tip ? bubbleId : undefined}
      title="Click for a tip from your learning journey · Click the page to move me"
      onClick={nextTip}>
      <span ref={artRef} className="world-mascot-art"><MascotSprite pose={pose} size={144} flip={flip} /></span>
    </button>
    {tip ? <MascotKnowledgeBubble id={bubbleId} tip={tip} bubbleRef={bubbleRef} onNext={nextTip} onDismiss={dismissTip} /> : null}
  </div>, document.body)}</>
}
