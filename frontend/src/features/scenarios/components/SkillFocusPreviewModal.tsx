import { useMemo, useState } from 'react'

import type { RepositorySnapshot } from '@/features/practice/types'
import { DemoCommandInput } from '@/features/scenarios/components/DemoCommandInput'
import { DemoExplanationPanel } from '@/features/scenarios/components/DemoExplanationPanel'
import { DemoLiveDagPanel } from '@/features/scenarios/components/DemoLiveDagPanel'
import { PreviewNavigationControls } from '@/features/scenarios/components/PreviewNavigationControls'
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
  const difficultyLabel = difficulty.difficulty.charAt(0).toUpperCase() + difficulty.difficulty.slice(1)

  function applyStep(nextIndex: number) {
    const step = steps[nextIndex]
    if (!step) return
    setSnapshot(isRepositorySnapshot(step.repository_state) ? step.repository_state : initialSnapshot)
    setExplanation(step.explanation)
    setStepIndex(nextIndex)
  }

  function runDemoCommand(command: string) {
    const normalizedCommand = normalize(command)
    const nextIndex = steps.findIndex((step) => normalize(step.command) === normalizedCommand)
    if (nextIndex >= 0) {
      applyStep(nextIndex)
      return
    }
    if ((scenario.safe_demo_commands ?? []).some((safeCommand) => normalize(safeCommand) === normalizedCommand)) {
      setExplanation('That safe demo command is available for exploration; this preview has no additional visual change for it.')
      return
    }
    setExplanation('This preview only accepts the listed safe demo commands. It does not run real scenario commands or evaluate answers.')
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
            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">{scenario.short_explanation}</p>
          </div>
          <div className="flex flex-wrap justify-end gap-2">
            <Badge variant="blue">{difficultyLabel}</Badge>
            <Badge variant="outline">{actionCopy[action]}</Badge>
          </div>
        </header>

        <section className="grid gap-3 rounded-lg border border-border bg-secondary/20 p-4">
          <div>
            <div className="text-sm font-bold">Short concept explanation</div>
            <p className="mt-1 text-sm leading-6 text-muted-foreground">{scenario.short_explanation}</p>
          </div>
          <div className="grid gap-2 text-sm leading-6">
            <div>
              <span className="font-semibold">Skill focus: </span>
              <span className="text-muted-foreground">{scenario.focus}</span>
            </div>
            {scenario.primary_focus_commands.length ? (
              <div>
                <span className="font-semibold">
                  {scenario.primary_focus_commands.length === 1 ? 'Focus command: ' : 'Focus commands: '}
                </span>
                <span className="font-mono text-muted-foreground">{scenario.primary_focus_commands.join(', ')}</span>
              </div>
            ) : null}
            {scenario.supporting_inspection_commands.length ? (
              <div>
                <span className="font-semibold">Supporting inspection commands: </span>
                <span className="font-mono text-muted-foreground">{scenario.supporting_inspection_commands.join(', ')}</span>
              </div>
            ) : null}
          </div>
        </section>

        <section className="grid grid-cols-[minmax(0,1.05fr)_minmax(18rem,0.75fr)] gap-4 max-lg:grid-cols-1">
          <DemoLiveDagPanel snapshot={snapshot} />
          <DemoExplanationPanel explanation={explanation} snapshot={snapshot} />
        </section>

        <DemoCommandInput safeCommands={scenario.safe_demo_commands ?? []} onCommand={runDemoCommand} />

        <p className="rounded-md border border-border bg-background/40 p-3 text-xs leading-5 text-muted-foreground">
          Preview commands use demo-only state. They do not start the scenario, count commands, affect CAR/SCR/RTA, change retry
          counts, create evaluator logs, or reveal the real scenario state.
        </p>

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
