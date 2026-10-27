import { Check, CircleAlert } from 'lucide-react'
import { useEffect, useId, useState } from 'react'
import type { CSSProperties, ReactNode } from 'react'

import type { CommandIntroduction } from '@/features/story-map/api/commandIntroductionsApi'
import { RepositoryChangeDiagram } from '@/features/story-map/components/RepositoryChangeDiagram'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { useCommandIntroduction } from '@/features/story-map/hooks/useCommandIntroduction'
import { useMediaQuery } from '@/shared/utils/useMediaQuery'
import { commandFamilyIcon, repositoryChangeIcon } from '@/features/story-map/utils/commandIntroductionIcons'
import { GameplayWorkspaceTour, type WorkspaceTourStep } from '@/shared/level/components/GameplayWorkspaceTour'
import { COMMAND_GUIDE_LAYOUT_KEY } from '@/shared/level/workspaceKeys'
import { GuideTutor } from '@/shared/tutoring/GuideTutor'

type RepositoryChange = CommandIntroduction['needs'][number]
type Tab = 'command' | 'change'

// Room for the command card and the "What changes" card side by side, with
// the workspace still visible around them. Below this they share one card.
const WIDE_QUERY = '(min-width: 1180px) and (min-height: 640px)'
const DEFAULT_PANE_LAYOUT = {
  main: { width: 454, height: 410 },
  aside: { width: 426, height: 396 },
  gap: 52,
  top: 24,
}
// The scenario, project files, tips and the guide's own "Ask Git-It" launcher
// stay readable while a guide is open; everything else sits under its veil.
const CONTEXT_REGIONS = [
  '[data-tour-target="level-story"]',
  '[data-tour-target="project-files"]',
  '[data-tour-target="workspace-tips"]',
  '[data-mascot-launcher="guide-tutor"]',
]
const FEEDBACK_REGIONS = [...CONTEXT_REGIONS, '[data-tour-target="terminal"]']
// The guide's chat window, its launcher and the terminal belong with the guide: clicks there keep it open.
const CLOSE_ON_OUTSIDE_CLICK = {
  except: ['.tutor-window', '[data-mascot-launcher="guide-tutor"]', '[data-tour-target="terminal"]'],
}

/**
 * "Command guide": introduces the command form the repository needs next, in
 * the scenario that teaches it.
 *
 * It explains the command part by part and shows what it will change as a
 * diagram; new words and techniques are tips beside it. Wide screens
 * show the guide as one frame holding the explanation and the change as their
 * own cards, each resized on its own; narrower screens use tabs in one card.
 *
 * Before a command its only button is close (×): it stays beside the terminal
 * while the learner types and turns into feedback once the command runs. Close,
 * Escape, or a click outside collapses it into the mascot launcher, which
 * brings it back. After a command, "Got it" records the guide as done.
 * Its "Ask Git-It" chat starts as a launcher beside it, so it never covers the
 * card, and closes with it.
 */
export function CommandIntroductionPanel({ run, tutor, replay = false, onDismiss }: {
  run: TierRun
  tutor: CommandIntroduction
  replay?: boolean
  onDismiss: () => void
}) {
  const lesson = useCommandIntroduction(run, tutor)
  const wide = useMediaQuery(WIDE_QUERY)
  const [tab, setTab] = useState<Tab>('command')
  const introduction = tutor.phase === 'introduction'
  // Feedback waits for "Got it"; introductions and replays can be put away.
  const dismissible = replay || introduction
  const missed = tutor.verdict === 'incorrect'
  const form = tutor.command_form
  const focusTerminal = () => {
    requestAnimationFrame(() => document.querySelector<HTMLInputElement>('[data-command-input]')?.focus())
  }
  useEffect(() => {
    if (introduction && !replay) focusTerminal()
  }, [introduction, replay])

  const error = lesson.error ? <p className="command-intro__error" role="alert">{lesson.error}</p> : null
  const changeTitle = 'What changes'
  const hasChange = (introduction || missed) && tutor.needs.length > 0
  const change = hasChange ? (
    <>
      <RepositoryChangeDiagram changes={tutor.needs} repository={undefined} />
      <ChangeList label="What this command does" changes={tutor.needs} />
    </>
  ) : null

  let command: ReactNode
  if (introduction) {
    command = (
      <>
        <CommandSyntax usage={form.usage_form} />
        <Anatomy parts={tutor.anatomy} />
        {form.summary && !sameWords(form.summary, tutor.title) ? (
          <p className="command-intro__summary">{form.summary}</p>
        ) : null}
        <p className="command-intro__note">
          Type it in the terminal and press Enter. This guide shows the result. It counts toward your command limit.
        </p>
      </>
    )
  } else if (missed) {
    command = (
      <>
        <Verdict tone="miss">{tutor.explanation}</Verdict>
        <CommandSyntax usage={form.usage_form} />
        {error}
      </>
    )
  } else {
    command = (
      <>
        <Verdict tone="hit">{tutor.explanation}</Verdict>
        <CommandSyntax usage={form.usage_form} compact />
        <ChangeList label="What changed" changes={tutor.changes} />
        {error}
      </>
    )
  }

  const split = wide && change !== null
  const body = split || change === null ? command : (
    <GuideTabs
      tab={tab}
      onTab={setTab}
      tabs={[
        { id: 'command', label: 'Command', content: command },
        { id: 'change', label: changeTitle, content: change },
      ]}
    />
  )

  const step: WorkspaceTourStep = {
    id: tutor.context_id,
    // Introductions point at the terminal; feedback points at the repository it changed.
    selector: introduction ? '[data-command-input]' : '[data-tour-target="live-dag"]',
    icon: commandFamilyIcon(form.usage_form),
    title: tutor.title,
    placement: introduction ? 'top' : 'left',
    body,
  }

  return (
    <>
      <GameplayWorkspaceTour
        label="Command guide"
        steps={[step]}
        refreshKey={tutor.context_id}
        finishLabel={lesson.pending ? 'Saving…' : 'Got it'}
        finishDisabled={lesson.pending}
        cardClassName="command-intro"
        skipLabel="Close command guide"
        skipIconOnly
        showSkip={dismissible}
        closeOnOutsideClick={dismissible ? CLOSE_ON_OUTSIDE_CLICK : undefined}
        showActions={!replay && !introduction}
        focusCard={replay || !introduction}
        showProgress={false}
        showSpeaker={false}
        transformable
        transformPreferenceKey={COMMAND_GUIDE_LAYOUT_KEY}
        paneLayout={DEFAULT_PANE_LAYOUT}
        paneLabels={{ main: 'command card', aside: `${changeTitle.toLowerCase()} card` }}
        reveal={introduction ? CONTEXT_REGIONS : FEEDBACK_REGIONS}
        collapseTarget='[data-mascot-launcher="command-guide"]'
        aside={split ? (
          <section className="command-intro__aside" aria-label={changeTitle}>
            <h3 className="command-intro__aside-title">{changeTitle}</h3>
            {change}
          </section>
        ) : undefined}
        onClose={(reason) => {
          if (reason === 'finish') {
            void lesson.complete().then((completed) => { if (completed) focusTerminal() })
            return
          }
          onDismiss()
          // After a click elsewhere, focus stays where the learner clicked.
          if (reason === 'skip') focusTerminal()
        }}
      />
      <GuideTutor
        key={tutor.context_id}
        runId={run.id}
        teachingKey={tutor.teaching_key}
        usageForm={form.usage_form}
        guideToken={tutor.help_token}
      />
    </>
  )
}

function sameWords(left: string, right: string) {
  const words = (text: string) => text.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()
  return words(left) === words(right)
}

function GuideTabs({ tab, onTab, tabs }: {
  tab: Tab
  onTab: (tab: Tab) => void
  tabs: readonly { id: Tab; label: string; content: ReactNode }[]
}) {
  const baseId = useId()
  return (
    <div className="command-intro__tabs">
      <div className="command-intro__tablist" role="tablist" aria-label="Command guide sections">
        {tabs.map((item) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            id={`${baseId}-${item.id}-tab`}
            aria-selected={tab === item.id}
            aria-controls={`${baseId}-${item.id}-panel`}
            className="command-intro__tab"
            onClick={() => onTab(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>
      {tabs.map((item) => (
        <div
          key={item.id}
          role="tabpanel"
          id={`${baseId}-${item.id}-panel`}
          aria-labelledby={`${baseId}-${item.id}-tab`}
          hidden={tab !== item.id}
          className="command-intro__tabpanel"
        >
          {item.content}
        </div>
      ))}
    </div>
  )
}

/** The command read part by part: git, the command, then each option and slot. */
function Anatomy({ parts }: { parts: CommandIntroduction['anatomy'] }) {
  if (parts.length === 0) return null
  return (
    <dl className="command-intro__anatomy" aria-label="What each part means">
      {parts.map((part, index) => (
        <div key={`${part.token}-${index}`} className="command-intro__part">
          <dt><code>{part.token}</code></dt>
          <dd>{part.text}</dd>
        </div>
      ))}
    </dl>
  )
}

const SYNTAX_TOKEN = /\[[^\]]*\]|\S+/g
const PLACEHOLDER = /(<[^>]+>)/g

/** Authored syntax with its fill-in slots (`<branch>`) and optional parts marked. */
function CommandSyntax({ usage, compact = false }: { usage: string; compact?: boolean }) {
  const tokens = usage.match(SYNTAX_TOKEN) ?? []
  return (
    <p className={`command-intro__syntax${compact ? ' is-compact' : ''}`}>
      <span className="sr-only">Syntax: {usage}</span>
      <span className="command-intro__prompt" aria-hidden="true">$</span>
      {tokens.map((token, index) => {
        const optional = token.startsWith('[') && token.endsWith(']')
        return (
          <span
            key={`${token}-${index}`}
            className={`command-intro__token${optional ? ' is-optional' : token.startsWith('-') ? ' is-flag' : ''}`}
            aria-hidden="true"
          >
            {token.split(PLACEHOLDER).map((part, partIndex) =>
              part.startsWith('<') && part.endsWith('>')
                ? <span key={partIndex} className="command-intro__slot">{part.slice(1, -1)}</span>
                : part,
            )}
          </span>
        )
      })}
    </p>
  )
}

function ChangeList({ label, changes }: { label: string; changes: readonly RepositoryChange[] }) {
  if (changes.length === 0) return null
  return (
    <section className="command-intro__section" aria-label={label}>
      <h3 className="command-intro__label">{label}</h3>
      <ul className="command-intro__changes">
        {changes.map((change, index) => {
          const Icon = repositoryChangeIcon(change.kind)
          return (
            <li key={`${change.kind}-${index}`} style={{ '--change-index': index } as CSSProperties}>
              <Icon aria-hidden="true" />
              <span>{change.text}</span>
            </li>
          )
        })}
      </ul>
    </section>
  )
}

function Verdict({ tone, children }: { tone: 'hit' | 'miss'; children: ReactNode }) {
  const Icon = tone === 'hit' ? Check : CircleAlert
  return (
    <p className={`command-intro__verdict is-${tone}`} role="status">
      <Icon aria-hidden="true" />
      <span>{children}</span>
    </p>
  )
}
