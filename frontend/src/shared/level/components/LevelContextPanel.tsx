import { BookOpenText, Check, ClipboardList, Star } from 'lucide-react'
import type { ComponentType, ReactNode } from 'react'

import { TaskSealIcon } from '@/shared/level/components/workspaceIcons'

import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'
import type { NormalizedLevelContext, ObjectiveCheck } from '@/shared/level/utils/levelContext'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'
import { CopyButton } from '@/shared/components/CopyButton'
import { cn } from '@/shared/utils/cn'

export type LevelFact = {
  label: string
  icon: ComponentType<{ className?: string }>
  /** Optional icon tint override (the mock renders the star/reward glyphs amber). */
  iconClass?: string
  value: ReactNode
}

export function StarTriplet({ count, className }: { count: number; className?: string }) {
  return (
    <span className={cn('gameplay-header-stars', className)} aria-label={`${count} of 3 stars`}>
      {Array.from({ length: 3 }).map((_, index) => (
        <Star key={index} aria-hidden="true" className={index < count ? 'is-lit' : ''} />
      ))}
    </span>
  )
}

export function DifficultyChip({ difficulty }: { difficulty: string }) {
  return (
    <span className={cn('lvlctx-chip', `lvlctx-chip--${difficulty.toLowerCase()}`)}>
      {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
    </span>
  )
}

export function RewardValue({ coins }: { coins: number }) {
  return (
    <span className="lvlctx-reward">
      <GitCoinIcon />
      <span>{coins.toLocaleString()} GitCoins</span>
    </span>
  )
}

/**
 * The reference mock's LEVEL CONTEXT panel, shared by both workspaces: panel
 * eyebrow over a hairline, icon-led title, STORY / TASK sections, then the
 * icon fact rows. No nested boxes.
 *
 * The live objective checklist is an adventure-only scaffold: the adventure
 * caller passes the evaluated rows via `checks`; challenges rely on the
 * expected-state reveal instead.
 */
export function LevelStoryCard({
  title,
  titleIcon: TitleIcon,
  context,
  facts,
  className,
  checks,
}: {
  title: string
  titleIcon: ComponentType<{ className?: string }>
  context: NormalizedLevelContext
  facts?: LevelFact[]
  className?: string
  checks?: ObjectiveCheck[]
}) {
  return (
    <Card className={cn('lvlctx shadow-none', className)}>
      <CardHeader className="lvlctx-header">
        <span className="panel-eyebrow">Level Context</span>
        <div className="lvlctx-titlerow">
          <TitleIcon aria-hidden="true" />
          <CardTitle className="lvlctx-title">{title}</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="lvlctx-body app-scrollbar">
        <Section icon={BookOpenText} title="Story" hidden={!context.story}>
          <p className="lvlctx-story">{context.story}</p>
        </Section>

        <Section icon={TaskSealIcon} title="Task" hidden={!context.task}>
          <p className="lvlctx-task">{context.task}</p>
        </Section>

        <Section icon={TaskSealIcon} title="Objective" hidden={!checks?.length}>
          <ul className="lvlctx-checks">
            {(checks ?? []).map((check) => (
              <li className={cn('lvlctx-check', check.satisfied && 'is-done')} key={check.label}>
                <span className="lvlctx-check-dot" aria-hidden="true">
                  {check.satisfied ? <Check /> : null}
                </span>
                <span className="lvlctx-check-label">{check.label}</span>
              </li>
            ))}
          </ul>
        </Section>

        {/* Required names (folder, branch, ...) sit right under the objective:
            the story references them and the panel bottom is the first thing
            to scroll out of view on short viewports. */}
        <Section icon={ClipboardList} title="Copy details" hidden={!context.details.length}>
          <ul className="lvlctx-copies" aria-label="Values referenced by the story and task">
            {context.details.map((item) => (
              <li className="lvlctx-copy" key={`${item.label}:${item.value}`}>
                {item.label ? <span className="sr-only">{item.label}: </span> : null}
                <code>{item.value}</code>
                <CopyButton
                  value={item.value}
                  label={`Copy ${item.label || item.value}`}
                  className="lvlctx-copy-btn"
                />
              </li>
            ))}
          </ul>
        </Section>

        {facts?.length ? (
          <section className="lvlctx-section">
            <dl className="lvlctx-facts">
              {facts.map((fact) => (
                <div className="lvlctx-fact" key={fact.label}>
                  <dt>
                    <fact.icon aria-hidden="true" className={fact.iconClass} />
                    {fact.label}
                  </dt>
                  <dd>{fact.value}</dd>
                </div>
              ))}
            </dl>
          </section>
        ) : null}
      </CardContent>
    </Card>
  )
}

function Section({
  children,
  hidden,
  icon: Icon,
  title,
}: {
  children: ReactNode
  hidden?: boolean
  icon: ComponentType<{ className?: string }>
  title: string
}) {
  if (hidden) return null
  return (
    <section className="lvlctx-section">
      <div className="lvlctx-eyebrow">
        <Icon aria-hidden="true" />
        {title}
      </div>
      {children}
    </section>
  )
}
