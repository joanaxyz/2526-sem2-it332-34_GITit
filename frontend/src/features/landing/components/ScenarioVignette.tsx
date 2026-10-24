import { useEffect, useRef, useState, type CSSProperties } from 'react'
import { Check, RotateCcw } from 'lucide-react'

import { VIGNETTE_COMMANDS } from '@/features/landing/utils/landingContent'
import { cn } from '@/shared/utils/cn'

const LAST_STEP = VIGNETTE_COMMANDS.length
const FIRST_STEP_DELAY_MS = 600
const STEP_MS = 1700

const NODES = {
  c1: { x: 84, y: 104, hash: '1c07e3a' },
  c2: { x: 140, y: 104, hash: '8d41e07' },
  c3: { x: 206, y: 46, hash: '3f9a2c1' },
  m: { x: 276, y: 104, hash: 'b52e9d4' },
} as const

type NodeId = keyof typeof NODES

// Where HEAD points after each step, read by index alongside VIGNETTE_COMMANDS.
const HEAD_BY_STEP: { node: NodeId; branch: string }[] = [
  { node: 'c2', branch: 'main' },
  { node: 'c2', branch: 'spellbook' },
  { node: 'c3', branch: 'spellbook' },
  { node: 'c2', branch: 'main' },
  { node: 'm', branch: 'main' },
]

// The resolved motion setting (shared/preferences) already folds in the OS
// preference, so the demo also honours the in-app Motion switch.
function motionReduced() {
  return typeof document !== 'undefined' && document.documentElement.dataset.motion === 'reduced'
}

export function ScenarioVignette() {
  const rootRef = useRef<HTMLElement>(null)
  const [reduced] = useState(motionReduced)
  const [step, setStep] = useState(() => (reduced ? LAST_STEP : 0))
  const [playing, setPlaying] = useState(() => typeof IntersectionObserver === 'undefined')

  useEffect(() => {
    const node = rootRef.current
    if (playing || reduced || !node) return
    const observer = new IntersectionObserver(
      (entries) => {
        if (!entries.some((entry) => entry.isIntersecting)) return
        setPlaying(true)
        observer.disconnect()
      },
      { threshold: 0.45 },
    )
    observer.observe(node)
    return () => observer.disconnect()
  }, [playing, reduced])

  useEffect(() => {
    if (!playing || reduced || step >= LAST_STEP) return
    const timer = window.setTimeout(() => setStep((current) => current + 1), step === 0 ? FIRST_STEP_DELAY_MS : STEP_MS)
    return () => window.clearTimeout(timer)
  }, [playing, reduced, step])

  const head = HEAD_BY_STEP[step]
  const headNode = NODES[head.node]
  const cleared = step >= LAST_STEP

  return (
    <figure ref={rootRef} className="landing-vignette" aria-label="Example scenario: branch, commit, and merge">
      <header className="landing-vignette__bar">
        <span className="landing-vignette__eyebrow">Scenario · Branch and merge</span>
        {!reduced && cleared ? (
          <button type="button" className="landing-vignette__replay" onClick={() => setStep(0)}>
            <RotateCcw aria-hidden="true" size={14} />
            Replay
          </button>
        ) : null}
      </header>

      <div className="landing-vignette__terminal">
        {VIGNETTE_COMMANDS.slice(0, step).map((line) => (
          <div key={line.command} className="landing-vignette__entry">
            <p className="landing-vignette__command">
              <span aria-hidden="true">$ </span>
              <span className="landing-vignette__typed" style={{ '--chars': line.command.length } as CSSProperties}>
                {line.command}
              </span>
            </p>
            <p className="landing-vignette__output">{line.output}</p>
          </div>
        ))}
        {cleared ? (
          <p className="landing-vignette__cleared">
            <Check aria-hidden="true" size={15} />
            Target state reached. Scenario cleared.
          </p>
        ) : (
          <p className="landing-vignette__command landing-vignette__command--idle" aria-hidden="true">
            $ <span className="landing-vignette__caret" />
          </p>
        )}
      </div>

      <div className="landing-vignette__graph">
        <svg viewBox="0 0 300 140" aria-hidden="true" className="landing-dag">
          <text x="0" y="108" className="landing-dag__lane is-on">main</text>
          <text x="0" y="50" className={cn('landing-dag__lane', step >= 1 && 'is-on')}>spellbook</text>

          <path d="M84 104 H140" pathLength={1} className="landing-dag__edge is-on" />
          <path d="M140 104 C172 104 174 46 206 46" pathLength={1} className={cn('landing-dag__edge', step >= 2 && 'is-on')} />
          <path d="M140 104 H276" pathLength={1} className={cn('landing-dag__edge', step >= 4 && 'is-on')} />
          <path d="M206 46 C240 46 242 104 276 104" pathLength={1} className={cn('landing-dag__edge', step >= 4 && 'is-on')} />

          <circle cx={NODES.c1.x} cy={NODES.c1.y} r="7" className="landing-dag__node is-on" />
          <circle cx={NODES.c2.x} cy={NODES.c2.y} r="7" className="landing-dag__node is-on" />
          <circle cx={NODES.c3.x} cy={NODES.c3.y} r="7" className={cn('landing-dag__node', step >= 2 && 'is-on')} />
          <circle cx={NODES.m.x} cy={NODES.m.y} r="8" className={cn('landing-dag__node landing-dag__node--merge', step >= 4 && 'is-on')} />

          <g className="landing-dag__head" style={{ transform: `translate(${headNode.x}px, ${headNode.y}px)` }}>
            <circle r="13" />
          </g>
        </svg>
        <p className="landing-vignette__head">
          HEAD → {head.branch} <span>@ {headNode.hash}</span>
        </p>
      </div>
    </figure>
  )
}
