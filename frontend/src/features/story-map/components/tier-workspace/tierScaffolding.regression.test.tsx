import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { tierScene } from '@/features/story-map/components/tierWorkspaceLayout'
import type { DagAnimationController } from '@/shared/level/workspace/useDagAnimation'
import { useRepoGraphDrawer } from '@/shared/level/workspace/useRepoGraphDrawer'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import type { RepositorySnapshot } from '@/shared/level/types'

// Heavy leaves are stubbed; every panel decision under test stays real.
vi.mock('@/shared/level/workspace/WorkspaceBattlePanel', () => ({
  WorkspaceBattlePanel: () => <div data-testid="battle-stage" />,
}))
vi.mock('@/shared/level/components/WorkspaceEditorOverlay', () => ({ WorkspaceEditorOverlay: () => null }))
vi.mock('@/shared/level/components/ProjectStructurePanel', () => ({
  ProjectStructurePanel: () => <div data-testid="project-files" />,
}))
vi.mock('@/shared/level/workspace/WorkspaceDagStage', () => ({
  WorkspaceDagStage: ({ showHeader = true }: { showHeader?: boolean }) => (
    <div data-testid="live-dag">{showHeader ? 'Live DAG' : null}</div>
  ),
}))
vi.mock('@/shared/level/components/LiveDagPanel', () => ({
  LiveDagPanel: ({ title }: { title: string }) => <div data-testid="expected-dag">{title}</div>,
}))

import { TierStatsBar } from './TierStatsBar'
import { GameplayWorkspaceMain } from '@/shared/level/workspace/GameplayWorkspaceMain'
import { REPO_GRAPH_ID } from '@/shared/level/workspace/WorkspaceDiagramStage'

/**
 * Fading scaffolding for adventure level tiers, as the backend tier ladder
 * (practice/services/scaffolding.py TIER_SCAFFOLDING_LADDER) and the seeded
 * command limits send it. Every assertion below is derived from these flags,
 * never from the difficulty name.
 */
const TIER_ROWS = [
  { difficulty: 'easy', scaffolding: { live_dag: true, expected_state: true, contextual_feedback: true }, maxCommands: 12 },
  { difficulty: 'medium', scaffolding: { live_dag: true, expected_state: true, contextual_feedback: false }, maxCommands: 10 },
  { difficulty: 'hard', scaffolding: { live_dag: true, expected_state: false, contextual_feedback: false }, maxCommands: 8 },
] as const

type Row = (typeof TIER_ROWS)[number]

/** The three layouts. jsdom has no layout engine: below 700px is the same DOM
 *  as the wide layout (CSS reorders it), so both run the non-drawer path. */
const LAYOUTS = [
  { name: '>= 1100px', drawer: false },
  { name: '700-1099px drawer', drawer: true },
  { name: '< 700px', drawer: false },
] as const

const animation = {
  activity: 'idle',
  animating: false,
  onCommandStart: vi.fn(),
  onCommandResolved: vi.fn(),
  onCommandError: vi.fn(),
} satisfies DagAnimationController

const director = { animating: false } as unknown as BattleDirector

function snapshot(commits: string[]): RepositorySnapshot {
  return {
    repository_initialized: true,
    commits: commits.map((id, index) => ({ id, message: id, parents: index ? [commits[index - 1]] : [], tree: {} })),
    branches: { main: commits.at(-1) ?? null },
    head: { type: 'branch', name: 'main', target: commits.at(-1) ?? null },
    staging: {},
    working_tree: {},
    conflicts: [],
  } as unknown as RepositorySnapshot
}

function makeRun(row: Row, repositoryState = snapshot(['c1'])): TierRun {
  return {
    id: 1,
    status: 'started',
    replay: false,
    stars: 0,
    difficulty: row.difficulty,
    tier: {
      id: 1,
      difficulty: row.difficulty,
      adventure_level_id: 5,
      adventure_level_slug: 'initializing-a-local-repository',
      adventure_level_title: 'Initializing Repositories',
    },
    variant: { id: 1, label: 'Initialize the current folder', changed_variant: false },
    scenario_context: { schema_version: 3, story: 'Story', task: 'Initialize the repository.' },
    scaffolding: row.scaffolding,
    policy: { min_counted_commands: 1, max_counted_commands: row.maxCommands },
    counts: { counted_action_total: 0 },
    reward: { coins: 25, claimed: false },
    wave: { index: 1, total: 1, title: '' },
    repository_state: repositoryState,
    // The backend sends a target only when the flag allows it.
    expected_state: row.scaffolding.expected_state ? snapshot(['t1']) : null,
    steps: [],
  } as unknown as TierRun
}

/** Wires the real drawer hook into the stats bar and workspace like TierWorkspace does. */
function Harness({ run, teachingActive = false }: { run: TierRun; teachingActive?: boolean }) {
  const drawer = useRepoGraphDrawer(run.repository_state)
  return (
    <>
      <TierStatsBar
        run={run}
        repoGraph={drawer.drawerMode ? {
          open: drawer.open,
          hasUpdate: drawer.hasUpdate,
          controls: REPO_GRAPH_ID,
          buttonRef: drawer.buttonRef,
          onOpen: drawer.openDrawer,
        } : undefined}
      />
      <GameplayWorkspaceMain
        teachingActive={teachingActive}
        repoGraphDrawer={drawer.drawerMode ? { open: drawer.open, openCount: drawer.openCount, onClose: drawer.closeDrawer } : undefined}
        run={run}
        scene={tierScene(run)}
        lines={[]}
        shellPrompt="learner"
        projectFilesOpen
        workspaceEditorPath={null}
        createDisabled={false}
        writeDisabled={false}
        dagAnimation={animation}
        battleDirector={director}
        mutationPending={false}
        onToggleProjectFiles={vi.fn()}
        onCreateFile={vi.fn()}
        onRenameFile={vi.fn()}
        onDeleteFile={vi.fn()}
        onOpenFile={vi.fn()}
        onOpenStory={vi.fn()}
        onCommand={vi.fn()}
        onCloseEditor={vi.fn()}
        onWriteFile={vi.fn()}
      />
    </>
  )
}

let drawerMatches = false
beforeEach(() => {
  vi.stubGlobal('matchMedia', (query: string) => ({
    matches: drawerMatches,
    media: query,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
  }))
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  drawerMatches = false
})

describe.each(LAYOUTS)('tier fading scaffolding, $name', ({ drawer }) => {
  beforeEach(() => {
    drawerMatches = drawer
  })

  it.each(TIER_ROWS)('$difficulty: panels follow the run flags', (row) => {
    render(<Harness run={makeRun(row)} />)
    const { expected_state: hasExpected, contextual_feedback: hasFeedback } = row.scaffolding

    // Contextual feedback card: rendered only with the flag (Medium and Hard leave Project files the space).
    expect(Boolean(screen.queryByTestId('tier-feedback-region'))).toBe(hasFeedback)
    expect(screen.getByTestId('tier-workspace-sidebar').classList.contains('has-feedback')).toBe(hasFeedback)
    expect(screen.getByTestId('project-files')).toBeInTheDocument()

    // Live / Expected tabs, or a plain Live DAG under its own title.
    expect(Boolean(screen.queryByRole('tablist', { hidden: true }))).toBe(hasExpected)
    expect(Boolean(screen.queryByTestId('expected-dag'))).toBe(hasExpected)
    // With tabs the tab bar is the heading, so the Live DAG drops its own title.
    expect(screen.getByTestId('live-dag').textContent).toBe(hasExpected ? '' : 'Live DAG')

    // The command limit in the stats bar.
    expect(document.querySelector('[data-tour-target="command-budget"]')).toHaveTextContent(`0 / ${row.maxCommands}`)

    // Drawer layout: a Repo graph button and a dialog rail; otherwise neither.
    const rail = document.getElementById(REPO_GRAPH_ID)!
    expect(Boolean(screen.queryByRole('button', { name: /repo graph/i }))).toBe(drawer)
    expect(rail.getAttribute('role')).toBe(drawer ? 'dialog' : null)
  })

  it.each(TIER_ROWS)('$difficulty: the command guide reserves feedback space only where feedback exists', (row) => {
    render(<Harness run={makeRun(row)} teachingActive />)
    const region = screen.queryByTestId('tier-feedback-region')

    if (row.scaffolding.contextual_feedback) {
      expect(region).toHaveClass('is-suspended')
    } else {
      expect(region).toBeNull()
    }
  })
})

describe('tier repo graph drawer (700-1099px), per difficulty', () => {
  beforeEach(() => {
    drawerMatches = true
  })

  it.each(TIER_ROWS)('$difficulty: the change dot and the drawer work with or without an Expected State', (row) => {
    const { rerender } = render(<Harness run={makeRun(row, snapshot(['c1']))} />)
    expect(screen.getByRole('button', { name: 'Repo graph' })).toBeInTheDocument()

    rerender(<Harness run={makeRun(row, snapshot(['c1', 'c2']))} />)
    const button = screen.getByRole('button', { name: 'Repo graph, updated' })

    act(() => fireEvent.click(button))

    const dialog = screen.getByRole('dialog', { name: 'Repository graph' })
    expect(dialog).not.toHaveAttribute('inert')
    expect(screen.getByRole('button', { name: 'Repo graph' })).toHaveAttribute('aria-expanded', 'true')
    expect(Boolean(screen.queryByRole('tablist'))).toBe(row.scaffolding.expected_state)
  })
})
