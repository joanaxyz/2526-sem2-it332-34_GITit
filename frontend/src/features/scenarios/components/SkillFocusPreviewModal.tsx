import { useMemo, useState } from 'react'

import type { RepositorySnapshot } from '@/features/practice/types'
import type { TerminalLine } from '@/features/practice/types'
import { TerminalPanel } from '@/features/practice/components/TerminalPanel'
import { DemoExplanationPanel } from '@/features/scenarios/components/DemoExplanationPanel'
import { DemoLiveDagPanel } from '@/features/scenarios/components/DemoLiveDagPanel'
import { PreviewNavigationControls } from '@/features/scenarios/components/PreviewNavigationControls'
import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import type { DifficultyAccess, DifficultyActionIntent, ScenarioSkillFocus } from '@/features/scenarios/types'
import { Badge } from '@/shared/components/Badge'
import { Modal } from '@/shared/components/Modal'

const emptyDemoSnapshot: RepositorySnapshot = {
  commits: [],
  branches: { 'demo-main': null },
  head: { type: 'branch', name: 'demo-main', target: null },
  staging: {},
  working_tree: {},
  conflicts: [],
}

const actionCopy: Record<DifficultyActionIntent, string> = {
  start: 'New practice session',
  continue: 'Resume existing practice session',
  review: 'Playable Review Mode session',
  retry: 'Retry practice attempt',
}

const demoBootLines: TerminalLine[] = [
  { id: 'demo-boot-1', kind: 'system', text: 'Demo repository loaded. This is a warm-up only.' },
  { id: 'demo-boot-2', kind: 'output', text: 'Try a safe demo command to see simulated output.' },
]

export function SkillFocusPreviewModal({
  scenario,
  difficulty,
  action,
  isProceeding,
  onClose,
  onProceed,
}: {
  scenario: ScenarioSkillFocus
  difficulty: DifficultyAccess
  action: DifficultyActionIntent
  isProceeding: boolean
  onClose: () => void
  onProceed: () => void
}) {
  const initialSnapshot = useMemo(
    () => (isRepositorySnapshot(scenario.demo_repository_state) ? scenario.demo_repository_state : emptyDemoSnapshot),
    [scenario.demo_repository_state],
  )
  const steps = scenario.demo_explanation_steps ?? []
  const [snapshot, setSnapshot] = useState<RepositorySnapshot>(initialSnapshot)
  const [explanation, setExplanation] = useState(scenario.short_explanation)
  const [stepIndex, setStepIndex] = useState(-1)
  const [terminalLines, setTerminalLines] = useState<TerminalLine[]>(demoBootLines)
  const [isRunningDemo, setIsRunningDemo] = useState(false)
  const difficultyLabel = difficulty.difficulty.charAt(0).toUpperCase() + difficulty.difficulty.slice(1)

  function applyStep(nextIndex: number) {
    const step = steps[nextIndex]
    if (!step) return
    setSnapshot(isRepositorySnapshot(step.repository_state) ? step.repository_state : initialSnapshot)
    setExplanation(step.explanation)
    setStepIndex(nextIndex)
  }

  async function runDemoCommand(command: string) {
    setTerminalLines((items) => [...items, { id: crypto.randomUUID(), kind: 'input', text: command }])
    setIsRunningDemo(true)
    const normalizedCommand = normalize(command)
    const nextIndex = steps.findIndex((step) => normalize(step.command) === normalizedCommand)

    try {
      const response = await scenariosApi.submitDemoCommand(scenario.slug, { command, repository_state: snapshot })
      if (isRepositorySnapshot(response.repository_state)) {
        setSnapshot(response.repository_state)
      }
      setTerminalLines((items) => [...items, { id: crypto.randomUUID(), kind: 'output', text: response.terminal_output }])
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Could not run demo command.'
      setTerminalLines((items) => [...items, { id: crypto.randomUUID(), kind: 'warning', text: message }])
    } finally {
      setIsRunningDemo(false)
    }

    if (nextIndex >= 0) {
      applyStep(nextIndex)
      return
    }
    if ((scenario.safe_demo_commands ?? []).some((safeCommand) => normalize(safeCommand) === normalizedCommand)) return
    setExplanation('This preview only accepts the listed safe demo commands. It does not evaluate answers.')
  }

  return (
    <Modal
      open
      title="Skill Focus Preview"
      onClose={onClose}
      className="max-h-[92vh] w-full max-w-6xl overflow-hidden"
      contentClassName="max-h-[calc(92vh-4.5rem)] overflow-auto p-5"
    >
      <div className="space-y-5">
        <header className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">Scenario skill focus</p>
            <h3 className="mt-1 text-2xl font-extrabold tracking-tight">{scenario.title}</h3>
          </div>
          <div className="flex flex-wrap justify-end gap-2">
            <Badge variant="blue">{difficultyLabel}</Badge>
            <Badge variant="outline">{actionCopy[action]}</Badge>
          </div>
        </header>

        <section className="grid gap-3 rounded-lg border border-border bg-secondary/20 p-4">
          <p className="text-sm leading-6 text-muted-foreground">{scenario.short_explanation}</p>

          {scenario.primary_focus_commands.length || scenario.supporting_inspection_commands.length ? (
            <div className="grid gap-2 text-sm leading-6">
              {scenario.primary_focus_commands.length ? (
                <div>
                  <span className="font-semibold">
                    {scenario.primary_focus_commands.length === 1 ? 'Focus command: ' : 'Focus commands: '}
                  </span>
                  <span className="font-mono text-muted-foreground">{scenario.primary_focus_commands.join(', ')}</span>
                </div>
              ) : null}
            </div>
          ) : null}

          <CommandQuickReference commands={scenario.primary_focus_commands ?? []} />
        </section>

        <section className="grid grid-cols-[minmax(0,1.05fr)_minmax(18rem,0.75fr)] gap-4 max-lg:grid-cols-1">
          <DemoLiveDagPanel snapshot={snapshot} />
          <DemoExplanationPanel explanation={explanation} snapshot={snapshot} />
        </section>

        <div className="grid gap-3">
          <TerminalPanel
            title="Demo terminal (simulated Git)"
            className="h-56"
            disabled={isRunningDemo}
            lines={terminalLines}
            onCommand={runDemoCommand}
          />
          {scenario.safe_demo_commands?.length ? (
            <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
              <span className="font-semibold">Safe demo commands:</span>
              <span className="font-mono">{scenario.safe_demo_commands.join(' · ')}</span>
            </div>
          ) : null}
        </div>

        <PreviewNavigationControls
          canGoPrevious={stepIndex > 0}
          canGoNext={steps.length > 0 && stepIndex < steps.length - 1}
          isProceeding={isProceeding}
          onPrevious={() => applyStep(stepIndex - 1)}
          onNext={() => applyStep(stepIndex + 1)}
          onSkip={onProceed}
          onStartPractice={onProceed}
        />
      </div>
    </Modal>
  )
}

function normalize(command: string) {
  return command.trim().replace(/\s+/g, ' ').toLowerCase()
}

function isRepositorySnapshot(value: RepositorySnapshot | Record<string, unknown> | null | undefined): value is RepositorySnapshot {
  return Boolean(value && Array.isArray((value as RepositorySnapshot).commits) && (value as RepositorySnapshot).head)
}

function CommandQuickReference({ commands }: { commands: string[] }) {
  const items = commands
    .map((command) => quickReferenceFor(command))
    .filter((item): item is NonNullable<ReturnType<typeof quickReferenceFor>> => Boolean(item))
  if (!items.length) return null

  return (
    <div className="rounded-md border border-border bg-background/40 p-3">
      <div className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">Command quick reference</div>
      <div className="grid gap-3 md:grid-cols-3">
        {items.map((item) => (
          <div className="rounded-md border border-border bg-secondary/20 p-3" key={item.key}>
            <div className="font-mono text-sm font-semibold text-foreground">{item.title}</div>
            <div className="mt-2 space-y-1 text-xs leading-5 text-muted-foreground">
              {item.syntax.map((line) => (
                <div className="font-mono" key={line}>
                  {line}
                </div>
              ))}
              <p className="mt-2 text-xs leading-5 text-muted-foreground">{item.note}</p>
            </div>
          </div>
        ))}
      </div>
      <p className="mt-3 text-xs leading-5 text-muted-foreground">
        This is a command warm-up only. It does not reveal the scenario setup or a correct command sequence.
      </p>
    </div>
  )
}

function quickReferenceFor(command: string) {
  const normalized = normalize(command)
  if (normalized === 'git status') {
    return {
      key: 'git-status',
      title: 'git status',
      syntax: ['git status'],
      note: 'Shows working tree vs staging area state so you can name what changed before acting.',
    }
  }
  if (normalized === 'git add') {
    return {
      key: 'git-add',
      title: 'git add',
      syntax: ['git add <path>', 'git add .', 'git add -A'],
      note: 'Stages selected changes. Use paths when you want a selective commit; use "." / "-A" only when you intend to stage everything.',
    }
  }
  if (normalized === 'git commit') {
    return {
      key: 'git-commit',
      title: 'git commit',
      syntax: ['git commit -m "message"', 'git commit'],
      note: 'Creates a commit from staged content. The -m flag sets the commit message inline.',
    }
  }
  return null
}
