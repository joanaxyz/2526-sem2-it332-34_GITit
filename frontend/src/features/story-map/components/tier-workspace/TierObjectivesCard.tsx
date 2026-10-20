import { BookOpenText, Check, ClipboardList, Sparkle, X } from 'lucide-react'

import type { TierObjective, TierObjectiveStatus } from '@/features/story-map/components/tierWorkspaceTypes'
import { Button } from '@/shared/components/Button'
import { Card, CardContent, CardHeader } from '@/shared/components/Card'
import { CopyButton } from '@/shared/components/CopyButton'
import { ScenarioInline } from '@/shared/level/components/ScenarioInline'
import { cn } from '@/shared/utils/cn'

const STATUS_LABEL: Record<TierObjectiveStatus, string> = {
  pending: 'Not done yet',
  done: 'Done',
  failed: 'Failed',
}

/**
 * Objectives for the current tier run: a scrolling checklist (plus any exact
 * values the scenario requires), with Story available in the pane header.
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
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="tier-story-button"
          disabled={!onOpenStory}
          onClick={onOpenStory}
          data-tour-target="tier-story"
          aria-haspopup="dialog"
          title="Read the mission briefing"
        >
          <BookOpenText className="tier-story-button__book" aria-hidden="true" />
          Story
          <span className="tier-story-button__sparkles" aria-hidden="true">
            <Sparkle className="tier-story-button__sparkle tier-story-button__sparkle--one" />
            <Sparkle className="tier-story-button__sparkle tier-story-button__sparkle--two" />
            <Sparkle className="tier-story-button__sparkle tier-story-button__sparkle--three" />
          </span>
        </Button>
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
      <span className="tier-objective__text"><ScenarioInline text={objective.text} /></span>
      <span className="sr-only">{STATUS_LABEL[status]}</span>
    </li>
  )
}
