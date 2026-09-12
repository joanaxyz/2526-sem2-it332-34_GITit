import { Check, ChevronRight, Eye, RotateCcw, Undo2 } from 'lucide-react'
import { useMemo, useState } from 'react'

import type { OrientationStep } from '@/features/story-map/components/orientation/types'
import { normalizeBuilderCommand } from '@/features/story-map/components/orientation/types'
import { CentralizedDistributedDiagram } from '@/features/story-map/components/orientation/visuals/CentralizedDistributedDiagram'
import { CommitAnatomyDiagram, CommitChainDiagram } from '@/features/story-map/components/orientation/visuals/CommitChainDiagram'
import { FourAreaPipelineDiagram } from '@/features/story-map/components/orientation/visuals/FourAreaPipelineDiagram'
import { PlatformWorkspaceDiagram } from '@/features/story-map/components/orientation/visuals/PlatformWorkspaceDiagram'
import { Button } from '@/shared/components/Button'
import { CopyButton } from '@/shared/components/CopyButton'
import { LiveDagPanel } from '@/shared/level/components/LiveDagPanel'
import { cn } from '@/shared/utils/cn'

const BUILDER_TOKENS = ['git', 'commit', 'log', 'status', '-m', '--oneline', '--graph', '--all', '"message"']

function addToSet(current: Set<string>, value: string) {
  return new Set([...current, value])
}

function StepAction({
  onClick,
  children = 'Complete & continue',
  disabled = false,
}: {
  onClick: () => void
  children?: string
  disabled?: boolean
}) {
  return (
    <Button type="button" className="orientation-step-primary-action" disabled={disabled} onClick={onClick}>
      {children} <ChevronRight aria-hidden="true" />
    </Button>
  )
}

export function OrientationStepView({
  step,
  layout,
  completed,
  onStepComplete,
  hasNextStep,
  onContinueToNext,
}: {
  step: OrientationStep
  layout: string
  completed: boolean
  onStepComplete: () => void
  hasNextStep: boolean
  onContinueToNext: () => void
}) {
  const [pipelineStage, setPipelineStage] = useState(0)
  const [selectedCompare, setSelectedCompare] = useState<string | null>(null)
  const [visitedCompare, setVisitedCompare] = useState<Set<string>>(() => new Set())
  const [matchSelections, setMatchSelections] = useState<Record<string, string>>({})
  const [matchRevealed, setMatchRevealed] = useState(false)
  const [anatomyPart, setAnatomyPart] = useState<string | null>(null)
  const [visitedAnatomy, setVisitedAnatomy] = useState<Set<string>>(() => new Set())
  const [immutabilityToggled, setImmutabilityToggled] = useState(false)
  const [builderParts, setBuilderParts] = useState<string[]>([])
  const [visitedHotspots, setVisitedHotspots] = useState<Set<string>>(() => new Set())
  const [activeHotspot, setActiveHotspot] = useState<string | null>(null)
  const [statusFocus, setStatusFocus] = useState<'staged' | 'working' | null>(null)
  const [visitedStatus, setVisitedStatus] = useState<Set<string>>(() => new Set())
  const [dagDiscoveries, setDagDiscoveries] = useState<Set<string>>(() => new Set())
  const [errorChoice, setErrorChoice] = useState<string | null>(null)

  const proceed = () => {
    if (!completed) onStepComplete()
    if (hasNextStep) onContinueToNext()
  }

  const builderTarget = normalizeBuilderCommand(step.target ?? '')
  const builderBuilt = useMemo(() => normalizeBuilderCommand(builderParts.join(' ')), [builderParts])
  const builderMatches = Boolean(builderTarget) && builderBuilt === builderTarget
  const answerOptions = useMemo(
    () => [...new Set((step.pairs ?? []).map((pair) => pair.problem))],
    [step.pairs],
  )
  const allPairsSelected =
    (step.pairs ?? []).length > 0 &&
    (step.pairs ?? []).every((pair) => Boolean(matchSelections[pair.scenario]?.trim()))
  const dagTargets = useMemo(() => {
    if (!step.initial_state) return []
    return [...Object.keys(step.initial_state.branches ?? {}).map((branch) => `branch:${branch}`), 'HEAD']
  }, [step.initial_state])

  const content = (() => {
    switch (step.kind) {
      case 'continue':
        return (
          <div className="orientation-reading-step">
            {step.body ? <p>{step.body}</p> : null}
            <StepAction onClick={proceed}>{hasNextStep ? 'Understood — continue' : 'Mark step complete'}</StepAction>
          </div>
        )

      case 'compare_toggle':
        return (
          <div className="orientation-interaction-stack">
            <CentralizedDistributedDiagram
              active={selectedCompare === 'centralized' ? 'centralized' : selectedCompare === 'distributed' ? 'distributed' : null}
            />
            <div className="orientation-choice-grid" role="group" aria-label="Compare version-control models">
              {(step.options ?? []).map((option) => {
                const selected = selectedCompare === option.id
                const visited = visitedCompare.has(option.id)
                return (
                  <button
                    key={option.id}
                    type="button"
                    className={cn('orientation-choice', selected && 'is-selected', visited && 'is-visited')}
                    aria-pressed={selected}
                    onClick={() => {
                      setSelectedCompare(option.id)
                      setVisitedCompare((current) => addToSet(current, option.id))
                    }}
                  >
                    <span>{visited ? <Check aria-hidden="true" /> : <Eye aria-hidden="true" />}</span>
                    <strong>{option.label}</strong>
                    <small>{selected ? option.detail : visited ? 'Inspected' : 'Select to inspect this model'}</small>
                  </button>
                )
              })}
            </div>
            <p className="orientation-interaction-status" aria-live="polite">
              {visitedCompare.size >= (step.options?.length ?? 0) ? 'Both models inspected.' : `${visitedCompare.size} of ${step.options?.length ?? 0} models inspected`}
            </p>
            <StepAction
              onClick={proceed}
              disabled={visitedCompare.size < (step.options?.length ?? 0)}
            >
              {hasNextStep ? 'Complete comparison' : 'Mark step complete'}
            </StepAction>
          </div>
        )

      case 'match_reveal':
        return (
          <div className="orientation-interaction-stack">
            <div className="orientation-match-list">
              {(step.pairs ?? []).map((pair, index) => (
                <label key={pair.scenario} className="orientation-match-row">
                  <span><small>Scenario {index + 1}</small>{pair.scenario}</span>
                  <select
                    value={matchSelections[pair.scenario] ?? ''}
                    onChange={(event) => setMatchSelections((current) => ({ ...current, [pair.scenario]: event.target.value }))}
                  >
                    <option value="">Choose a capability…</option>
                    {answerOptions.map((answer) => <option key={answer} value={answer}>{answer}</option>)}
                  </select>
                </label>
              ))}
            </div>
            {!matchRevealed ? (
              <Button type="button" variant="outline" disabled={!allPairsSelected} onClick={() => setMatchRevealed(true)}>
                Reveal answers
              </Button>
            ) : (
              <div className="orientation-answer-reveal" aria-live="polite">
                {(step.pairs ?? []).map((pair) => (
                  <p key={pair.scenario}>
                    <Check aria-hidden="true" /> <span>{pair.scenario}</span><strong>{pair.problem}</strong>
                  </p>
                ))}
              </div>
            )}
            {matchRevealed ? <StepAction onClick={proceed} /> : null}
          </div>
        )

      case 'git_command':
      case 'shell_command': {
        const command = (step.accept_prefixes ?? step.accept_exact ?? [])[0] ?? step.hint ?? 'See the prompt above.'
        return (
          <div className="orientation-command-lesson">
            <div className="orientation-command-block">
              <div className="orientation-command-label">
                <span>{step.kind === 'git_command' ? 'Git command' : 'Shell command'}</span>
                <CopyButton value={command} label="command" />
              </div>
              <pre><code>{command}</code></pre>
            </div>
            {step.success_output ? (
              <div className="orientation-output-block">
                <span>Expected output</span>
                <pre><code>{step.success_output}</code></pre>
              </div>
            ) : null}
            {step.hint ? <p className="orientation-hint">{step.hint}</p> : null}
            <StepAction onClick={proceed}>{hasNextStep ? 'I tried this — continue' : 'Mark step complete'}</StepAction>
          </div>
        )
      }

      case 'pipeline':
        return (
          <div className="orientation-interaction-stack">
            <FourAreaPipelineDiagram
              activeIndex={pipelineStage}
              onSelectStage={(index) => setPipelineStage(index)}
            />
            <p className="orientation-interaction-status" aria-live="polite">
              Area {pipelineStage + 1} of {step.stages?.length ?? 4}
            </p>
            <Button
              type="button"
              className="orientation-step-primary-action"
              onClick={() => {
                const finalStage = pipelineStage + 1 >= (step.stages?.length ?? 4)
                if (finalStage) proceed()
                else setPipelineStage((value) => value + 1)
              }}
            >
              {pipelineStage + 1 >= (step.stages?.length ?? 4) ? 'Complete the lifecycle' : 'Move file forward'}
              <ChevronRight aria-hidden="true" />
            </Button>
          </div>
        )

      case 'status_annotate': {
        const lines = (step.sample_output ?? '').split('\n')
        let section: 'neutral' | 'staged' | 'working' = 'neutral'
        return (
          <div className="orientation-interaction-stack">
            <div className="orientation-status-controls" role="group" aria-label="Highlight git status sections">
              <button
                type="button"
                className={statusFocus === 'staged' ? 'is-selected' : undefined}
                aria-pressed={statusFocus === 'staged'}
                onClick={() => {
                  setStatusFocus('staged')
                  setVisitedStatus((current) => addToSet(current, 'staged'))
                }}
              >Staging area <small>Changes to be committed</small></button>
              <button
                type="button"
                className={statusFocus === 'working' ? 'is-selected' : undefined}
                aria-pressed={statusFocus === 'working'}
                onClick={() => {
                  setStatusFocus('working')
                  setVisitedStatus((current) => addToSet(current, 'working'))
                }}
              >Working tree <small>Changes not staged</small></button>
            </div>
            <pre className="orientation-status-output"><code>{lines.map((line, index) => {
              if (line.startsWith('Changes to be committed:')) section = 'staged'
              if (line.startsWith('Changes not staged for commit:')) section = 'working'
              return <span key={`${index}-${line}`} className={statusFocus === section ? 'is-highlighted' : undefined}>{line || ' '}\n</span>
            })}</code></pre>
            <p className="orientation-interaction-status" aria-live="polite">{visitedStatus.size} of 2 areas inspected</p>
            <Button type="button" disabled={visitedStatus.size < 2} onClick={proceed}>
              Complete status check <ChevronRight aria-hidden="true" />
            </Button>
          </div>
        )
      }

      case 'anatomy':
        return (
          <div className="orientation-interaction-stack">
            <CommitAnatomyDiagram highlight={anatomyPart} />
            <div className="orientation-token-row" role="group" aria-label="Commit fields">
              {(step.parts ?? []).map((part) => (
                <button
                  key={part}
                  type="button"
                  className={cn(anatomyPart === part && 'is-selected', visitedAnatomy.has(part) && 'is-visited')}
                  aria-pressed={anatomyPart === part}
                  onClick={() => {
                    setAnatomyPart(part)
                    setVisitedAnatomy((current) => addToSet(current, part))
                  }}
                >
                  {visitedAnatomy.has(part) ? <Check aria-hidden="true" /> : null}{part}
                </button>
              ))}
            </div>
            <p className="orientation-interaction-status" aria-live="polite">{visitedAnatomy.size} of {step.parts?.length ?? 0} fields inspected</p>
            <Button type="button" disabled={visitedAnatomy.size < (step.parts?.length ?? 0)} onClick={proceed}>
              Complete anatomy review <ChevronRight aria-hidden="true" />
            </Button>
          </div>
        )

      case 'immutability_demo':
        return (
          <div className="orientation-interaction-stack">
            <p className="orientation-support-copy">Amending creates a <strong>new</strong> commit; the original remains unchanged.</p>
            <CommitChainDiagram amended={immutabilityToggled} />
            {!immutabilityToggled ? (
              <Button type="button" variant="outline" onClick={() => setImmutabilityToggled(true)}>
                <RotateCcw aria-hidden="true" /> Simulate amend
              </Button>
            ) : (
              <StepAction onClick={proceed}>Commit hash changed — continue</StepAction>
            )}
          </div>
        )

      case 'dag_explore':
        return (
          <div className="orientation-interaction-stack">
            {step.initial_state ? (
              <LiveDagPanel snapshot={step.initial_state} title="Commit graph" className="orientation-dag-panel" />
            ) : null}
            <p className="orientation-support-copy">Select each pointer after you find it in the graph.</p>
            <div className="orientation-token-row" role="group" aria-label="Graph pointers to find">
              {dagTargets.map((target) => (
                <button
                  key={target}
                  type="button"
                  className={dagDiscoveries.has(target) ? 'is-visited' : undefined}
                  aria-pressed={dagDiscoveries.has(target)}
                  onClick={() => setDagDiscoveries((current) => addToSet(current, target))}
                >
                  {dagDiscoveries.has(target) ? <Check aria-hidden="true" /> : <Eye aria-hidden="true" />}
                  {target.replace('branch:', '')}
                </button>
              ))}
            </div>
            <Button type="button" disabled={dagDiscoveries.size < dagTargets.length} onClick={proceed}>
              Complete graph inspection <ChevronRight aria-hidden="true" />
            </Button>
          </div>
        )

      case 'command_builder':
        return (
          <div className="orientation-command-builder">
            <div className="orientation-token-row" role="group" aria-label="Command tokens">
              {BUILDER_TOKENS.map((token) => (
                <button key={token} type="button" onClick={() => setBuilderParts((current) => [...current, token])}>
                  {token}
                </button>
              ))}
            </div>
            <div className={cn('orientation-built-command', builderMatches && 'is-correct')}>
              <code>{builderBuilt || 'Choose tokens to build the command'}</code>
              <div>
                <button type="button" aria-label="Remove last token" disabled={!builderParts.length} onClick={() => setBuilderParts((current) => current.slice(0, -1))}>
                  <Undo2 aria-hidden="true" />
                </button>
                <button type="button" aria-label="Clear command" disabled={!builderParts.length} onClick={() => setBuilderParts([])}>
                  <RotateCcw aria-hidden="true" />
                </button>
              </div>
            </div>
            <p className={cn('orientation-interaction-status', builderMatches && 'is-success')} aria-live="polite">
              {builderMatches ? 'Command assembled correctly.' : 'Order matters: Git, subcommand, flags, then arguments.'}
            </p>
            <Button type="button" disabled={!builderMatches} onClick={proceed}>
              Complete command <ChevronRight aria-hidden="true" />
            </Button>
          </div>
        )

      case 'error_parse': {
        const correct = errorChoice === step.answer
        return (
          <div className="orientation-error-parser">
            <pre><code>{step.error_text}</code></pre>
            <div className="orientation-choice-row" role="group" aria-label="Choose the part that failed">
              {['subcommand', 'flag', 'repository', 'argument'].map((choice) => (
                <button
                  key={choice}
                  type="button"
                  className={cn(errorChoice === choice && 'is-selected', errorChoice === choice && !correct && 'is-error')}
                  aria-pressed={errorChoice === choice}
                  onClick={() => setErrorChoice(choice)}
                >
                  {choice}
                </button>
              ))}
            </div>
            <p className={cn('orientation-interaction-status', correct && 'is-success')} aria-live="polite">
              {!errorChoice ? 'Choose the command context named by the error.' : correct ? 'Correct — Git cannot find repository metadata here.' : 'Not quite. Read what Git says it cannot find.'}
            </p>
            <Button type="button" disabled={!correct} onClick={proceed}>
              Complete error check <ChevronRight aria-hidden="true" />
            </Button>
          </div>
        )
      }

      case 'platform_panel':
        return (
          <div className="orientation-interaction-stack">
            <PlatformWorkspaceDiagram activeHotspot={activeHotspot} />
            {step.body ? <p className="orientation-support-copy">{step.body}</p> : null}
            <div className="orientation-token-row" role="group" aria-label="Workspace areas to inspect">
              {(step.hotspots ?? []).map((spot) => (
                <button
                  key={spot}
                  type="button"
                  className={cn(activeHotspot === spot && 'is-selected', visitedHotspots.has(spot) && 'is-visited')}
                  aria-pressed={activeHotspot === spot}
                  onClick={() => {
                    setActiveHotspot(spot)
                    setVisitedHotspots((current) => addToSet(current, spot))
                  }}
                >
                  {visitedHotspots.has(spot) ? <Check aria-hidden="true" /> : null}
                  {spot.replace('_', ' ')}
                </button>
              ))}
            </div>
            <p className="orientation-interaction-status" aria-live="polite">{visitedHotspots.size} of {step.hotspots?.length ?? 0} areas inspected</p>
            <Button type="button" disabled={visitedHotspots.size < (step.hotspots?.length ?? 0)} onClick={proceed}>
              Complete walkthrough <ChevronRight aria-hidden="true" />
            </Button>
          </div>
        )

      default:
        return <StepAction onClick={proceed}>{hasNextStep ? 'Complete & continue' : 'Mark step complete'}</StepAction>
    }
  })()

  return (
    <section className="orientation-step" data-layout={layout} data-complete={completed || undefined} aria-labelledby={`orientation-step-${step.id}`}>
      <header className="orientation-step-header">
        <div>
          <span>{completed ? <><Check aria-hidden="true" /> Completed</> : 'Current interaction'}</span>
          <h3 id={`orientation-step-${step.id}`}>{step.title}</h3>
        </div>
        <p>{step.prompt}</p>
      </header>
      <div className="orientation-step-content">{content}</div>
    </section>
  )
}
