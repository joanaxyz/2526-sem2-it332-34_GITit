import { useCallback, useMemo, useState } from 'react'

import { LiveDagPanel } from '@/features/practice/components/LiveDagPanel'
import { TerminalPanel } from '@/features/practice/components/TerminalPanel'
import type { TerminalLine } from '@/features/practice/types'
import { modulesApi } from '@/features/modules/api/modulesApi'
import type { OrientationCommandResult, OrientationStep } from '@/features/modules/orientation/types'
import { normalizeBuilderCommand } from '@/features/modules/orientation/types'
import { CentralizedDistributedDiagram } from '@/features/modules/orientation/visuals/CentralizedDistributedDiagram'
import { CommitAnatomyDiagram, CommitChainDiagram } from '@/features/modules/orientation/visuals/CommitChainDiagram'
import { FourAreaPipelineDiagram } from '@/features/modules/orientation/visuals/FourAreaPipelineDiagram'
import { PlatformWorkspaceDiagram } from '@/features/modules/orientation/visuals/PlatformWorkspaceDiagram'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { LoadingState } from '@/shared/components/LoadingState'
import { cn } from '@/shared/utils/cn'

function shellOutput(command: string, cwd: string) {
  const normalized = command.trim().toLowerCase()
  if (normalized === 'pwd') return cwd
  if (normalized.startsWith('cat readme.md')) return 'hello'
  return ''
}

function matchesPrefixes(command: string, prefixes: string[] | undefined) {
  const normalized = command.trim().toLowerCase()
  return (prefixes ?? []).some((prefix) => normalized.startsWith(prefix.toLowerCase()))
}

export function OrientationStepView({
  step,
  layout,
  sessionId,
  sessionLoading = false,
  onStepComplete,
  hasNextStep,
  onContinueToNext,
}: {
  step: OrientationStep
  layout: string
  sessionId: number | null
  sessionLoading?: boolean
  onStepComplete: () => void
  hasNextStep: boolean
  onContinueToNext: () => void
}) {
  const [done, setDone] = useState(false)
  const [hint, setHint] = useState<string | null>(null)
  const [lines, setLines] = useState<TerminalLine[]>([])
  const [processing, setProcessing] = useState(false)
  const [pipelineStage, setPipelineStage] = useState(0)
  const [selectedCompare, setSelectedCompare] = useState<string | null>(null)
  const [matchSelections, setMatchSelections] = useState<Record<string, string>>({})
  const [matchRevealed, setMatchRevealed] = useState(false)
  const [anatomyPart, setAnatomyPart] = useState<string | null>(null)
  const [immutabilityToggled, setImmutabilityToggled] = useState(false)
  const [builderParts, setBuilderParts] = useState<string[]>([])
  const [visitedHotspots, setVisitedHotspots] = useState<Set<string>>(new Set())
  const [activeHotspot, setActiveHotspot] = useState<string | null>(null)
  const [shellCwd, setShellCwd] = useState('/home/student')
  const [shellTree, setShellTree] = useState<string[]>(['/home/student'])
  const [shellReadmeContent, setShellReadmeContent] = useState('')

  const lineId = useCallback(() => crypto.randomUUID(), [])

  const complete = useCallback(() => {
    setDone(true)
    onStepComplete()
  }, [onStepComplete])
  const proceed = useCallback(() => {
    complete()
    if (hasNextStep) onContinueToNext()
  }, [complete, hasNextStep, onContinueToNext])

  const appendLines = useCallback(
    (entries: Array<{ kind: TerminalLine['kind']; text: string }>) => {
      setLines((current) => [
        ...current,
        ...entries.map((entry) => ({ id: lineId(), kind: entry.kind, text: entry.text })),
      ])
    },
    [lineId],
  )

  const handleGitCommand = useCallback(
    async (command: string) => {
      if (!sessionId) {
        setHint('Session is not ready. Refresh the page.')
        return
      }
      setProcessing(true)
      setHint(null)
      appendLines([{ kind: 'input', text: command }])
      try {
        const result: OrientationCommandResult = await modulesApi.submitOrientationCommand(
          sessionId,
          command,
          step.id,
        )
        const stderrIsDuplicate = Boolean(result.stderr) && result.stderr.trim() === (result.output ?? '').trim()
        const shouldShowWarning = !result.accepted && Boolean(result.stderr) && !stderrIsDuplicate
        if (result.output) appendLines([{ kind: result.accepted || !result.exit_code ? 'output' : 'warning', text: result.output }])
        if (shouldShowWarning) appendLines([{ kind: 'warning', text: result.stderr }])
        if (result.accepted) {
          appendLines([{ kind: 'success', text: 'Step complete.' }])
          complete()
        } else {
          setHint(result.hint ?? step.hint ?? 'Try again.')
        }
      } catch (error) {
        setHint(error instanceof Error ? error.message : 'Command failed.')
      } finally {
        setProcessing(false)
      }
    },
    [appendLines, complete, sessionId, step.hint, step.id],
  )

  const handleShellCommand = useCallback(
    (command: string) => {
      const normalized = command.trim().toLowerCase()
      appendLines([{ kind: 'input', text: command }])
      if (!matchesPrefixes(command, step.accept_prefixes)) {
        setHint(step.hint ?? 'Check the step instructions.')
        return
      }
      setHint(null)
      let output = shellOutput(command, shellCwd)
      if (normalized === 'mkdir practice') {
        const practicePath = `${shellCwd}/practice`
        if (!shellTree.includes(practicePath)) {
          setShellTree((tree) => [...tree, practicePath])
          output = `created directory: ${practicePath}`
        } else {
          output = `mkdir: cannot create directory '${practicePath}': File exists`
        }
      }
      if (normalized.startsWith('cd ')) {
        const target = normalized.replace('cd ', '').trim()
        if (target === 'practice') {
          const nextCwd = `${shellCwd}/practice`
          setShellCwd(nextCwd)
          output = `current directory: ${nextCwd}`
        }
      }
      if (normalized === 'ls -la' || normalized === 'ls -a -l') {
        const practicePath = '/home/student/practice'
        const inPractice = shellCwd === practicePath
        output = inPractice
          ? `total 4\n.\n..\nreadme.md`
          : `total 8\n.\n..\npractice`
      }
      if (normalized === 'touch readme.md') {
        output = `created file: ${shellCwd}/readme.md`
      }
      if (normalized === 'echo "hello" > readme.md' || normalized === 'echo hello > readme.md') {
        setShellReadmeContent('hello')
        output = `wrote to ${shellCwd}/readme.md`
      }
      if (normalized === 'cat readme.md') {
        output = shellReadmeContent || 'hello'
      }
      if (output) appendLines([{ kind: 'output', text: output }])
      appendLines([{ kind: 'success', text: 'Step complete.' }])
      complete()
    },
    [appendLines, complete, shellCwd, shellReadmeContent, shellTree, step.accept_prefixes, step.hint],
  )

  const builderTarget = normalizeBuilderCommand(step.target ?? '')
  const builderBuilt = useMemo(() => normalizeBuilderCommand(builderParts.join(' ')), [builderParts])
  const allPairsSelected =
    (step.pairs ?? []).length > 0 &&
    (step.pairs ?? []).every((pair) => Boolean(matchSelections[pair.scenario]?.trim()))

  const content = (() => {
    switch (step.kind) {
      case 'continue':
        return (
          <div className="grid gap-4">
            {step.body ? <p className="text-sm leading-7 text-muted-foreground">{step.body}</p> : null}
            <Button type="button" onClick={proceed}>
              Continue
            </Button>
          </div>
        )
      case 'compare_toggle':
        return (
          <div className="grid gap-4">
            <CentralizedDistributedDiagram
              active={selectedCompare === 'centralized' ? 'centralized' : selectedCompare === 'distributed' ? 'distributed' : null}
            />
            <div className="grid gap-3 sm:grid-cols-2">
            {(step.options ?? []).map((option) => (
              <button
                key={option.id}
                type="button"
                className={cn(
                  'rounded-lg border p-4 text-left transition',
                  selectedCompare === option.id ? 'border-primary bg-primary/10' : 'border-border bg-secondary/30',
                )}
                onClick={() => setSelectedCompare(option.id)}
              >
                <div className="font-semibold">{option.label}</div>
                {selectedCompare === option.id ? (
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">{option.detail}</p>
                ) : null}
              </button>
            ))}
            <Button
              type="button"
              className="sm:col-span-2"
              disabled={!selectedCompare}
              onClick={proceed}
            >
              Continue
            </Button>
            </div>
          </div>
        )
      case 'match_reveal':
        return (
          <div className="grid gap-3">
            {(step.pairs ?? []).map((pair) => (
              <div key={pair.scenario} className="flex flex-wrap items-center gap-2 rounded-md border border-border p-3">
                <span className="flex-1 text-sm">{pair.scenario}</span>
                <select
                  className="rounded border border-border bg-background px-2 py-1 text-sm"
                  value={matchSelections[pair.scenario] ?? ''}
                  onChange={(event) =>
                    setMatchSelections((current) => ({ ...current, [pair.scenario]: event.target.value }))
                  }
                >
                  <option value="">Choose…</option>
                  <option value="history">History</option>
                  <option value="collaboration">Collaboration</option>
                  <option value="recovery">Recovery</option>
                </select>
              </div>
            ))}
            <Button
              type="button"
              variant="outline"
              onClick={() => setMatchRevealed(true)}
              disabled={!allPairsSelected}
            >
              Reveal answers
            </Button>
            {matchRevealed ? (
              <div className="text-sm text-muted-foreground">
                {(step.pairs ?? []).map((pair) => (
                  <div key={pair.scenario}>
                    {pair.scenario} → <strong>{pair.problem}</strong>
                  </div>
                ))}
                <Button type="button" className="mt-3" onClick={proceed}>
                  Continue
                </Button>
              </div>
            ) : null}
          </div>
        )
      case 'git_command':
        return (
          <div className="grid gap-2">
            {sessionLoading ? <LoadingState label="Preparing repository" variant="compact" /> : null}
            <TerminalPanel
              className="h-64"
              lines={lines}
              processing={processing}
              disabled={done || sessionLoading || !sessionId}
              onCommand={handleGitCommand}
              title="Git"
            />
          </div>
        )
      case 'shell_command':
        return (
          <div className="grid gap-3 lg:grid-cols-[12rem_1fr]">
            <Card className="p-3 font-mono text-xs shadow-none">
              <div className="mb-2 font-semibold text-foreground">Folders</div>
              {shellTree.map((path) => (
                <div key={path} className="truncate text-muted-foreground">
                  {path}
                </div>
              ))}
            </Card>
            <TerminalPanel
              className="h-56"
              lines={lines}
              processing={processing}
              disabled={done}
              onCommand={handleShellCommand}
              title="Shell"
            />
          </div>
        )
      case 'pipeline':
        return (
          <div className="grid gap-4">
            <FourAreaPipelineDiagram activeIndex={pipelineStage} />
            <Button
              type="button"
              onClick={() => {
                if (pipelineStage + 1 >= (step.stages?.length ?? 0)) complete()
                else setPipelineStage((value) => value + 1)
              }}
            >
              {pipelineStage + 1 >= (step.stages?.length ?? 0) ? 'Finish pipeline' : 'Move file to next area'}
            </Button>
          </div>
        )
      case 'status_annotate':
        return (
          <div className="grid gap-3">
            <pre className="overflow-auto rounded-lg border border-border bg-black/40 p-4 font-mono text-xs leading-6 text-muted-foreground">
              {step.sample_output}
            </pre>
            <Button type="button" onClick={proceed}>
              Continue
            </Button>
          </div>
        )
      case 'anatomy':
        return (
          <div className="grid gap-4">
            <CommitAnatomyDiagram highlight={anatomyPart} />
            <div className="flex flex-wrap gap-2">
              {(step.parts ?? []).map((part) => (
                <button
                  key={part}
                  type="button"
                  className={cn(
                    'rounded-md border px-3 py-1.5 text-sm capitalize',
                    anatomyPart === part ? 'border-primary bg-primary/10' : 'border-border',
                  )}
                  onClick={() => setAnatomyPart(part)}
                >
                  {part}
                </button>
              ))}
            </div>
            <Button type="button" disabled={!anatomyPart} onClick={proceed}>
              Continue
            </Button>
          </div>
        )
      case 'immutability_demo':
        return (
          <div className="grid gap-3">
            <p className="text-sm text-muted-foreground">
              Amending creates a <strong>new</strong> commit; the original stays in history unchanged.
            </p>
            <CommitChainDiagram amended={immutabilityToggled} />
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setImmutabilityToggled(true)
                complete()
              }}
            >
              Simulate amend and update commit hash
            </Button>
          </div>
        )
      case 'dag_explore':
        return (
          <div className="grid gap-3">
            {step.initial_state ? (
              <LiveDagPanel snapshot={step.initial_state} title="Commit graph" className="min-h-[220px]" />
            ) : null}
            <p className="text-sm text-muted-foreground">
              Find branch labels <strong>main</strong> and <strong>feature</strong>, and note where HEAD points.
            </p>
            <Button type="button" onClick={proceed}>
              Continue
            </Button>
          </div>
        )
      case 'command_builder':
        return (
          <div className="grid gap-3">
            <div className="flex flex-wrap gap-2">
              {['git', 'commit', 'log', 'status', '-m', '--oneline', '--graph', '--all', '"message"'].map((token) => (
                <Button
                  key={token}
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() => setBuilderParts((current) => [...current, token])}
                >
                  {token}
                </Button>
              ))}
              <Button type="button" size="sm" variant="ghost" onClick={() => setBuilderParts([])}>
                Clear
              </Button>
            </div>
            <pre className="rounded-md border border-border bg-black/40 p-3 font-mono text-sm">{builderBuilt || '…'}</pre>
            <Button
              type="button"
              disabled={!builderTarget || builderBuilt !== builderTarget}
              onClick={proceed}
            >
              Continue
            </Button>
          </div>
        )
      case 'error_parse':
        return (
          <div className="grid gap-3">
            <pre className="rounded-md border border-border bg-black/40 p-3 font-mono text-xs text-warning">
              {step.error_text}
            </pre>
            <div className="flex flex-wrap gap-2">
              {['subcommand', 'flag', 'repository', 'argument'].map((choice) => (
                <Button
                  key={choice}
                  type="button"
                  variant="outline"
                  onClick={() => {
                    if (choice === step.answer) proceed()
                    else setHint('Read which part of the command context failed.')
                  }}
                >
                  {choice}
                </Button>
              ))}
            </div>
          </div>
        )
      case 'platform_panel':
        return (
          <div className="grid gap-3">
            <PlatformWorkspaceDiagram activeHotspot={activeHotspot} />
            {step.body ? <p className="text-sm leading-7 text-muted-foreground">{step.body}</p> : null}
            <div className="flex flex-wrap gap-2">
              {(step.hotspots ?? []).map((spot) => (
                <Button
                  key={spot}
                  type="button"
                  size="sm"
                  variant={activeHotspot === spot ? 'default' : 'outline'}
                  onClick={() => {
                    setActiveHotspot(spot)
                    setVisitedHotspots((current) => new Set([...current, spot]))
                  }}
                >
                  {spot.replace('_', ' ')}
                </Button>
              ))}
            </div>
            <Button type="button" disabled={visitedHotspots.size < (step.hotspots?.length ?? 0)} onClick={proceed}>
              Continue
            </Button>
          </div>
        )
      default:
        return (
          <Button type="button" onClick={proceed}>
            Continue
          </Button>
        )
    }
  })()

  return (
    <div
      className={cn(
        'grid gap-4',
        layout === 'guide_terminal' && step.kind === 'continue' && 'lg:col-span-1',
        layout === 'guide_terminal' && step.kind === 'git_command' && 'lg:col-span-1',
      )}
    >
      <div>
        <h3 className="text-lg font-bold">{step.title}</h3>
        <p className="mt-1 text-sm leading-6 text-muted-foreground">{step.prompt}</p>
      </div>
      {hint ? <p className="text-sm text-accent">{hint}</p> : null}
      {content}
      {done ? <p className="text-sm text-primary">Step completed.</p> : null}
    </div>
  )
}
