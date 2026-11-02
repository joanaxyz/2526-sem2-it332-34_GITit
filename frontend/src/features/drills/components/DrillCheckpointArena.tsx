import { useEffect, useEffectEvent, useRef, useState } from 'react'
import { Check, Flag, Pause, Play } from 'lucide-react'

import type { DrillAnswer, DrillVerdict } from '@/features/drills/types'
import { firstWrongBlock } from '@/features/drills/utils/drillGrading'
import { prefersReducedMotion } from '@/features/drills/utils/flyToSlot'
import { MascotSprite } from '@/shared/mascot/MascotSprite'

const START_WIDTH = 192
const BLOCK_WIDTH = 160
const FINISH_WIDTH = 160
const FALL_MS = 1100
const MIN_RUN_DISTANCE = BLOCK_WIDTH * 2
const WALK_IN_DISTANCE = BLOCK_WIDTH / 2
const RUN_SPEED = 144
type Phase = 'walking' | 'checking' | 'running' | 'falling' | 'fallen' | 'crossed'

export type DrillCheckpointControls = {
  onResolve: (answer: DrillAnswer | null, fell: boolean) => void
  paused?: boolean
  onPauseChange?: (paused: boolean) => void
  showHud?: boolean
}

/** The answer is the pavement: missing pieces and the first wrong piece are holes. */
export function DrillCheckpointArena({ values, expected, variant, verdict, onAnswer, onResolve, paused: pausedProp, onPauseChange, showHud = true }: {
  values: string[]
  expected: string[]
  variant: 'tokens' | 'steps'
  verdict: DrillVerdict | null
  onAnswer: (answer: DrillAnswer | null) => void
} & DrillCheckpointControls) {
  const [placedIds, setPlacedIds] = useState<number[]>([])
  const placedIdsRef = useRef<number[]>([])
  const [keystrokes, setKeystrokes] = useState('')
  const keystrokesRef = useRef('')
  const [phase, setPhase] = useState<Phase>('walking')
  const [hole, setHole] = useState<number | null>(null)
  const [localPaused, setLocalPaused] = useState(false)
  const paused = pausedProp ?? localPaused
  function setPaused(next: boolean) { setLocalPaused(next); onPauseChange?.(next) }
  const [facingLeft, setFacingLeft] = useState(false)
  const viewportRef = useRef<HTMLDivElement>(null)
  const actorRef = useRef<HTMLDivElement>(null)
  const position = useRef(64)
  const resolved = useRef(false)
  const attempt = useRef<{ values: string[]; wrong: number | null; canRun: boolean } | null>(null)
  const placed = placedIds.map((id) => values[id])
  const latest = useRef({ placed, onResolve, readyToJudge: false })
  latest.current = { placed, onResolve, readyToJudge: placed.length >= expected.length }
  const locked = Boolean(verdict) || phase !== 'walking'
  const slotCount = Math.max(expected.length, placed.length)

  function typePrefix(next: string) {
    keystrokesRef.current = next
    setKeystrokes(next)
  }

  function update(nextIds: number[]) {
    if (locked || paused) return
    placedIdsRef.current = nextIds
    setPlacedIds(nextIds)
    typePrefix('')
    const next = nextIds.map((id) => values[id])
    onAnswer(next.length ? { kind: 'tokens', values: next } : null)
  }

  const onPieceKey = useEffectEvent((event: KeyboardEvent) => {
    if (event.defaultPrevented || event.repeat || event.isComposing || event.metaKey || event.ctrlKey || event.altKey || locked || paused) return
    const target = event.target
    if (target instanceof Element) {
      if (target.closest('input, textarea, select, [contenteditable]:not([contenteditable="false"]), [role="dialog"]')) return
      const control = target.closest('button, a, [role="button"], [role="tab"]')
      if (control && !control.matches('.drill-piece, .drill-path-slab')) return
      // A focused piece keeps its native Space/Enter activation unless a
      // partially typed value needs the delimiter to finish it.
      if (control && !keystrokesRef.current && (event.key === ' ' || event.key === 'Enter')) return
    }
    if (event.key === 'Escape') return
    const ids = placedIdsRef.current
    if (event.key === 'Backspace') {
      event.preventDefault()
      if (keystrokesRef.current) typePrefix(keystrokesRef.current.slice(0, -1))
      else if (ids.length) update(ids.slice(0, -1))
      return
    }
    const delimiter = event.key === 'Enter' || (variant === 'tokens' && event.key === ' ')
    if (!delimiter && event.key.length !== 1) return
    if (delimiter && !keystrokesRef.current) {
      if (event.key === ' ') event.preventDefault()
      return
    }
    event.preventDefault()
    const prefix = delimiter ? keystrokesRef.current : keystrokesRef.current + event.key
    const available = values.map((value, id) => ({ value, id })).filter(({ id }) => !ids.includes(id))
    const exact = available.find(({ value }) => value === prefix)
    const ambiguous = available.some(({ value }) => value !== prefix && value.startsWith(prefix))
    if (exact && (delimiter || !ambiguous)) {
      update([...ids, exact.id])
      // Typing has taken over from piece-button navigation. Return focus
      // to the course so the next separator cannot activate an older slab.
      if (target instanceof Element && target.closest('.drill-piece, .drill-path-slab')) {
        viewportRef.current?.focus({ preventScroll: true })
      }
      return
    }
    // Keep a mistyped prefix visible so Backspace can correct it without
    // committing a wrong block or silently discarding keystrokes.
    const maxLength = Math.max(0, ...available.map(({ value }) => value.length)) + 1
    typePrefix(prefix.slice(0, maxLength))
  })

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => onPieceKey(event)
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  useEffect(() => {
    if (paused || verdict) return
    let frame = 0
    let last = 0
    let fallTimer: ReturnType<typeof setTimeout> | undefined
    let falling = false
    const reduced = prefersReducedMotion()
    setPhase(attempt.current ? 'checking' : 'walking')

    function resolve(fell: boolean, snapshot: string[]) {
      if (resolved.current) return
      resolved.current = true
      setPhase(fell ? 'fallen' : 'crossed')
      latest.current.onResolve(snapshot.length ? { kind: 'tokens', values: snapshot } : null, fell)
    }

    function tick(time: number) {
      if (resolved.current || falling) return
      // A background tab never silently spends the learner's building time.
      const dt = !last || document.hidden ? 0 : Math.min((time - last) / 1000, 0.05)
      last = time
      const current = latest.current.placed
      if (!attempt.current && latest.current.readyToJudge) {
        const wrong = firstWrongBlock(current, expected, variant)
        const destination = wrong === null
          ? START_WIDTH + slotCount * BLOCK_WIDTH + FINISH_WIDTH / 2
          : START_WIDTH + wrong * BLOCK_WIDTH + BLOCK_WIDTH / 2
        attempt.current = { values: [...current], wrong, canRun: Math.abs(destination - position.current) >= MIN_RUN_DISTANCE }
        setHole(wrong)
      }
      const judged = attempt.current
      const gap = judged ? judged.wrong : current.length
      const target = gap === null
        ? START_WIDTH + slotCount * BLOCK_WIDTH + FINISH_WIDTH / 2
        : START_WIDTH + gap * BLOCK_WIDTH + BLOCK_WIDTH / 2
      const distance = target - position.current
      setFacingLeft((previous) => previous === (distance < -1) ? previous : distance < -1)
      // Known outcomes can be reached faster; only a safe checkpoint gets a walk-in.
      const running = judged?.canRun && (judged.wrong !== null || distance > WALK_IN_DISTANCE)
      const movement = running ? 'running' : judged ? 'checking' : 'walking'
      setPhase((previous) => previous === movement ? previous : movement)
      const speed = running ? RUN_SPEED : variant === 'steps' ? 24 : 30
      const step = Math.min(Math.abs(distance), speed * dt)
      position.current += Math.sign(distance) * step
      const paintedPosition = reduced
        ? position.current < START_WIDTH ? 64 : Math.min(target, START_WIDTH + Math.floor((position.current - START_WIDTH) / BLOCK_WIDTH) * BLOCK_WIDTH + BLOCK_WIDTH / 2)
        : position.current
      if (actorRef.current) actorRef.current.style.transform = `translateX(${paintedPosition}px)`
      const viewport = viewportRef.current
      if (viewport) {
        const x = position.current - viewport.scrollLeft
        if (x > viewport.clientWidth * 0.7 || x < viewport.clientWidth * 0.15) {
          viewport.scrollLeft = Math.max(0, position.current - viewport.clientWidth * 0.4)
        }
      }
      if (Math.abs(target - position.current) < 1) {
        if (gap === null) {
          resolve(false, judged!.values)
        } else {
          falling = true
          setHole(gap)
          setPhase('falling')
          const snapshot = [...(judged?.values ?? current)]
          fallTimer = setTimeout(() => resolve(true, snapshot), reduced ? 150 : FALL_MS)
        }
        return
      }
      frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => {
      cancelAnimationFrame(frame)
      clearTimeout(fallTimer)
    }
  }, [expected, paused, slotCount, variant, verdict])

  const pose = phase === 'falling' || phase === 'fallen' ? 'idle'
    : paused || phase === 'crossed' ? 'idle' : phase === 'running' ? 'run' : 'walk'
  const status = phase === 'fallen' ? 'Game over. Blue fell through the path.'
    : phase === 'falling' ? 'The ground gave way!'
    : phase === 'crossed' ? 'Checkpoint cleared. The path holds.'
    : paused ? 'Crossing paused.'
    : phase === 'running' && hole === null ? 'The path holds. Heading for the checkpoint.'
    : phase === 'checking' || phase === 'running' ? hole === null ? 'The path holds. Keep walking.' : `Block ${hole + 1} is wrong. A hole opened.`
    : 'Fill the gaps before Blue reaches them.'

  return <div className="drill-checkpoint" data-phase={phase}>
    {showHud ? <div className="drill-path-hud">
      <span className="drill-path-count" aria-label={`${placed.length} of ${expected.length} blocks placed`}>{placed.length}/{expected.length}</span>
      <button type="button" className="drill-path-pause" disabled={['falling', 'fallen', 'crossed'].includes(phase)}
        aria-label={paused ? 'Resume crossing' : 'Pause crossing'} onClick={() => setPaused(!paused)}>
        {paused ? <Play aria-hidden="true" /> : <Pause aria-hidden="true" />}
      </button>
    </div> : null}
    <div ref={viewportRef} className="drill-path-viewport" role="region" aria-label="Command pavement" tabIndex={0}>
      <div className="drill-path-course" style={{ width: START_WIDTH + slotCount * BLOCK_WIDTH + FINISH_WIDTH }}>
        <div className="drill-path-scenery" aria-hidden="true" />
        <div ref={actorRef} className="drill-path-actor" data-pose={pose} style={{ transform: 'translateX(64px)' }}>
          <div className="drill-path-actor-art"><MascotSprite pose={pose} size={160} flip={facingLeft} /></div>
        </div>
        <div className="drill-path-ground" style={{ gridTemplateColumns: `${START_WIDTH}px repeat(${slotCount}, ${BLOCK_WIDTH}px) ${FINISH_WIDTH}px` }}>
          <div className="drill-path-land drill-path-start"><span>START</span></div>
          {Array.from({ length: slotCount }, (_, index) => {
            const value = placed[index]
            const collapsed = hole === index
            const empty = value === undefined
            return <div key={index} className="drill-path-block" data-hole={empty || collapsed || undefined}
              data-collapsed={collapsed || undefined} data-state={collapsed ? 'wrong' : verdict?.correct ? 'right' : undefined}>
              {empty || collapsed ? <div className="drill-path-hole" aria-hidden="true"><span /><i /><i /></div> : null}
              {value !== undefined ? <button type="button" className="drill-path-slab" disabled={locked || paused}
                aria-label={`${collapsed ? 'Wrong block' : 'Remove'} ${value} ${collapsed ? 'at' : 'from'} position ${index + 1}`}
                onClick={() => update(placedIds.filter((_, i) => i !== index))}>
                <span className="drill-path-block-number">{index + 1}</span><code>{value}</code>
                {collapsed ? <span className="drill-path-broken-label">Ground collapsed</span> : null}
              </button> : <span className="drill-path-empty-label">{index + 1}<span>Open gap</span></span>}
            </div>
          })}
          <div className="drill-path-land drill-path-finish"><Flag aria-hidden="true" /><span>CHECKPOINT</span></div>
        </div>
      </div>
    </div>
    <div className="drill-path-caption" role="status" aria-live="polite">
      {phase === 'crossed' ? <Check aria-hidden="true" /> : null}<span>{status}</span>
    </div>
    <ul className="drill-bank" aria-label="Available pieces">
      {values.map((value, id) => placedIds.includes(id) ? null : <li key={id}>
        <button type="button" className="drill-piece" disabled={locked || paused}
          data-typing={Boolean(keystrokes && value.startsWith(keystrokes)) || undefined}
          onClick={() => update([...placedIdsRef.current, id])}>{value}</button>
      </li>)}
    </ul>
    <output className="drill-path-keystrokes" role="status" aria-live="polite"
      data-invalid={Boolean(keystrokes && !values.some((value, id) => !placedIds.includes(id) && value.startsWith(keystrokes))) || undefined}>
      {!locked && keystrokes ? <kbd>{keystrokes}</kbd> : null}
    </output>
    {paused ? <div className="drill-flight-overlay"><Pause aria-hidden="true" /><h2>Crossing paused</h2>
      <button type="button" className="ui-button ui-button--default" onClick={() => setPaused(false)}>Resume</button>
    </div> : null}
  </div>
}
