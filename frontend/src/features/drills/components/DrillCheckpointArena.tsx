import { useEffect, useRef, useState } from 'react'
import { Check, Flag, Keyboard, Pause, Play, Undo2 } from 'lucide-react'

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
}

/** The answer is the pavement: missing pieces and the first wrong piece are holes. */
export function DrillCheckpointArena({ values, expected, variant, verdict, onAnswer, onResolve }: {
  values: string[]
  expected: string[]
  variant: 'tokens' | 'steps'
  verdict: DrillVerdict | null
  onAnswer: (answer: DrillAnswer | null) => void
} & DrillCheckpointControls) {
  const [placedIds, setPlacedIds] = useState<number[]>([])
  const [typed, setTyped] = useState<string | null>(null)
  const [typedConfirmed, setTypedConfirmed] = useState(false)
  const [phase, setPhase] = useState<Phase>('walking')
  const [hole, setHole] = useState<number | null>(null)
  const [paused, setPaused] = useState(false)
  const [facingLeft, setFacingLeft] = useState(false)
  const viewportRef = useRef<HTMLDivElement>(null)
  const actorRef = useRef<HTMLDivElement>(null)
  const position = useRef(64)
  const resolved = useRef(false)
  const attempt = useRef<{ values: string[]; wrong: number | null; canRun: boolean } | null>(null)
  const typedValues = typed?.trim().split(/\s+/).filter(Boolean) ?? []
  const placed = typed === null ? placedIds.map((id) => values[id]) : typedConfirmed ? typedValues : []
  const latest = useRef({ placed, onResolve, readyToJudge: false })
  latest.current = { placed, onResolve, readyToJudge: typed === null ? placed.length >= expected.length : typedConfirmed }
  const locked = Boolean(verdict) || phase !== 'walking'
  const slotCount = Math.max(expected.length, placed.length)

  function update(nextIds: number[], nextTyped = typed) {
    if (locked) return
    setPlacedIds(nextIds)
    setTyped(nextTyped)
    setTypedConfirmed(false)
    const next = nextTyped === null ? nextIds.map((id) => values[id]) : nextTyped.trim().split(/\s+/).filter(Boolean)
    onAnswer(next.length ? { kind: 'tokens', values: next } : null)
  }

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
    <div className="drill-path-hud">
      <span><Flag aria-hidden="true" /> Walking checkpoint</span>
      <span className="drill-path-count">{placed.length}/{expected.length} blocks</span>
      <button type="button" className="drill-path-pause" disabled={['falling', 'fallen', 'crossed'].includes(phase)}
        aria-label={paused ? 'Resume crossing' : 'Pause crossing'} onClick={() => setPaused(!paused)}>
        {paused ? <Play aria-hidden="true" /> : <Pause aria-hidden="true" />}
      </button>
    </div>
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
              {value !== undefined ? <button type="button" className="drill-path-slab" disabled={locked || typed !== null}
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
    {typed !== null ? <form className="drill-path-typing" onSubmit={(event) => {
      event.preventDefault()
      if (!locked && typedValues.length) setTypedConfirmed(true)
    }}>
      <label>Type the command<input className="drill-typed-input" value={typed} disabled={locked}
        spellCheck={false} autoComplete="off" autoCapitalize="off" autoCorrect="off" placeholder="git …"
        onKeyDown={(event) => { if (event.key === 'Enter') event.stopPropagation() }}
        onChange={(event) => update([], event.target.value)} /></label>
      {!locked ? <button type="submit" className="ui-button ui-button--outline" disabled={!typedValues.length || typedConfirmed}>
        {typedConfirmed ? 'Command placed' : 'Place command'}
      </button> : null}
      {!locked ? <button type="button" className="drill-mode-toggle" onClick={() => update([], null)}><Undo2 aria-hidden="true" />Use the token bank</button> : null}
    </form> : <>
      <div className="drill-path-bank-label">{locked ? 'Arrangement locked' : 'Build from left to right'}
        {!locked ? <span>Click a placed block to remove it</span> : null}
      </div>
      <ul className="drill-bank" aria-label="Available pieces">
        {values.map((value, id) => placedIds.includes(id) ? null : <li key={id}>
          <button type="button" className="drill-piece" disabled={locked} onClick={() => update([...placedIds, id])}>{value}</button>
        </li>)}
      </ul>
      {variant === 'tokens' && !locked ? <button type="button" className="drill-mode-toggle" onClick={() => update([], '')}>
        <Keyboard aria-hidden="true" />Type it instead
      </button> : null}
    </>}
  </div>
}
