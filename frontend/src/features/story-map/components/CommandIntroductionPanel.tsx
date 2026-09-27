import { Check, CircleAlert } from 'lucide-react'
import { useEffect, useId, useState, useSyncExternalStore } from 'react'
import type { CSSProperties, ReactNode } from 'react'

import type { CommandIntroduction } from '@/features/story-map/api/commandIntroductionsApi'
import { RepositoryChangeDiagram } from '@/features/story-map/components/RepositoryChangeDiagram'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { useCommandIntroduction } from '@/features/story-map/hooks/useCommandIntroduction'
import { commandFamilyIcon, repositoryChangeIcon } from '@/features/story-map/utils/commandIntroductionIcons'
import { GameplayWorkspaceTour, type WorkspaceTourStep } from '@/shared/level/components/GameplayWorkspaceTour'

type RepositoryChange = CommandIntroduction['needs'][number]
type Concept = CommandIntroduction['concepts'][number]
type Tab = 'command' | 'change'

// Room for the command card and the "What changes" card side by side, with
// the workspace still visible around them. Below this they share one card.
const WIDE_QUERY = '(min-width: 1180px) and (min-height: 640px)'
// The scenario and project files stay readable while a guide is open.
const CONTEXT_REGIONS = ['[data-tour-target="level-story"]', '[data-tour-target="project-files"]']
const FEEDBACK_REGIONS = [...CONTEXT_REGIONS, '[data-tour-target="terminal"]']

/**
 * "Command guide": introduces the one new command form, or technique, the
 * repository needs next.
 *
 * It explains the command part by part, shows what it will change as a
 * diagram, and defines new words the first times they come up. Wide screens
 * show the guide as one frame holding the explanation and the change as their
 * own cards, each resized on its own; narrower screens use tabs in one card.
 *
 * Before a command it has no buttons: it stays beside the terminal while the
 * learner types and turns into feedback once the command runs. Hiding it (×)
 * is the only way to put it away; the command-bar book can bring it back.
 * After a command, "Got it" records the guide (and its new words) as done.
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
  const missed = tutor.verdict === 'incorrect'
  const form = tutor.command_form
  const primer = tutor.concepts.find((concept) => concept.key === 'commands')
  const words = tutor.concepts.filter((concept) => concept.key !== 'commands')
  const focusTerminal = () => {
    requestAnimationFrame(() => document.querySelector<HTMLInputElement>('[data-command-input]')?.focus())
  }
  useEffect(() => {
    if (introduction && !replay) focusTerminal()
  }, [introduction, replay])

  const error = lesson.error ? <p className="command-intro__error" role="alert">{lesson.error}</p> : null
  const changeTitle = 'What changes'
  const hasChange = (introduction || missed) && (tutor.needs.length > 0 || words.length > 0)
  const change = hasChange ? (
    <>
      <RepositoryChangeDiagram changes={tutor.needs} repository={run.repository_state} />
      <ChangeList label={introduction ? 'Your repository needs' : 'It will'} changes={tutor.needs} />
      <Words concepts={words} />
    </>
  ) : null

  let command: ReactNode
  if (introduction) {
    command = (
      <>
        {primer ? <Primer concept={primer} /> : null}
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
        {tutor.example_command ? (
          <section className="command-intro__section" aria-label="Command to try">
            <h3 className="command-intro__label">Try this</h3>
            <code className="command-intro__example">{tutor.example_command}</code>
          </section>
        ) : <CommandSyntax usage={form.usage_form} />}
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
    <GameplayWorkspaceTour
      label="Command guide"
      steps={[step]}
      refreshKey={tutor.context_id}
      finishLabel={lesson.pending ? 'Saving…' : 'Got it'}
      finishDisabled={lesson.pending}
      cardClassName="command-intro"
      skipLabel={replay ? 'Close command guide' : 'Hide command guide'}
      skipIconOnly
      showSkip={replay || introduction}
      showActions={!replay && !introduction}
      focusCard={replay || !introduction}
      showProgress={false}
      transformable
      paneLabels={{ main: 'command card', aside: `${changeTitle.toLowerCase()} card` }}
      reveal={introduction ? CONTEXT_REGIONS : FEEDBACK_REGIONS}
      collapseTarget="[data-command-guide-launcher]"
      aside={split ? (
        <section className="command-intro__aside" aria-label={changeTitle}>
          <h3 className="command-intro__aside-title">{changeTitle}</h3>
          {change}
        </section>
      ) : undefined}
      onClose={(reason) => {
        if (replay) {
          onDismiss()
          focusTerminal()
          return
        }
        if (reason === 'skip') {
          onDismiss()
          focusTerminal()
        } else {
          void lesson.complete().then((completed) => { if (completed) focusTerminal() })
        }
      }}
    />
  )
}

function sameWords(left: string, right: string) {
  const words = (text: string) => text.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()
  return words(left) === words(right)
}

function useMediaQuery(query: string) {
  return useSyncExternalStore(
    (notify) => {
      const list = window.matchMedia?.(query)
      list?.addEventListener('change', notify)
      return () => list?.removeEventListener('change', notify)
    },
    () => window.matchMedia?.(query).matches ?? false,
    () => false,
  )
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

function Primer({ concept }: { concept: Concept }) {
  return (
    <p className="command-intro__primer">
      <strong>{concept.title}.</strong> {concept.text}
    </p>
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

function Words({ concepts }: { concepts: readonly Concept[] }) {
  if (concepts.length === 0) return null
  return (
    <section className="command-intro__section" aria-label="Words to know">
      <h3 className="command-intro__label">Words to know</h3>
      <dl className="command-intro__words">
        {concepts.map((concept) => (
          <div key={concept.key}>
            <dt>{concept.title}</dt>
            <dd>{concept.text}</dd>
          </div>
        ))}
      </dl>
    </section>
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
