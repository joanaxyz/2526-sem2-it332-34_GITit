import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { AdventureOutcomeModal } from '@/features/adventures/components/AdventureOutcomeModal'
import type { AdventureRun } from '@/features/adventures/types'
import { ChallengeOutcomeModal } from '@/features/challenges/components/ChallengeOutcomeModal'
import type { ChallengeRun } from '@/features/challenges/types'
import { Button } from '@/shared/components/Button'
import { cn } from '@/shared/utils/cn'

type PreviewMode = 'adventure-win' | 'adventure-loss' | 'challenge-win' | 'challenge-loss'

function previewMode(value: string | null): PreviewMode {
  if (value === 'adventure-loss' || value === 'challenge-win' || value === 'challenge-loss') return value
  return 'adventure-win'
}

const adventureRun = {
  id: 1,
  status: 'completed',
  replay: false,
  stars: 3,
  library_opened: false,
  is_passed: true,
  adventure: { id: 1, slug: 'repo-basecamp', title: 'Repository Basecamp', description: '' },
  selected_level: { id: 1, slug: 'create-repository', title: 'Create a repository', is_required: true },
  next_level: { id: 2, slug: 'first-commit', title: 'First commit', is_required: true },
  chapter_id: 1,
  current_level_index: 2,
  total_levels: 3,
  current_wave: 3,
  total_waves: 3,
  mastery: {
    commands: [
      {
        slug: 'git-init/current-directory',
        form_id: 1,
        form_slug: 'current-directory',
        skill_slug: 'git-init',
        title: 'Initialize the current folder',
        strength: 1,
        mastered_bar: 1,
        introduced: true,
        mastered: true,
      },
      {
        slug: 'git-init/named-folder',
        form_id: 2,
        form_slug: 'named-folder',
        skill_slug: 'git-init',
        title: 'Initialize a named folder',
        strength: 1,
        mastered_bar: 1,
        introduced: true,
        mastered: true,
      },
      {
        slug: 'git-branch/first-name',
        form_id: 3,
        form_slug: 'first-name',
        skill_slug: 'git-branch',
        title: 'Choose the first branch name',
        strength: 1,
        mastered_bar: 1,
        introduced: true,
        mastered: true,
      },
    ],
    commands_mastered: 3,
    total_commands: 3,
    total_achievable: 3,
    passed: true,
  },
  story: { id: 1, slug: 'arcane-spire', title: 'The Arcane Spire', world_slug: 'arcane-spire' },
  completed_at: '2026-06-30T00:00:00Z',
  current_attempt: null,
  results: [],
  progress: { completed: 2, total: 7 },
} as unknown as AdventureRun

const challengeRun = {
  id: 7,
  replay: false,
  status: 'completed',
  stars: 3,
  failure_reason: null,
  completed_at: '2026-06-30T00:00:00Z',
  challenge: {
    id: 10,
    slug: 'repo-basecamp',
    title: 'Repository Basecamp',
    summary: '',
    narrative: '',
    level_id: 101,
  },
  chapter: { id: 1, number: 1, title: 'Foundations' },
  battle_stage: null,
  difficulty: 'easy',
  variant: { id: 1, label: 'Variant A' },
  mastery_progress: { cleared: true, stars: 3 },
  policy: { min_counted_commands: 2, max_counted_commands: 5 },
  counts: {
    counted_action_total: 2,
    minimum_counted_commands: 2,
    maximum_counted_commands: 5,
    non_counted_diagnostic_total: 1,
    remaining_counted_commands: 3,
    max_reached: false,
    total_attempts: 1,
  },
  scaffolding: {
    live_dag: false,
    expected_state: false,
    contextual_feedback: false,
  },
  repository_state: {},
  visualization: { commit_dag: {} },
  expected_state: null,
  steps: [],
  next_difficulty: { id: 11, difficulty: 'medium' },
  sibling_levels: [
    { id: 101, difficulty: 'easy', status: 'completed' },
    { id: 102, difficulty: 'medium', status: 'in_progress' },
    { id: 103, difficulty: 'hard', status: 'locked' },
  ],
  completion: null,
} as unknown as ChallengeRun

/**
 * Dev-only outcome preview (/dev/outcomes). The router only imports this route
 * in DEV, so production builds do not expose it.
 */
export function OutcomePreviewPage() {
  const [searchParams] = useSearchParams()
  const [mode, setMode] = useState<PreviewMode>(() => previewMode(searchParams.get('mode')))
  const isAdventure = mode.startsWith('adventure')
  const isLoss = mode.endsWith('loss')

  const activeAdventureRun = {
    ...adventureRun,
    status: isLoss ? 'failed' : 'completed',
    stars: isLoss ? 0 : 3,
    mastery: {
      ...adventureRun.mastery,
      passed: !isLoss,
      commands: adventureRun.mastery.commands.map((command) => ({
        ...command,
        strength: isLoss ? 0 : command.strength,
        mastered: isLoss ? false : command.mastered,
      })),
      commands_mastered: isLoss ? 0 : adventureRun.mastery.commands_mastered,
    },
  } as AdventureRun

  const activeChallengeRun = {
    ...challengeRun,
    status: isLoss ? 'failed' : 'completed',
    stars: isLoss ? 0 : 3,
    counts: {
      ...challengeRun.counts,
      counted_action_total: isLoss ? 5 : 2,
      remaining_counted_commands: isLoss ? 0 : 3,
      max_reached: isLoss,
    },
    mastery_progress: { cleared: !isLoss, stars: isLoss ? 0 : 3 },
    next_difficulty: isLoss ? null : challengeRun.next_difficulty,
  } as ChallengeRun

  return (
    <div className="workspace-bg min-h-screen overflow-hidden p-4 text-foreground">
      <header className="flex items-center gap-2 border-b border-primary/15 pb-3">
        <span className="grid size-8 place-items-center rounded-md border border-primary/30 bg-primary/10 text-primary">
          {isAdventure ? 'A' : 'C'}
        </span>
        <div>
          <h1 className="text-sm font-semibold">Outcome preview</h1>
          <p className="text-xs text-muted-foreground">Dev fixture for the game result overlay.</p>
        </div>
        <div className="ml-auto flex flex-wrap gap-2">
          {(['adventure-win', 'adventure-loss', 'challenge-win', 'challenge-loss'] as const).map((item) => (
            <Button
              key={item}
              type="button"
              size="sm"
              variant={mode === item ? 'default' : 'outline'}
              onClick={() => setMode(item)}
            >
              {item.replace('-', ' ')}
            </Button>
          ))}
        </div>
      </header>

      <main className="grid min-h-[calc(100vh-5rem)] grid-cols-[22rem_minmax(0,1fr)] gap-3 pt-3 opacity-60 max-lg:grid-cols-1">
        <aside className="space-y-3">
          <section className="rounded-lg border border-border/50 bg-card/55 p-4">
            <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-primary">Story</p>
            <h2 className="mt-2 text-lg font-bold">Start a Repository</h2>
            <p className="mt-3 text-sm leading-6 text-muted-foreground">
              A teammate handed you starter files before the first review. Choose the first branch and keep history clean.
            </p>
          </section>
          <section className="rounded-lg border border-border/50 bg-card/55 p-4">
            <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-primary">Project Files</p>
            <div className="mt-4 space-y-2 font-mono text-xs text-muted-foreground">
              <p>src/app.py</p>
              <p>README.md</p>
            </div>
          </section>
        </aside>
        <section className="rounded-lg border border-border/50 bg-background/60 p-4">
          <div className="h-48 rounded-lg border border-primary/20 bg-[radial-gradient(circle_at_50%_20%,rgba(var(--theme-accent-rgb),0.18),transparent_24rem),hsl(var(--background)/0.72)]" />
          <div className="mt-3 h-2 overflow-hidden rounded-full bg-border/40">
            <div className={cn('h-full rounded-full bg-primary shadow-[0_0_16px_rgba(var(--theme-primary-rgb),0.45)]', isLoss ? 'w-1/4' : 'w-3/4')} />
          </div>
        </section>
      </main>

      {isAdventure ? (
        <AdventureOutcomeModal
          open
          run={activeAdventureRun}
          onRestart={() => setMode('adventure-win')}
          onNextLevel={() => setMode('challenge-win')}
          onBackToMap={() => setMode('adventure-win')}
          onClose={() => undefined}
        />
      ) : (
        <ChallengeOutcomeModal
          open
          run={activeChallengeRun}
          onClose={() => undefined}
          onBackToMap={() => setMode('challenge-win')}
          onRetry={() => setMode('challenge-win')}
          onNextLevel={() => setMode('challenge-win')}
          onSelectLevel={() => undefined}
          nextDifficultyLabel="Medium"
        />
      )}
    </div>
  )
}

export const Component = OutcomePreviewPage
