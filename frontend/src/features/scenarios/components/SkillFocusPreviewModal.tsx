import { useQuery } from '@tanstack/react-query'
import { BookOpen, CheckCircle2, CircleAlert, Code2, GitBranch, Play, SquareTerminal } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { useMemo, useState } from 'react'

import type { RepositorySnapshot, TerminalLine } from '@/features/practice/types'
import { TerminalPanel } from '@/features/practice/components/TerminalPanel'
import { DemoLiveDagPanel } from '@/features/scenarios/components/DemoLiveDagPanel'
import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import type {
  CommandPreviewSection,
  DemoExplanationStep,
  DifficultyAccess,
  DifficultyActionIntent,
  ScenarioSkillFocus,
} from '@/features/scenarios/types'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'
import { Modal } from '@/shared/components/Modal'
import { cn } from '@/shared/utils/cn'

const emptyDemoSnapshot: RepositorySnapshot = {
  commits: [],
  branches: { 'demo-main': null },
  head: { type: 'branch', name: 'demo-main', target: null },
  staging: {},
  working_tree: {},
  conflicts: [],
}

const demoBootLines: TerminalLine[] = [
  { id: 'demo-boot-1', kind: 'system', text: 'Inline demo repository loaded.' },
  { id: 'demo-boot-2', kind: 'output', text: 'Run one of the preview commands to watch the shared DAG update.' },
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
  isProceeding?: boolean
  onClose: () => void
  onProceed?: () => void
}) {
  const detailQuery = useQuery({
    queryKey: ['skill-focus', scenario.slug],
    queryFn: () => scenariosApi.getSkillFocus(scenario.slug),
    staleTime: 5 * 60 * 1000,
  })

  if (detailQuery.isLoading) {
    return (
      <Modal open title="Command preview" onClose={onClose} className="w-full max-w-xl" contentClassName="p-5">
        <div className="py-8 text-center text-sm text-muted-foreground">Loading preview...</div>
      </Modal>
    )
  }

  if (detailQuery.isError || !detailQuery.data) {
    return (
      <Modal open title="Command preview" onClose={onClose} className="w-full max-w-xl" contentClassName="p-5">
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
      isProceeding={Boolean(isProceeding)}
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
  onProceed?: () => void
}) {
  const preview = scenario.command_preview
  const initialSnapshot = useMemo(
    () =>
      isRepositorySnapshot(preview?.demo_repository_state)
        ? preview.demo_repository_state
        : isRepositorySnapshot(scenario.demo_repository_state)
          ? scenario.demo_repository_state
          : emptyDemoSnapshot,
    [preview?.demo_repository_state, scenario.demo_repository_state],
  )
  const supportedDemoCommands = useMemo(
    () => preview?.supported_demo_commands ?? scenario.safe_demo_commands ?? [],
    [preview?.supported_demo_commands, scenario.safe_demo_commands],
  )
  const sections = useMemo(
    () => buildPreviewSections(scenario, initialSnapshot),
    [initialSnapshot, scenario],
  )
  const [selectedSectionIndex, setSelectedSectionIndex] = useState(0)
  const [selectedStepIndex, setSelectedStepIndex] = useState(0)
  const selectedSection = sections[selectedSectionIndex] ?? sections[0]
  const selectedSteps = selectedSection?.demo_steps ?? []
  const selectedStep = selectedSteps[selectedStepIndex] ?? selectedSteps[0] ?? null
  const [snapshot, setSnapshot] = useState<RepositorySnapshot>(() => selectedStep?.repository_state ?? initialSnapshot)
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

  function selectSection(nextIndex: number) {
    const section = sections[nextIndex]
    if (!section) return
    const firstStep = section.demo_steps?.[0]
    setSelectedSectionIndex(nextIndex)
    setSelectedStepIndex(0)
    setSnapshot(firstStep?.repository_state ?? initialSnapshot)
  }

  function applyDemoStep(nextIndex: number) {
    const step = selectedSteps[nextIndex]
    if (!step) return
    setSelectedStepIndex(nextIndex)
    setSnapshot(step.repository_state)
  }

  async function runDemoCommand(command: string) {
    setTerminalLines((items) => [...items, { id: crypto.randomUUID(), kind: 'input', text: command }])
    setIsRunningDemo(true)
    const normalizedCommand = normalize(command)
    const nextSectionIndex = sections.findIndex((section) =>
      (section.demo_steps ?? []).some((step) => normalize(step.command) === normalizedCommand),
    )
    const nextStepIndex =
      nextSectionIndex >= 0
        ? (sections[nextSectionIndex].demo_steps ?? []).findIndex((step) => normalize(step.command) === normalizedCommand)
        : -1

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

    if (nextSectionIndex >= 0 && nextStepIndex >= 0) {
      setSelectedSectionIndex(nextSectionIndex)
      setSelectedStepIndex(nextStepIndex)
    }
  }

  return (
    <Modal
      open
      title={preview?.title ?? 'Command preview'}
      onClose={onClose}
      className="max-h-[94vh] w-full max-w-7xl overflow-hidden"
      contentClassName="max-h-[calc(94vh-4.5rem)] overflow-auto p-0 app-scrollbar"
    >
      <div className="grid min-h-0 grid-cols-[18rem_minmax(0,1fr)_22rem] max-xl:grid-cols-[16rem_minmax(0,1fr)] max-lg:grid-cols-1">
        <aside className="border-r border-border bg-secondary/20 p-4 max-lg:border-b max-lg:border-r-0">
          <div className="mb-4">
            <p className="text-xs font-semibold uppercase text-primary">Scenario preview</p>
            <h3 className="mt-1 text-xl font-extrabold leading-tight">{scenario.title}</h3>
            <div className="mt-3 flex flex-wrap gap-2">
              <Badge variant="blue">{difficultyLabel}</Badge>
              <Badge variant="outline">{preview?.focus_label ?? scenario.focus}</Badge>
            </div>
          </div>
          <nav className="grid gap-2" aria-label="Command preview sections">
            {sections.map((section, index) => (
              <button
                aria-pressed={index === selectedSectionIndex}
                className={cn(
                  'rounded-md border px-3 py-3 text-left transition',
                  index === selectedSectionIndex
                    ? 'border-primary bg-primary/10 text-foreground'
                    : 'border-border bg-background/40 text-muted-foreground hover:bg-secondary',
                )}
                key={section.id ?? `${section.title}-${index}`}
                type="button"
                onClick={() => selectSection(index)}
              >
                <span className="block truncate text-sm font-bold">{section.title}</span>
                {section.command ? <span className="mt-1 block truncate font-mono text-xs">{section.command}</span> : null}
              </button>
            ))}
          </nav>
        </aside>

        <main className="min-w-0 p-5">
          <header className="mb-5 rounded-md border border-border bg-card p-4">
            <div className="flex items-start gap-3">
              <div className="grid size-10 shrink-0 place-items-center rounded-md border border-primary/30 bg-primary/10 text-primary">
                <BookOpen className="size-5" />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-semibold text-foreground">{preview?.command_title ?? scenario.title}</p>
                <p className="mt-1 text-sm leading-6 text-muted-foreground">
                  {preview?.intro ?? preview?.short_explanation ?? scenario.short_explanation ?? scenario.summary}
                </p>
                {preview?.purpose ? <p className="mt-2 text-sm leading-6 text-muted-foreground">{preview.purpose}</p> : null}
              </div>
            </div>
          </header>

          <article className="grid gap-4">
            <section className="rounded-md border border-border bg-card p-4">
              <div className="mb-2 flex items-center gap-2 text-sm font-bold">
                <GitBranch className="size-4 text-primary" />
                {selectedSection.title}
              </div>
              <p className="text-sm leading-6 text-muted-foreground">{selectedSection.explanation}</p>
            </section>

            <PreviewList
              icon={Code2}
              title="Syntax examples"
              items={selectedSection.syntax_examples}
              mono
              emptyText="No syntax examples were provided for this section."
            />
            <PreviewList
              icon={CheckCircle2}
              title="What it changes"
              items={selectedSection.what_changes}
              emptyText="This section is informational."
            />
            <PreviewList
              icon={CircleAlert}
              title="What it does not change"
              items={selectedSection.what_does_not_change}
              emptyText="No boundaries were provided for this section."
            />
            <PreviewList
              icon={CircleAlert}
              title="Common mistakes"
              items={selectedSection.common_mistakes}
              emptyText="No common mistakes were provided for this section."
            />
            <PreviewList
              icon={CheckCircle2}
              title="Readiness notes"
              items={selectedSection.readiness_notes}
              emptyText="Review the scenario prompt before starting."
            />
          </article>
        </main>

        <aside className="border-l border-border bg-background p-4 max-xl:col-span-2 max-xl:border-l-0 max-xl:border-t max-lg:col-span-1">
          <div className="mb-3 flex items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2 text-sm font-bold">
                <SquareTerminal className="size-4 text-primary" />
                Shared demo
              </div>
              <p className="mt-1 text-xs leading-5 text-muted-foreground">One demo area updates as you move through the outline.</p>
            </div>
          </div>

          {selectedSteps.length ? (
            <div className="mb-3 flex flex-wrap gap-2">
              {selectedSteps.map((step, index) => (
                <button
                  type="button"
                  key={`${step.command}-${index}`}
                  className={cn(
                    'rounded-sm border px-2 py-1 font-mono text-[11px] transition',
                    index === selectedStepIndex
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border bg-secondary/30 text-muted-foreground hover:text-foreground',
                  )}
                  onClick={() => applyDemoStep(index)}
                >
                  {step.command}
                </button>
              ))}
            </div>
          ) : null}

          <div className="grid gap-3">
            <div className="rounded-md border border-border bg-card p-3">
              <DemoLiveDagPanel snapshot={snapshot} />
            </div>
            <TerminalPanel
              title="Inline command demo"
              className="h-60 rounded-md"
              disabled={isRunningDemo || supportedDemoCommands.length === 0}
              lines={terminalLines}
              onCommand={runDemoCommand}
            />
          </div>
        </aside>
      </div>

      <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-border bg-card/70 px-5 py-4">
        <p className="text-xs leading-5 text-muted-foreground">Use this as a reference before working in the generated repository.</p>
        {onProceed ? (
          <Button type="button" disabled={isProceeding} onClick={onProceed}>
            <Play data-icon="inline-start" />
            {isProceeding ? 'Opening...' : startLabel}
          </Button>
        ) : (
          <Button type="button" variant="outline" onClick={onClose}>
            Close preview
          </Button>
        )}
      </footer>
    </Modal>
  )
}

function PreviewList({
  icon: Icon,
  title,
  items,
  emptyText,
  mono = false,
}: {
  icon: LucideIcon
  title: string
  items?: string[]
  emptyText: string
  mono?: boolean
}) {
  const visibleItems = items?.filter(Boolean) ?? []
  return (
    <section className="rounded-md border border-border bg-card p-4">
      <div className="mb-3 flex items-center gap-2 text-sm font-bold">
        <Icon className="size-4 text-primary" />
        {title}
      </div>
      {visibleItems.length ? (
        <ul className="grid gap-2">
          {visibleItems.map((item) => (
            <li
              className={cn(
                'rounded-sm border border-border bg-secondary/20 px-3 py-2 text-sm leading-6 text-muted-foreground',
                mono && 'font-mono text-xs text-foreground',
              )}
              key={item}
            >
              {item}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm leading-6 text-muted-foreground">{emptyText}</p>
      )}
    </section>
  )
}

function buildPreviewSections(
  scenario: ScenarioSkillFocus,
  fallbackSnapshot: RepositorySnapshot,
): CommandPreviewSection[] {
  const configuredSections = scenario.command_preview?.sections?.filter((section) => section.title && section.explanation) ?? []
  if (configuredSections.length) {
    return configuredSections.map((section, index) => ({
      ...section,
      id: section.id ?? `${normalize(section.title)}-${index}`,
      demo_steps: normalizeDemoSteps(section.demo_steps ?? [], fallbackSnapshot, section.explanation, section.common_mistakes?.[0]),
    }))
  }

  const normalizedSteps = normalizeDemoSteps(
    scenario.command_preview?.demo_steps?.length ? scenario.command_preview.demo_steps : scenario.demo_explanation_steps,
    fallbackSnapshot,
    scenario.command_preview?.short_explanation ?? scenario.short_explanation,
    scenario.command_preview?.common_mistakes?.[0],
  )
  if (normalizedSteps.length) {
    return normalizedSteps.map((step, index) => ({
      id: `${normalize(step.command)}-${index}`,
      title: step.title || step.command,
      command: step.command,
      explanation: step.explanation,
      syntax_examples: [step.command],
      what_changes: scenario.command_preview?.what_changes ?? [],
      what_does_not_change: scenario.command_preview?.what_does_not_change ?? [],
      common_mistakes: step.common_mistake ? [step.common_mistake] : [],
      readiness_notes: scenario.command_preview?.readiness_notes ?? [],
      demo_steps: [step],
    }))
  }

  return [
    {
      id: 'overview',
      title: scenario.focus || 'Scenario focus',
      command: scenario.primary_focus_commands[0],
      explanation: scenario.short_explanation ?? scenario.summary,
      syntax_examples: scenario.command_preview?.syntax_examples ?? scenario.primary_focus_commands,
      what_changes: scenario.command_preview?.what_changes ?? [],
      what_does_not_change: scenario.command_preview?.what_does_not_change ?? [],
      common_mistakes: scenario.command_preview?.common_mistakes ?? [],
      readiness_notes: scenario.command_preview?.readiness_notes ?? [],
      demo_steps: [],
    },
  ]
}

function normalizeDemoSteps(
  value: unknown,
  fallbackSnapshot: RepositorySnapshot,
  fallbackExplanation?: string,
  fallbackCommonMistake = 'Skipping inspection before choosing an action.',
): DemoExplanationStep[] {
  if (!Array.isArray(value)) return []
  return value
    .map((item, index): DemoExplanationStep | null => {
      if (typeof item === 'string') {
        return {
          command: `Demo step ${index + 1}`,
          title: `Demo step ${index + 1}`,
          explanation: item || fallbackExplanation || '',
          repository_state: fallbackSnapshot,
          common_mistake: fallbackCommonMistake,
          diagnostic: false,
          counted: true,
        }
      }
      if (!item || typeof item !== 'object') return null
      const candidate = item as Partial<DemoExplanationStep>
      const command = typeof candidate.command === 'string' && candidate.command.trim()
        ? candidate.command
        : `Demo step ${index + 1}`
      return {
        command,
        title: typeof candidate.title === 'string' && candidate.title.trim() ? candidate.title : command,
        explanation:
          typeof candidate.explanation === 'string' && candidate.explanation.trim()
            ? candidate.explanation
            : fallbackExplanation || `Demo step ${index + 1}`,
        repository_state: isRepositorySnapshot(candidate.repository_state) ? candidate.repository_state : fallbackSnapshot,
        common_mistake:
          typeof candidate.common_mistake === 'string' && candidate.common_mistake.trim()
            ? candidate.common_mistake
            : fallbackCommonMistake,
        diagnostic: candidate.diagnostic ?? false,
        counted: candidate.counted ?? true,
      }
    })
    .filter((step): step is DemoExplanationStep => Boolean(step))
}

function normalize(command: string) {
  return command.trim().replace(/\s+/g, ' ').toLowerCase()
}

function isRepositorySnapshot(value: unknown): value is RepositorySnapshot {
  if (!value || typeof value !== 'object') return false
  const snapshot = value as Partial<RepositorySnapshot>
  return Array.isArray(snapshot.commits) && Boolean((snapshot as RepositorySnapshot).head)
}
