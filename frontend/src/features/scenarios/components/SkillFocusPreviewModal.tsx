import { useQuery } from '@tanstack/react-query'
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

const demoBootLines: TerminalLine[] = [
  { id: 'demo-boot-1', kind: 'system', text: 'Demo repository loaded. This is a warm-up only.' },
  { id: 'demo-boot-2', kind: 'output', text: 'Read the command behavior first, then try a safe demo command.' },
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
  const detailQuery = useQuery({
    queryKey: ['skill-focus', scenario.slug],
    queryFn: () => scenariosApi.getSkillFocus(scenario.slug),
    staleTime: 5 * 60 * 1000,
  })

  if (detailQuery.isLoading) {
    return (
      <Modal
        open
        title="Command preview"
        onClose={onClose}
        className="w-full max-w-xl"
        contentClassName="p-5"
      >
        <div className="py-8 text-center text-sm text-muted-foreground">Loading preview...</div>
      </Modal>
    )
  }

  if (detailQuery.isError || !detailQuery.data) {
    return (
      <Modal
        open
        title="Command preview"
        onClose={onClose}
        className="w-full max-w-xl"
        contentClassName="p-5"
      >
        <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm leading-6 text-destructive">
          {detailQuery.error?.message ?? 'Could not load the command preview.'}
        </div>
      </Modal>
    )
  }

  return (
    <SkillFocusPreviewContent
      scenario={detailQuery.data}
      difficulty={difficulty}
      action={action}
      isProceeding={isProceeding}
      onClose={onClose}
      onProceed={onProceed}
    />
  )
}

function SkillFocusPreviewContent({
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
  const steps = useMemo(
    () => normalizeDemoSteps(scenario.command_preview?.demo_steps ?? scenario.demo_explanation_steps, initialSnapshot, scenario.short_explanation),
    [initialSnapshot, scenario.command_preview?.demo_steps, scenario.demo_explanation_steps, scenario.short_explanation],
  )
  const supportedDemoCommands = scenario.command_preview?.supported_demo_commands ?? scenario.safe_demo_commands ?? []
  const syntaxExamples = scenario.command_preview?.syntax_examples ?? []
  const commonMistakes = scenario.command_preview?.common_mistakes ?? []
  const [snapshot, setSnapshot] = useState<RepositorySnapshot>(initialSnapshot)
  const [explanation, setExplanation] = useState(commandBehaviorSummary(scenario))
  const [stepIndex, setStepIndex] = useState(0)
  const [terminalLines, setTerminalLines] = useState<TerminalLine[]>(demoBootLines)
  const [isRunningDemo, setIsRunningDemo] = useState(false)
  const difficultyLabel = difficulty.difficulty.charAt(0).toUpperCase() + difficulty.difficulty.slice(1)
  const startLabel =
    action === 'review'
        ? 'Open review'
        : action === 'continue' || action === 'resume'
          ? 'Continue'
        : action === 'retry'
          ? 'Retry scenario'
          : 'Start scenario'

  function applyDemoStep(nextIndex: number) {
    const step = steps[nextIndex]
    if (!step) return
    setSnapshot(isRepositorySnapshot(step.repository_state) ? step.repository_state : initialSnapshot)
    setExplanation(step.explanation)
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
      applyDemoStep(nextIndex)
      return
    }
    if (supportedDemoCommands.some((safeCommand) => normalize(safeCommand) === normalizedCommand)) return
    setExplanation('This preview accepts the listed demo commands. It teaches command behavior without evaluating the scenario answer.')
  }

  const previewSteps = [
    'What this command is for',
    'Before state',
    'Try command in demo terminal',
    'After state / DAG change',
    'Common mistake',
    'Proceed to scenario',
  ]
  const currentStep = previewSteps[stepIndex] ?? previewSteps[0]

  return (
    <Modal
      open
      title="Command preview"
      onClose={onClose}
      className="max-h-[92vh] w-full max-w-6xl overflow-hidden"
      contentClassName="max-h-[calc(92vh-4.5rem)] overflow-auto p-5"
    >
      <div className="space-y-5">
        <header className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">Command preview</p>
            <h3 className="mt-1 text-2xl font-extrabold tracking-tight">{scenario.title}</h3>
          </div>
          <div className="flex flex-wrap justify-end gap-2">
            <Badge variant="blue">{difficultyLabel}</Badge>
            {scenario.command_preview?.diagnostic ? <Badge variant="outline">Diagnostic</Badge> : null}
          </div>
        </header>

        <section className="grid grid-cols-[13rem_minmax(0,1fr)] gap-4 max-lg:grid-cols-1">
          <nav className="grid content-start gap-2" aria-label="Command preview steps">
            {previewSteps.map((label, index) => (
              <button
                className={`rounded-md border px-3 py-2 text-left text-sm transition ${
                  index === stepIndex
                    ? 'border-primary bg-primary/10 font-semibold text-foreground'
                    : 'border-border bg-secondary/20 text-muted-foreground hover:bg-secondary'
                }`}
                key={label}
                type="button"
                onClick={() => setStepIndex(index)}
              >
                {index + 1}. {label}
              </button>
            ))}
          </nav>

          <div className="grid gap-4">
            <section className="rounded-md border border-border bg-card p-4">
              <div className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                {currentStep}
              </div>
              <PreviewStepContent
                stepIndex={stepIndex}
                scenario={scenario}
                explanation={explanation}
                snapshot={snapshot}
                syntaxExamples={syntaxExamples}
                supportedDemoCommands={supportedDemoCommands}
                commonMistakes={commonMistakes}
                startLabel={startLabel}
              />
            </section>

            <section className="grid grid-cols-[minmax(0,1fr)_20rem] gap-4 max-xl:grid-cols-1">
              <TerminalPanel
                title="Demo terminal"
                className="h-60"
                disabled={isRunningDemo}
                lines={terminalLines}
                onCommand={runDemoCommand}
              />
              <DemoExplanationPanel explanation={explanation} snapshot={snapshot} />
            </section>
          </div>
        </section>

        <PreviewNavigationControls
          canGoPrevious={stepIndex > 0}
          canGoNext={stepIndex < previewSteps.length - 1}
          isProceeding={isProceeding}
          startLabel={startLabel}
          onPrevious={() => setStepIndex((index) => Math.max(0, index - 1))}
          onNext={() => setStepIndex((index) => Math.min(previewSteps.length - 1, index + 1))}
          onStartPractice={onProceed}
        />
      </div>
    </Modal>
  )
}

function PreviewStepContent({
  stepIndex,
  scenario,
  explanation,
  snapshot,
  syntaxExamples,
  supportedDemoCommands,
  commonMistakes,
  startLabel,
}: {
  stepIndex: number
  scenario: ScenarioSkillFocus
  explanation: string
  snapshot: RepositorySnapshot
  syntaxExamples: string[]
  supportedDemoCommands: string[]
  commonMistakes: string[]
  startLabel: string
}) {
  if (stepIndex === 0) {
    return (
      <div className="grid gap-3">
        <p className="text-sm leading-6 text-muted-foreground">{scenario.short_explanation || explanation}</p>
        <div className="flex flex-wrap gap-2">
          {[...(scenario.primary_focus_commands ?? []), ...(scenario.supporting_inspection_commands ?? [])].map((command) => (
            <span className="rounded-md border border-border bg-secondary/40 px-2 py-1 font-mono text-xs" key={command}>
              {command}
            </span>
          ))}
        </div>
        {syntaxExamples.length ? (
          <div className="grid gap-2">
            <div className="text-sm font-semibold">Syntax examples</div>
            <div className="flex flex-wrap gap-2">
              {syntaxExamples.slice(0, 8).map((syntax) => (
                <code className="rounded-md bg-secondary px-2 py-1 text-xs" key={syntax}>
                  {syntax}
                </code>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    )
  }

  if (stepIndex === 1) {
    return (
      <div className="grid gap-3">
        <p className="text-sm leading-6 text-muted-foreground">Start by reading the repository shape before typing a command.</p>
        <DemoLiveDagPanel snapshot={snapshot} />
      </div>
    )
  }

  if (stepIndex === 2) {
    return (
      <div className="grid gap-3">
        <p className="text-sm leading-6 text-muted-foreground">Try any listed command in the demo terminal. These commands are a warm-up and are not scenario answers.</p>
        <div className="grid max-h-32 gap-2 overflow-auto rounded-md border border-border bg-secondary/20 p-2">
          {supportedDemoCommands.map((command) => (
            <code className="text-xs" key={command}>{command}</code>
          ))}
        </div>
      </div>
    )
  }

  if (stepIndex === 3) {
    return (
      <div className="grid gap-3">
        <p className="text-sm leading-6 text-muted-foreground">{explanation}</p>
        <DemoLiveDagPanel snapshot={snapshot} />
      </div>
    )
  }

  if (stepIndex === 4) {
    return (
      <div className="grid gap-2">
        {(commonMistakes.length ? commonMistakes : ['Skipping inspection before choosing an action.']).map((mistake) => (
          <div className="rounded-md border border-border bg-secondary/30 p-3 text-sm leading-6 text-muted-foreground" key={mistake}>
            {mistake}
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid gap-3">
      <p className="text-sm leading-6 text-muted-foreground">
        The scenario opens as a generated variant with its own paths, messages, and validation rules. Use the command behavior here, then inspect the actual scenario state before acting.
      </p>
      <div className="rounded-md border border-border bg-secondary/30 p-3 text-sm font-semibold">{startLabel}</div>
    </div>
  )
}

type NormalizedDemoStep = {
  command: string
  explanation: string
  repository_state: RepositorySnapshot
}

function normalizeDemoSteps(
  value: unknown,
  fallbackSnapshot: RepositorySnapshot,
  fallbackExplanation?: string,
): NormalizedDemoStep[] {
  if (!Array.isArray(value)) return []
  return value
    .map((item, index): NormalizedDemoStep | null => {
      if (typeof item === 'string') {
        return {
          command: '',
          explanation: item || fallbackExplanation || '',
          repository_state: fallbackSnapshot,
        }
      }
      if (!item || typeof item !== 'object') return null
      const candidate = item as Partial<NormalizedDemoStep>
      return {
        command: typeof candidate.command === 'string' ? candidate.command : '',
        explanation:
          typeof candidate.explanation === 'string' && candidate.explanation.trim()
            ? candidate.explanation
            : fallbackExplanation || `Demo step ${index + 1}`,
        repository_state: isRepositorySnapshot(candidate.repository_state) ? candidate.repository_state : fallbackSnapshot,
      }
    })
    .filter((step): step is NormalizedDemoStep => Boolean(step))
}

function commandBehaviorSummary(scenario: ScenarioSkillFocus) {
  const normalized = normalize(scenario.focus)
  if (normalized === 'git init') {
    return 'git init prepares a folder for Git by creating repository metadata. It does not stage files, commit files, or change file contents.'
  }
  if (normalized === 'git clone') {
    return 'git clone copies a remote repository into a local folder, checks out the default branch, and sets up origin tracking.'
  }
  if (normalized === 'git add') {
    return 'git add moves selected changes from the working tree into the staging area so the next commit can save them.'
  }
  if (normalized === 'git commit') {
    return 'git commit saves the staged snapshot and moves the current branch tip to the new commit.'
  }
  if (normalized === '.gitignore') {
    return '.gitignore teaches Git which untracked local files should be ignored, while already tracked files need an explicit untrack step.'
  }
  if (normalized === 'git add -p') {
    return 'git add -p lets you stage selected hunks, so one file can be split across separate focused commits.'
  }
  if (normalized === 'git commit --amend') {
    return 'git commit --amend replaces the latest local commit with a corrected version instead of creating a separate follow-up commit.'
  }
  if (normalized === 'git restore') {
    return 'git restore can either unstage selected paths or discard selected working-tree changes depending on the flags used.'
  }
  return scenario.short_explanation ?? 'This preview explains the command behavior before you open a generated scenario variant.'
}

function normalize(command: string) {
  return command.trim().replace(/\s+/g, ' ').toLowerCase()
}

function isRepositorySnapshot(value: unknown): value is RepositorySnapshot {
  if (!value || typeof value !== 'object') return false
  const snapshot = value as Partial<RepositorySnapshot>
  return Array.isArray(snapshot.commits) && Boolean((snapshot as RepositorySnapshot).head)
}
