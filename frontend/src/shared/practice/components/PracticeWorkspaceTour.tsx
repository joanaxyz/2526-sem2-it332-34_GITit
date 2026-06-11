import { Check, GitBranch, HelpCircle, MessageSquareText, MonitorDot, PanelLeft, TerminalSquare, X } from 'lucide-react'
import { useEffect, useState } from 'react'

import type { ChallengeRun } from '@/shared/practice/types'
import { Button } from '@/shared/components/Button'
import { cn } from '@/shared/utils/cn'

const tourSteps = [
  {
    target: 'practice-brief',
    icon: PanelLeft,
    label: 'Practice brief',
    body: 'Story, required details, constraints, and attempt state live here. Read this before touching the terminal.',
    placement: 'right',
  },
  {
    target: 'live-dag',
    icon: GitBranch,
    label: 'Live DAG',
    body: 'Your current repository map. Watch commits, branches, and HEAD move after each valid command.',
    placement: 'bottom',
  },
  {
    target: 'expected-state',
    icon: MonitorDot,
    label: 'Target DAG',
    body: 'On supported quests, this diagram shows the target repository shape without giving away the command path.',
    placement: 'bottom',
  },
  {
    target: 'terminal',
    icon: TerminalSquare,
    label: 'Terminal',
    body: 'Inspect for free, then act. State-changing Git commands update the simulator and use action budget.',
    placement: 'top',
  },
  {
    target: 'feedback',
    icon: MessageSquareText,
    label: 'Feedback panel',
    body: 'When guidance is available, this explains what your last command changed without handing you the solution.',
    placement: 'top',
  },
] as const

type TourTarget = (typeof tourSteps)[number]

type CalloutLayout = {
  card: { left: number; top: number }
  dot: { x: number; y: number }
  lineEnd: { x: number; y: number }
}

const CALLOUT_WIDTH = 260
const CALLOUT_HEIGHT = 132
const EDGE_GAP = 14

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max)
}

function getCalloutLayout(target: TourTarget, rect: DOMRect): CalloutLayout {
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 2
  let left = centerX - CALLOUT_WIDTH / 2
  let top = centerY - CALLOUT_HEIGHT / 2

  if (target.placement === 'right') {
    left = rect.right + 18
    top = rect.top + Math.min(84, rect.height / 3)
  }

  if (target.placement === 'bottom') {
    top = rect.bottom + 16
  }

  if (target.placement === 'top') {
    top = rect.top - CALLOUT_HEIGHT - 16
  }

  left = clamp(left, EDGE_GAP, viewportWidth - CALLOUT_WIDTH - EDGE_GAP)
  top = clamp(top, 56, viewportHeight - CALLOUT_HEIGHT - EDGE_GAP)

  const cardCenterX = left + CALLOUT_WIDTH / 2
  const cardCenterY = top + CALLOUT_HEIGHT / 2
  return {
    card: { left, top },
    dot: { x: centerX, y: centerY },
    lineEnd: { x: cardCenterX, y: cardCenterY },
  }
}

export function ChallengeWorkspaceTour({
  run,
  onClose,
}: {
  run: ChallengeRun
  onClose: () => void
}) {
  const [layouts, setLayouts] = useState<Record<string, CalloutLayout>>({})

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') onClose()
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  useEffect(() => {
    let frameId = 0

    function updateLayouts() {
      frameId = window.requestAnimationFrame(() => {
        const nextLayouts: Record<string, CalloutLayout> = {}
        for (const step of tourSteps) {
          const element = document.querySelector(`[data-tour-target="${step.target}"]`)
          const rect = element?.getBoundingClientRect()
          if (rect && rect.width > 0 && rect.height > 0) {
            nextLayouts[step.target] = getCalloutLayout(step, rect)
          }
        }
        setLayouts(nextLayouts)
      })
    }

    updateLayouts()
    window.addEventListener('resize', updateLayouts)
    window.addEventListener('scroll', updateLayouts, true)
    return () => {
      window.cancelAnimationFrame(frameId)
      window.removeEventListener('resize', updateLayouts)
      window.removeEventListener('scroll', updateLayouts, true)
    }
  }, [run.id])

  return (
    <div className="pointer-events-none fixed inset-0 z-50 overflow-hidden">
      <svg className="absolute inset-0 h-full w-full" aria-hidden="true">
        <defs>
          <marker id="tour-arrowhead" markerHeight="8" markerWidth="8" orient="auto" refX="6" refY="3">
            <path d="M0,0 L0,6 L7,3 z" className="fill-accent" />
          </marker>
        </defs>
        {tourSteps.map((step) => {
          const layout = layouts[step.target]
          if (!layout) return null
          return (
            <line
              key={step.target}
              x1={layout.lineEnd.x}
              y1={layout.lineEnd.y}
              x2={layout.dot.x}
              y2={layout.dot.y}
              className="stroke-accent/80"
              markerEnd="url(#tour-arrowhead)"
              strokeDasharray="5 6"
              strokeLinecap="round"
              strokeWidth="1.8"
            />
          )
        })}
      </svg>

      <div className="pointer-events-auto absolute right-4 top-14 flex max-w-[calc(100vw-2rem)] items-center gap-2 rounded-full border border-border bg-card/95 px-3 py-2 shadow-[0_18px_54px_rgba(0,0,0,0.34)]">
        <HelpCircle className="size-4 text-accent" />
        <span className="text-xs font-medium text-muted-foreground">Workspace map</span>
        <Button type="button" size="sm" className="h-7 rounded-full px-2.5" onClick={onClose}>
          <Check className="size-3.5" />
          Got it
        </Button>
        <Button type="button" variant="ghost" size="icon" className="size-7 rounded-full" aria-label="Close guide" onClick={onClose}>
          <X className="size-3.5" />
        </Button>
      </div>

      {tourSteps.map((step, index) => {
        const layout = layouts[step.target]
        if (!layout) return null
        const Icon = step.icon
        return (
          <div
            key={step.target}
            className="pointer-events-auto absolute w-[260px] rounded-lg border border-border bg-card/95 p-3 shadow-[0_18px_54px_rgba(0,0,0,0.34)]"
            style={{ left: layout.card.left, top: layout.card.top }}
          >
            <div className="flex items-start gap-3">
              <div className="grid size-8 shrink-0 place-items-center rounded-md border border-accent/30 bg-accent/10 text-accent">
                <Icon className="size-4" />
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="grid size-5 shrink-0 place-items-center rounded-full bg-accent text-[11px] font-bold text-accent-foreground">
                    {index + 1}
                  </span>
                  <h2 className="text-sm font-semibold leading-tight">{step.label}</h2>
                </div>
                <p className="mt-2 text-xs leading-5 text-muted-foreground">{step.body}</p>
              </div>
            </div>
          </div>
        )
      })}

      {tourSteps.map((step, index) => {
        const layout = layouts[step.target]
        return layout ? (
          <div
            key={`${step.target}-dot`}
            className={cn(
              'absolute grid size-8 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full border border-accent bg-background text-xs font-bold text-accent shadow-[0_0_0_6px_hsla(var(--accent)/0.16)]',
            )}
            style={{ left: layout.dot.x, top: layout.dot.y }}
          >
            {index + 1}
          </div>
        ) : null
      })}
    </div>
  )
}
