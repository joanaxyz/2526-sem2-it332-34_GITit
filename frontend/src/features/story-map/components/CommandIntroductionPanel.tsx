import { Check, CircleAlert, CornerDownLeft } from 'lucide-react'
import type { CSSProperties, ReactNode } from 'react'

import type { CommandIntroduction } from '@/features/story-map/api/commandIntroductionsApi'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { useCommandIntroduction } from '@/features/story-map/hooks/useCommandIntroduction'
import { commandFamilyIcon, repositoryChangeIcon } from '@/features/story-map/utils/commandIntroductionIcons'
import { GameplayWorkspaceTour, type WorkspaceTourStep } from '@/shared/level/components/GameplayWorkspaceTour'

type RepositoryChange = CommandIntroduction['needs'][number]

/** Introduces the one new command form the repository needs next ("Command guide"). */
export function CommandIntroductionPanel({ run, tutor, onDismiss }: {
  run: TierRun
  tutor: CommandIntroduction
  onDismiss: () => void
}) {
  const lesson = useCommandIntroduction(run, tutor)
  const introduction = tutor.phase === 'introduction'
  const missed = tutor.verdict === 'incorrect'
  const form = tutor.command_form
  const focusTerminal = () => {
    requestAnimationFrame(() => document.querySelector<HTMLInputElement>('[data-command-input]')?.focus())
  }

  let body: ReactNode
  if (introduction) {
    body = (
      <>
        <CommandSyntax usage={form.usage_form} />
        {form.summary ? <p className="command-intro__summary">{form.summary}</p> : null}
        <ChangeList label="Your repository needs" changes={tutor.needs} />
        <p className="command-intro__note">Type it in the terminal. It counts toward your command limit.</p>
      </>
    )
  } else if (missed) {
    body = (
      <>
        <Verdict tone="miss">{tutor.explanation}</Verdict>
        {tutor.example_command ? (
          <section className="command-intro__section" aria-label="Command to try">
            <h3 className="command-intro__label">Try this</h3>
            <code className="command-intro__example">{tutor.example_command}</code>
          </section>
        ) : <CommandSyntax usage={form.usage_form} />}
        <ChangeList label="It will" changes={tutor.needs} />
        {lesson.error ? <p className="command-intro__error" role="alert">{lesson.error}</p> : null}
      </>
    )
  } else {
    body = (
      <>
        <Verdict tone="hit">{tutor.explanation}</Verdict>
        <CommandSyntax usage={form.usage_form} compact />
        <ChangeList label="What changed" changes={tutor.changes} />
        {lesson.error ? <p className="command-intro__error" role="alert">{lesson.error}</p> : null}
      </>
    )
  }

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
      finishLabel={introduction ? 'Try it' : lesson.pending ? 'Saving…' : 'Got it'}
      finishIcon={introduction ? CornerDownLeft : Check}
      finishDisabled={lesson.pending}
      cardClassName="command-intro"
      skipLabel="Not now"
      showSkip={introduction}
      showProgress={false}
      onClose={(reason) => {
        if (introduction) {
          onDismiss()
          if (reason === 'finish') focusTerminal()
        } else if (reason === 'finish') {
          void lesson.complete().then((completed) => { if (completed) focusTerminal() })
        }
      }}
    />
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
