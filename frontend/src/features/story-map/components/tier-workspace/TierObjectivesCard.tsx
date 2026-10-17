import { BookOpenText, Check, ClipboardList, X } from 'lucide-react'

import type { TierObjective, TierObjectiveStatus } from '@/features/story-map/components/tierWorkspaceTypes'
import { Button } from '@/shared/components/Button'
import { Card, CardContent, CardHeader } from '@/shared/components/Card'
import { CopyButton } from '@/shared/components/CopyButton'
import { cn } from '@/shared/utils/cn'

const STATUS_LABEL: Record<TierObjectiveStatus, string> = {
  pending: 'Not done yet',
  done: 'Done',
  failed: 'Failed',
}

/**
 * Objectives for the current tier run: a scrolling checklist (plus any exact
 * values the scenario requires) above a Story button that stays pinned.
 */
export function TierObjectivesCard({
  objectives,
  requiredValues,
  onOpenStory,
}: {
  objectives: TierObjective[]
  requiredValues: { label: string; value: string }[]
  /** Opens the level story. Without it the button is shown but disabled. */
  onOpenStory?: () => void
}) {
  return (
    <Card className="lvlctx tier-objectives shadow-none" data-tour-target="tier-brief">
      <CardHeader className="lvlctx-header workspace-panel-header">
        <span className="panel-eyebrow">Objectives</span>
      </CardHeader>
      <CardContent className="tier-objectives__body">
        <div className="tier-objectives__scroll app-scrollbar">
          {objectives.length ? (
            <ul className="tier-objective-list" aria-label="Objectives">
              {objectives.map((objective) => (
                <ObjectiveRow key={objective.id} objective={objective} />
              ))}
            </ul>
          ) : (
            <p className="tier-objectives__empty">No objective is listed for this level.</p>
          )}

          {requiredValues.length ? (
            <section className="tier-required-values">
              <div className="lvlctx-eyebrow">
                <ClipboardList aria-hidden="true" />
                Required values
              </div>
              <ul className="lvlctx-copies" aria-label="Values the objective requires">
                {requiredValues.map((item) => (
                  <li className="lvlctx-copy" key={`${item.label}:${item.value}`}>
                    {item.label ? <span className="lvlctx-copy-label">{item.label}</span> : null}
                    <code>{item.value}</code>
                    <CopyButton value={item.value} label={item.label || item.value} className="lvlctx-copy-btn" />
                  </li>
                ))}
              </ul>
            </section>
          ) : null}
        </div>

        <Button
          type="button"
          variant="outline"
          className="tier-story-button"
          disabled={!onOpenStory}
          onClick={onOpenStory}
          data-tour-target="tier-story"
        >
          <BookOpenText aria-hidden="true" />
          Story
        </Button>
      </CardContent>
    </Card>
  )
}

function ObjectiveRow({ objective }: { objective: TierObjective }) {
  const { status } = objective
  return (
    <li className={cn('tier-objective', `is-${status}`)}>
      <span className="tier-objective__box" aria-hidden="true">
        {status === 'done' ? <Check /> : status === 'failed' ? <X /> : null}
      </span>
      <span className="tier-objective__text">{objective.text}</span>
      <span className="sr-only">{STATUS_LABEL[status]}</span>
    </li>
  )
}
