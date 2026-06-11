import { Check, Loader2, Lock, Play, Swords } from 'lucide-react'
import type { ComponentType } from 'react'

import type { ChallengeQuestAccess, ChallengeStatus, Difficulty } from '@/features/challenges/types'
import { cn } from '@/shared/utils/cn'

const DIFFICULTY_LABELS: Record<string, string> = {
  easy: 'Easy',
  medium: 'Medium',
  hard: 'Hard',
}

function difficultyLabel(difficulty: Difficulty) {
  return DIFFICULTY_LABELS[difficulty] ?? difficulty.charAt(0).toUpperCase() + difficulty.slice(1)
}

type NodeTone = 'completed' | 'current' | 'available' | 'locked'

function nodeTone(quest: ChallengeQuestAccess, currentQuestId: number): NodeTone {
  if (quest.id === currentQuestId) return 'current'
  if (quest.status === 'completed') return 'completed'
  if (quest.status === 'locked') return 'locked'
  return 'available'
}

const TONE_ICON: Record<NodeTone, ComponentType<{ className?: string }>> = {
  completed: Check,
  current: Swords,
  available: Play,
  locked: Lock,
}

/**
 * Quest navigator for the challenge completion modal. Renders every quest of the
 * challenge as a connected stepper so a learner on a higher quest can drop back to
 * any unlocked (or completed) quest — and, once the whole challenge is cleared,
 * jump freely between all of them. Locked quests stay visible but disabled.
 */
export function ChallengeQuestNav({
  quests,
  currentQuestId,
  onSelectQuest,
  busyQuestId,
  disabled = false,
}: {
  quests: ChallengeQuestAccess[]
  currentQuestId: number
  onSelectQuest: (questId: number) => void
  busyQuestId?: number | null
  disabled?: boolean
}) {
  if (quests.length < 2) return null

  return (
    <div className="mt-5 rounded-xl border border-border/50 bg-card/50 p-3">
      <div className="mb-3 flex items-center justify-center gap-1.5 font-mono text-[0.6rem] uppercase tracking-[0.16em] text-muted-foreground">
        <Swords className="size-3" />
        Jump to a quest
      </div>
      <div className="flex items-stretch justify-center gap-1.5">
        {quests.map((quest, index) => {
          const tone = nodeTone(quest, currentQuestId)
          const Icon = quest.id === busyQuestId ? Loader2 : TONE_ICON[tone]
          const isLocked = tone === 'locked'
          const isBusy = quest.id === busyQuestId
          const isInteractive = !isLocked && !disabled && !isBusy

          return (
            <button
              key={quest.id}
              type="button"
              disabled={!isInteractive}
              aria-current={tone === 'current' ? 'step' : undefined}
              onClick={() => onSelectQuest(quest.id)}
              className={cn(
                'group relative flex flex-1 flex-col items-center gap-1.5 rounded-lg border px-2 py-2.5 transition-all duration-200',
                tone === 'current' &&
                  'border-primary/60 bg-primary/10 shadow-[0_0_18px_rgba(0,245,212,0.22)]',
                tone === 'completed' &&
                  'border-emerald-400/40 bg-emerald-400/5 hover:-translate-y-0.5 hover:border-emerald-400/70',
                tone === 'available' &&
                  'border-border/60 bg-card/60 hover:-translate-y-0.5 hover:border-primary/60 hover:bg-primary/5',
                isLocked && 'cursor-not-allowed border-border/40 bg-card/30 opacity-50',
                !isInteractive && !isLocked && 'cursor-wait',
              )}
            >
              {/* Connector to the previous node, tinted once both sides are cleared. */}
              {index > 0 ? (
                <span
                  aria-hidden
                  className={cn(
                    'absolute right-full top-1/2 h-px w-1.5 -translate-y-1/2',
                    tone === 'locked' ? 'bg-border/40' : 'bg-primary/40',
                  )}
                />
              ) : null}

              <span
                className={cn(
                  'grid size-7 place-items-center rounded-full border',
                  tone === 'current' && 'border-primary/60 bg-primary/15 text-primary',
                  tone === 'completed' && 'border-emerald-400/50 bg-emerald-400/15 text-emerald-300',
                  tone === 'available' &&
                    'border-border/70 bg-background/60 text-muted-foreground group-hover:text-primary',
                  isLocked && 'border-border/50 bg-background/40 text-muted-foreground',
                )}
              >
                <Icon className={cn('size-3.5', isBusy && 'animate-spin')} />
              </span>
              <span
                className={cn(
                  'text-xs font-bold',
                  tone === 'current' ? 'text-primary' : 'text-foreground',
                )}
              >
                {difficultyLabel(quest.difficulty)}
              </span>
              <span className="text-[0.6rem] font-medium uppercase tracking-wide text-muted-foreground">
                {statusLabel(quest.status, tone)}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

function statusLabel(status: ChallengeStatus, tone: NodeTone): string {
  if (tone === 'current') return 'Current'
  if (status === 'completed') return 'Cleared'
  if (status === 'locked') return 'Locked'
  if (status === 'in_progress') return 'In progress'
  if (status === 'failed' || status === 'abandoned') return 'Retry'
  return 'Open'
}
