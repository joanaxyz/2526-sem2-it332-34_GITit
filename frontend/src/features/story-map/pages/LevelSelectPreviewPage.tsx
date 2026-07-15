import { useState } from 'react'

import type {
  ChallengeSummary,
  ChallengeTrialAccess,
  AdventureSummary,
} from '@/features/challenges/types'
import { AdventureLevelsModal } from '@/features/story-map/components/AdventureLevelsModal'
import { ChallengeTrialsModal } from '@/features/story-map/components/ChallengeTrialsModal'

/**
 * DEV-only visual checkpoint for the redesigned level-select modals. Mock data
 * only; no API/auth. Compiled away in production.
 */

const LEVEL_TITLES = [
  'Initialise the repository',
  'Stage your first change',
  'Commit with a message',
  'Inspect the log',
  'Amend the last commit',
  'Branch off main',
  'Switch between branches',
  'Merge a feature branch',
  'Resolve a conflict',
  'Tag a release',
  'Push to the remote',
]

function buildAdventures(): AdventureSummary[] {
  return LEVEL_TITLES.map((title, i) => {
    const completed = i < 5
    const locked = i > 7
    return {
      item_type: 'adventure',
      id: i + 1,
      slug: `level-${i + 1}`,
      title,
      description: 'Learn the core commit workflow.',
      command: 'git',
      learned: completed,
      completed,
      locked,
      lock_reason: 'Clear the previous level to unlock.',
      wave_count: (i % 3) + 1,
      completion: completed
        ? { stars: Math.max(1, 3 - (i % 3)), counted_action_total: i + 1, completed_at: '' }
        : null,
      latest_run_id: completed ? 8000 + i : null,
      status: completed ? 'completed' : locked ? 'not_started' : 'started',
      is_passed: completed,
      progress: { value: completed ? 100 : 0, numerator: completed ? 1 : 0, denominator: 1 },
    }
  })
}

function lvl(
  id: number,
  difficulty: ChallengeTrialAccess['difficulty'],
  status: ChallengeTrialAccess['status'],
  opts: Partial<ChallengeTrialAccess> = {},
): ChallengeTrialAccess {
  const cleared = status === 'completed'
  return {
    id,
    difficulty,
    status,
    cleared,
    replay_available: cleared,
    latest_attempt: null,
    completion:
      status === 'completed'
        ? { stars: opts.completion?.stars ?? 1, counted_action_total: 4, completed_at: '' }
        : null,
    command_budget: { min_counted_commands: 1, max_counted_commands: 6 },
    ...opts,
  }
}

const CHALLENGES: ChallengeSummary[] = [
  {
    item_type: 'challenge',
    id: 1,
    slug: 'untangle-the-history',
    title: 'Untangle the History',
    narrative: '',
    summary: 'Rebuild a tangled commit graph back to a clean linear history.',
    status: 'in_progress',
    completed: false,
    locked: false,
    trials: [
      lvl(11, 'easy', 'completed', { completion: { stars: 3, counted_action_total: 3, completed_at: '' } }),
      lvl(12, 'medium', 'in_progress'),
      lvl(13, 'hard', 'not_started'),
    ],
  },
  {
    item_type: 'challenge',
    id: 2,
    slug: 'rescue-the-detached-head',
    title: 'Rescue the Detached HEAD',
    narrative: '',
    summary: 'Recover work stranded on a detached HEAD before it is lost.',
    status: 'failed',
    completed: false,
    locked: false,
    trials: [
      lvl(21, 'easy', 'completed'),
      lvl(22, 'medium', 'failed'),
      lvl(23, 'hard', 'locked'),
    ],
  },
]


export function Component() {
  const [view, setView] = useState<'adventure' | 'challenge'>('adventure')
  const [open, setOpen] = useState(true)
  const adventures = buildAdventures()

  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', background: 'hsl(var(--background))', gap: '1rem' }}>
      <div style={{ display: 'flex', gap: '0.75rem' }}>
        <button
          type="button"
          onClick={() => {
            setView('adventure')
            setOpen(true)
          }}
          style={ctrl(view === 'adventure')}
        >
          Adventure
        </button>
        <button
          type="button"
          onClick={() => {
            setView('challenge')
            setOpen(true)
          }}
          style={ctrl(view === 'challenge')}
        >
          Challenge
        </button>
      </div>

      {open && view === 'adventure' ? (
        <AdventureLevelsModal adventures={adventures} onClose={() => setOpen(false)} />
      ) : null}
      {open && view === 'challenge' ? (
        <ChallengeTrialsModal challenges={CHALLENGES} locked={false} onClose={() => setOpen(false)} />
      ) : null}
    </div>
  )
}

function ctrl(active: boolean): React.CSSProperties {
  return {
    padding: '0.5rem 1rem',
    borderRadius: '0.6rem',
    border: '1px solid rgba(var(--theme-primary-rgb),0.3)',
    background: active ? 'rgba(var(--theme-primary-rgb),0.16)' : 'transparent',
    color: 'hsl(var(--foreground))',
    fontWeight: 700,
    cursor: 'pointer',
  }
}
