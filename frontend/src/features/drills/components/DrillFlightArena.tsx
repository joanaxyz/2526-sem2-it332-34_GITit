import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { Check, Heart, Pause, Play, X } from 'lucide-react'
import type { DrillChoice, DrillVerdict } from '@/features/drills/types'
import { MascotSprite, type MascotPose } from '@/shared/mascot/MascotSprite'
import { warmImages } from '@/shared/sprites/preload'

type Point = { x: number; y: number }

// Keep reading time consistent: one arena width every 28 seconds, even on phones.
const CHOICE_CROSSING_SECONDS = 28

export function DrillFlightArena({ options, verdict, lives, started, onStart, onCollide, onMiss, voice, round = 0, children, paused: pausedProp, onPauseChange, showHud = true }: {
  children?: ReactNode
  paused?: boolean
  onPauseChange?: (paused: boolean) => void
  showHud?: boolean
  round?: number
  options: DrillChoice[]
  verdict: DrillVerdict | null
  lives: number
  started: boolean
  onStart: () => void
  onCollide: (value: string) => void
  onMiss?: () => void
  voice: 'machine' | 'prose'
}) {
  const arenaRef = useRef<HTMLDivElement>(null)
  const questionRef = useRef<HTMLDivElement>(null)
  const playBounds = useRef({ top: 64, bottom: 36 })
  const actorRef = useRef<HTMLDivElement>(null)
  const tiltRef = useRef<HTMLDivElement>(null)
  const tilt = useRef(0)
  const choiceRefs = useRef<Array<HTMLButtonElement | null>>([])
  const position = useRef<Point>({ x: 0, y: 0 })
  const destination = useRef<Point>({ x: 0, y: 0 })
  const projectileX = useRef<number[]>([])
  const resolved = useRef(false)
  const initialized = useRef(false)
  const previousSize = useRef({ width: 0, height: 0 })
  const [localPaused, setLocalPaused] = useState(false)
  const paused = pausedProp ?? localPaused
  const setPaused = useCallback((next: boolean) => {
    setLocalPaused(next)
    onPauseChange?.(next)
  }, [onPauseChange])
  const [launching, setLaunching] = useState(false)
  const [reduced, setReduced] = useState(false)
  const flightActive = started && !paused && !launching && !verdict
  const laneY = useCallback((index: number, height: number) =>
    playBounds.current.top + (index + 0.5) * Math.max(0, height - playBounds.current.top - playBounds.current.bottom) / Math.max(1, options.length), [options.length])

  useEffect(() => {
    void warmImages(['idle', 'fly', 'float', 'take-off', 'die'].map((name) => `/mascot/${name}.png`))
  }, [])

  useLayoutEffect(() => {
    resolved.current = false
    const arena = arenaRef.current
    if (!arena) return
    projectileX.current = options.map((_, index) => round && !reduced ? arena.clientWidth * 1.12
      : Math.min(arena.clientWidth * 0.77, arena.clientWidth - (choiceRefs.current[index]?.offsetWidth ?? 0) / 2 - 16))
    choiceRefs.current.forEach((node, index) => {
      if (node) node.style.transform = `translate(${projectileX.current[index]}px, ${laneY(index, arena.clientHeight)}px) translate(-50%, -50%)`
    })
  }, [round, options, laneY, reduced])

  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)')
    const sync = () => setReduced(media.matches)
    sync()
    media.addEventListener('change', sync)
    const hide = () => { if (document.hidden && started) setPaused(true) }
    document.addEventListener('visibilitychange', hide)
    return () => {
      media.removeEventListener('change', sync)
      document.removeEventListener('visibilitychange', hide)
    }
  }, [setPaused, started])

  useEffect(() => {
    if (!launching) return
    const timer = setTimeout(() => setLaunching(false), reduced ? 0 : 1350)
    return () => clearTimeout(timer)
  }, [launching, reduced])

  useEffect(() => {
    if (!verdict && !reduced) return
    tilt.current = 0
    if (tiltRef.current) tiltRef.current.style.transform = 'rotate(0deg)'
  }, [verdict, reduced])

  useEffect(() => {
    const arena = arenaRef.current
    if (!arena) return
    function measure() {
      const width = arena!.clientWidth
      const height = arena!.clientHeight
      if (!width || !height) return
      const question = questionRef.current
      const bottomInset = height < 360 ? 24 : 56
      const questionGap = height < 360 ? 16 : 28
      playBounds.current = question ? {
        top: Math.max(64, Math.min(height - bottomInset, question.offsetTop + question.offsetHeight + questionGap)),
        bottom: bottomInset,
      } : { top: 64, bottom: 36 }
      arena!.style.setProperty('--drill-play-top', `${playBounds.current.top}px`)
      arena!.style.setProperty('--drill-play-bottom', `${playBounds.current.bottom}px`)
      if (!initialized.current) {
        position.current = { x: width * 0.15, y: started ? height * 0.5 : height - 94 }
        destination.current = { ...position.current }
        initialized.current = true
        projectileX.current = options.map(() => width * 0.77)
      } else if (previousSize.current.width && previousSize.current.height) {
        const sx = width / previousSize.current.width
        const sy = height / previousSize.current.height
        position.current = { x: position.current.x * sx, y: position.current.y * sy }
        destination.current = { x: destination.current.x * sx, y: destination.current.y * sy }
        projectileX.current = projectileX.current.map((x) => x * sx)
      }
      previousSize.current = { width, height }
      if (!started) position.current = { x: width * 0.15, y: height - 94 }
      position.current.x = Math.max(45, Math.min(width - 45, position.current.x))
      const minY = question ? playBounds.current.top : 76
      position.current.y = Math.max(minY, Math.min(height - 55, position.current.y))
      destination.current.x = Math.max(45, Math.min(width - 45, destination.current.x))
      destination.current.y = Math.max(minY, Math.min(height - 55, destination.current.y))
      actorRef.current!.style.transform = `translate(${position.current.x}px, ${position.current.y}px)`
      choiceRefs.current.forEach((node, index) => {
        if (node && reduced) projectileX.current[index] = Math.max(node.offsetWidth / 2 + 16, Math.min(width - node.offsetWidth / 2 - 16, projectileX.current[index]))
        if (node) node.style.transform = `translate(${projectileX.current[index]}px, ${laneY(index, height)}px) translate(-50%, -50%)`
      })
    }
    measure()
    const observer = new ResizeObserver(measure)
    observer.observe(arena)
    if (questionRef.current) observer.observe(questionRef.current)
    return () => observer.disconnect()
  }, [laneY, options, reduced, started])

  useEffect(() => {
    if (!flightActive || reduced || !options.length) return
    let frame = 0
    let last = 0
    function tick(time: number) {
      const arena = arenaRef.current
      if (!arena || resolved.current) return
      const dt = last ? Math.min((time - last) / 1000, 0.04) : 0
      last = time
      const { clientWidth: width, clientHeight: height } = arena
      const current = position.current
      const target = destination.current
      const distance = Math.hypot(target.x - current.x, target.y - current.y)
      const step = Math.min(distance, Math.max(width * 0.52, 260) * dt)
      const targetTilt = distance > 4 ? Math.max(-30, Math.min(30, Math.atan2(target.y - current.y, Math.max(100, Math.abs(target.x - current.x))) * 180 / Math.PI)) : 0
      tilt.current += (targetTilt - tilt.current) * Math.min(1, dt * 9)
      if (tiltRef.current) tiltRef.current.style.transform = `rotate(${tilt.current}deg)`
      if (distance > 1) {
        current.x += (target.x - current.x) / distance * step
        current.y += (target.y - current.y) / distance * step
      }
      actorRef.current!.style.transform = `translate(${current.x}px, ${current.y}px)`
      let allPassed = true
      for (let index = 0; index < options.length; index++) {
        const node = choiceRefs.current[index]
        if (!node) continue
        const halfWidth = node.offsetWidth / 2
        const x = (projectileX.current[index] ?? width * 0.77) - (width / CHOICE_CROSSING_SECONDS) * dt
        if (x + halfWidth >= 0) allPassed = false
        projectileX.current[index] = x
        const y = laneY(index, height)
        node.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%)`
        if (Math.abs(current.x + 20 - x) < halfWidth + 21 && Math.abs(current.y - y) < node.offsetHeight / 2 + 19) {
          resolved.current = true
          onCollide(options[index].value)
          return
        }
      }
      if (allPassed) {
        resolved.current = true
        onMiss?.()
        return
      }
      frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [flightActive, laneY, onCollide, onMiss, options, reduced])

  function guide(x: number, y: number) {
    const arena = arenaRef.current
    if (!arena || verdict || paused) return
    if (!started) {
      setLaunching(true)
      onStart()
    }
    destination.current = {
      x: Math.max(50, Math.min(arena.clientWidth - 50, x)),
      y: Math.max(questionRef.current ? playBounds.current.top : 76, Math.min(arena.clientHeight - 55, y)),
    }
  }

  function intercept(index: number) {
    const arena = arenaRef.current
    if (!arena || verdict || paused || resolved.current) return
    guide(projectileX.current[index] ?? arena.clientWidth * 0.77, laneY(index, arena.clientHeight))
    if (reduced) {
      resolved.current = true
      onCollide(options[index].value)
    }
  }

  const pose: MascotPose = lives === 0 ? 'die' : verdict ? verdict.correct ? 'fly' : 'float'
    : launching ? 'take-off' : !started ? 'idle' : paused || !options.length ? 'float' : 'fly'
  const tone = verdict ? verdict.correct ? 'right' : 'wrong' : 'idle'

  return <div className="drill-flight" data-tone={tone} data-flying={flightActive && !reduced || undefined}>
    {showHud ? <div className="drill-flight-hud">
      <div className="drill-flight-lives" role="status" aria-label={`${lives} of 3 lives remaining`}>
        {[0, 1, 2].map((index) => <Heart key={index} aria-hidden="true" data-lost={index >= lives || undefined} />)}
      </div>
      <button type="button" className="drill-flight-pause"
        aria-label={paused ? 'Resume flight' : 'Pause flight'} onClick={() => setPaused(!paused)}>
        {paused ? <Play aria-hidden="true" /> : <Pause aria-hidden="true" />}
      </button>
    </div> : null}

    <div ref={arenaRef} className="drill-flight-field" role="group" aria-label="Flight arena. Move your mouse or tap to steer toward the correct answer."
      onPointerMove={(event) => {
        if (!started || event.pointerType !== 'mouse' || reduced) return
        const bounds = event.currentTarget.getBoundingClientRect()
        guide(event.clientX - bounds.left, event.clientY - bounds.top)
      }}
      onPointerDown={(event) => {
        if ((event.target as Element).closest('button')) return
        const bounds = event.currentTarget.getBoundingClientRect()
        guide(event.clientX - bounds.left, event.clientY - bounds.top)
      }}>
      <div className="drill-flight-sky" aria-hidden="true" />
      <div className="drill-flight-horizon" aria-hidden="true" />
      {children ? <div ref={questionRef} className="drill-flight-question">{children}</div> : null}
      <div className="drill-flight-platform" aria-hidden="true"><span /></div>
      {options.map((option, index) => <div key={option.value} className="drill-flight-lane" aria-hidden="true"
        style={{ top: `calc(var(--drill-play-top, 64px) + ${(index + 0.5) / Math.max(1, options.length)} * (100% - var(--drill-play-top, 64px) - var(--drill-play-bottom, 36px)))` }} />)}
      <div ref={actorRef} className="drill-flight-actor" data-pose={pose}>
        <div className="drill-flight-actor-art"><div ref={tiltRef} className="drill-flight-tilt">
          <div className="drill-flight-recoil" data-stagger={verdict && !verdict.correct && lives > 0 ? round : undefined}>
            <MascotSprite pose={pose} size={192} />
          </div>
        </div></div>
      </div>
      <div className="drill-flight-projectiles" role="group" aria-label="Incoming answers">
        {options.map((option, index) => <button key={option.value} type="button"
          ref={(node) => { choiceRefs.current[index] = node }}
          className="drill-projectile" data-voice={voice}
          data-hit={verdict?.picked === option.value ? tone : undefined}
          disabled={Boolean(verdict) || paused} onClick={() => intercept(index)}
          aria-keyshortcuts={String(index + 1)}
          aria-label={verdict?.picked === option.value ? verdict.correct ? 'Correct' : 'Wrong' : `Fly to answer ${index + 1}: ${option.value}`}>
          {verdict?.picked === option.value ? <>
            {verdict.correct ? <Check aria-hidden="true" /> : <X aria-hidden="true" />}
            <strong>{verdict.correct ? 'Correct' : 'Wrong'}</strong>
          </> : <><span className="drill-projectile-number" aria-hidden="true">{index + 1}</span>
            <span>{option.value}</span></>}
        </button>)}
      </div>
      {!started ? <div className="drill-flight-intro">
        <button type="button" className="ui-button ui-button--default"
          onClick={() => guide((arenaRef.current?.clientWidth ?? 600) * 0.28,
            (playBounds.current.top + (arenaRef.current?.clientHeight ?? 400) - playBounds.current.bottom) / 2)}>
          <Play aria-hidden="true" /> Take off
        </button>
        <p>{reduced ? 'Choose an answer to fly into it.' : 'Move to steer. Fly into an answer.'}</p>
      </div> : null}
      {paused ? <div className="drill-flight-overlay">
        <Pause aria-hidden="true" /><h2>Flight paused</h2>
        <button type="button" className="ui-button ui-button--default" onClick={() => setPaused(false)}>Resume</button>
      </div> : null}
    </div>
  </div>
}
