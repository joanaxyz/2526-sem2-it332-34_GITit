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
        title="Scenario preview"
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
        title="Scenario preview"
        onClose={onClose}
        className="w-full max-w-xl"
        contentClassName="p-5"
      >
        <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm leading-6 text-destructive">
          {detailQuery.error?.message ?? 'Could not load the scenario preview.'}
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
    () => normalizeDemoSteps(scenario.demo_explanation_steps, initialSnapshot, scenario.short_explanation),
    [initialSnapshot, scenario.demo_explanation_steps, scenario.short_explanation],
  )
  const [snapshot, setSnapshot] = useState<RepositorySnapshot>(initialSnapshot)
  const [explanation, setExplanation] = useState(commandBehaviorSummary(scenario))
  const [stepIndex, setStepIndex] = useState(-1)
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
    setExplanation('This preview accepts only a small warm-up set. It teaches command behavior without evaluating the scenario answer.')
  }

  return (
    <Modal
      open
      title="Scenario preview"
      onClose={onClose}
      className="max-h-[92vh] w-full max-w-6xl overflow-hidden"
      contentClassName="max-h-[calc(92vh-4.5rem)] overflow-auto p-5"
    >
      <div className="space-y-5">
        <header className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">Scenario</p>
            <h3 className="mt-1 text-2xl font-extrabold tracking-tight">{scenario.title}</h3>
          </div>
          <div className="flex flex-wrap justify-end gap-2">
            <Badge variant="blue">{difficultyLabel}</Badge>
          </div>
        </header>

        <section className="grid gap-3 rounded-lg border border-border bg-secondary/20 p-4">
          <p className="text-sm leading-6 text-muted-foreground">{scenario.short_explanation ?? ''}</p>

          {scenario.primary_focus_commands.length || (scenario.supporting_inspection_commands ?? []).length ? (
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

          <CommandConceptGuide scenario={scenario} />
          <CommandQuickReference commands={scenario.primary_focus_commands ?? []} />
        </section>

        <section className="grid grid-cols-[minmax(0,1.05fr)_minmax(18rem,0.75fr)] gap-4 max-lg:grid-cols-1">
          <DemoLiveDagPanel snapshot={snapshot} />
          <DemoExplanationPanel explanation={explanation} snapshot={snapshot} />
        </section>

        <div className="grid gap-3">
          <TerminalPanel
            title="Demo terminal"
            className="h-56"
            disabled={isRunningDemo}
            lines={terminalLines}
            onCommand={runDemoCommand}
          />
        </div>

        <PreviewNavigationControls
          canGoPrevious={stepIndex > 0}
          canGoNext={steps.length > 0 && stepIndex < steps.length - 1}
          isProceeding={isProceeding}
          startLabel={startLabel}
          onPrevious={() => applyStep(stepIndex - 1)}
          onNext={() => applyStep(stepIndex + 1)}
          onStartPractice={onProceed}
        />
      </div>
    </Modal>
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

function CommandConceptGuide({ scenario }: { scenario: ScenarioSkillFocus }) {
  const normalized = normalize(scenario.focus)
  const guide = commandGuideFor(normalized)
  if (!guide) return null

  return (
    <div className="grid gap-3 rounded-md border border-border bg-background/40 p-3 md:grid-cols-3">
      <div>
        <div className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">What it changes</div>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">{guide.changes}</p>
      </div>
      <div>
        <div className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">What it does not do</div>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">{guide.doesNotDo}</p>
      </div>
      <div>
        <div className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">Common mistake</div>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">{guide.mistake}</p>
      </div>
    </div>
  )
}

function commandGuideFor(normalizedCommand: string) {
  const guides: Record<string, { changes: string; doesNotDo: string; mistake: string }> = {
    'git init': {
      changes: 'Creates Git metadata in the current folder or in the named folder when you use git init <directory>.',
      doesNotDo: 'It does not create a first commit, stage files, or make existing files tracked.',
      mistake: 'Initializing the parent folder when the requested repository is a specific child directory.',
    },
    'git clone': {
      changes: 'Creates a local repository from a remote and records origin plus remote-tracking branches.',
      doesNotDo: 'It does not push anything back to the remote or change the remote repository.',
      mistake: 'Forgetting the required destination folder when the scenario asks for a custom folder name.',
    },
    'git add': {
      changes: 'Copies selected working-tree changes into the staging area for the next commit.',
      doesNotDo: 'It does not create a commit by itself and does not automatically mean every file should be staged.',
      mistake: 'Using git add . when the scenario asks for only selected files.',
    },
    'git commit': {
      changes: 'Creates a new snapshot from staged content and moves the current branch tip forward.',
      doesNotDo: 'It does not include unstaged changes and should not include unrelated work accidentally.',
      mistake: 'Committing before checking what is staged.',
    },
    '.gitignore': {
      changes: 'Adds ignore rules that Git uses when deciding which untracked local paths to ignore.',
      doesNotDo: 'It does not automatically remove files that are already tracked in history.',
      mistake: 'Committing generated files or secrets instead of committing only the ignore rules and untracking already tracked generated paths.',
    },
    'git add -p': {
      changes: 'Stages selected hunks while leaving other hunks in the working tree.',
      doesNotDo: 'It does not require staging the whole file.',
      mistake: 'Accepting every hunk when only one logical change belongs in the commit.',
    },
    'git commit --amend': {
      changes: 'Replaces the latest local commit with a corrected commit.',
      doesNotDo: 'It should not create a second follow-up commit for a simple latest-commit repair.',
      mistake: 'Using a normal commit when the task specifically asks to repair the latest commit.',
    },
    'git restore': {
      changes: 'With --staged, moves paths out of staging; without --staged, restores working-tree paths.',
      doesNotDo: 'It does not create a commit and can discard work when used on the working tree.',
      mistake: 'Confusing unstage with discard and accidentally removing work you meant to keep.',
    },
  }
  return guides[normalizedCommand] ?? null
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
  if (normalized === 'git init') {
    return {
      key: 'git-init',
      title: 'git init',
      syntax: ['git init', 'git init <directory>'],
      note: 'Creates repository metadata in the current folder, or in the named directory when a directory is provided.',
    }
  }
  if (normalized === 'git clone') {
    return {
      key: 'git-clone',
      title: 'git clone',
      syntax: ['git clone <url>', 'git clone <url> <folder>'],
      note: 'Creates a local working copy from a remote repository and configures origin.',
    }
  }
  if (normalized === 'git remote') {
    return {
      key: 'git-remote',
      title: 'git remote',
      syntax: ['git remote', 'git remote -v', 'git remote add origin <url>'],
      note: 'Shows or configures named remote repository locations such as origin.',
    }
  }
  if (normalized === 'git fetch') {
    return {
      key: 'git-fetch',
      title: 'git fetch',
      syntax: ['git fetch', 'git fetch origin'],
      note: 'Updates remote-tracking refs without moving the current local branch.',
    }
  }
  if (normalized === 'git pull') {
    return {
      key: 'git-pull',
      title: 'git pull',
      syntax: ['git pull'],
      note: 'Updates the current branch from its configured upstream.',
    }
  }
  if (normalized === 'git push') {
    return {
      key: 'git-push',
      title: 'git push',
      syntax: ['git push'],
      note: 'Publishes the current branch to its configured upstream remote branch.',
    }
  }
  if (normalized === 'git restore' || normalized === 'git restore --staged') {
    return {
      key: normalized.replace(/\s+/g, '-'),
      title: normalized,
      syntax: normalized === 'git restore --staged' ? ['git restore --staged <path>'] : ['git restore <path>'],
      note: normalized === 'git restore --staged'
        ? 'Moves selected paths out of staging while keeping the working tree copy.'
        : 'Discards selected working-tree changes from the current checkout.',
    }
  }
  if (normalized === 'git stash') {
    return {
      key: 'git-stash',
      title: 'git stash',
      syntax: ['git stash', 'git stash pop'],
      note: 'Temporarily saves local changes so branch navigation or integration can continue.',
    }
  }
  if (normalized === 'git reflog') {
    return {
      key: 'git-reflog',
      title: 'git reflog',
      syntax: ['git reflog'],
      note: 'Shows recent HEAD movements that can help recover from pointer mistakes.',
    }
  }
  if (normalized === 'git commit --amend') {
    return {
      key: 'git-commit-amend',
      title: 'git commit --amend',
      syntax: ['git commit --amend', 'git commit --amend -m "message"'],
      note: 'Replaces the latest commit with staged changes and optionally a revised message.',
    }
  }
  return null
}
