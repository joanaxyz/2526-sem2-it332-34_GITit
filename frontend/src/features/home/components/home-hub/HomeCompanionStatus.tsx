import { AlertTriangle, BookOpen, UserRoundPlus } from 'lucide-react'
import { Link } from 'react-router-dom'

import type { UnresolvedCompanionPresentation } from './companionPresentation'
import { SHOP_ROUTE } from '@/shared/navigation/routes'

type HomeCompanionStatusProps = {
  companion: UnresolvedCompanionPresentation
}

const STATUS_COPY = {
  loading: {
    title: 'Loading companion',
    detail: 'Checking your equipped companion.',
    spellbook: 'Loading your companion before preparing battle spells.',
  },
  error: {
    title: 'Companion unavailable',
    detail: 'Refresh the page to try loading your companion again.',
    spellbook: 'Companion data could not be loaded. Refresh the page to try again.',
  },
  empty: {
    title: 'No companion selected',
    detail: 'Recruit a companion to unlock the animated showcase.',
    spellbook: 'Choose a companion before binding learned commands to battle spells.',
  },
} as const

function CompanionStatusIcon({ status }: { status: UnresolvedCompanionPresentation['status'] }) {
  if (status === 'loading') {
    return <div className="home-companion-status-placeholder" aria-hidden="true" />
  }
  if (status === 'error') return <AlertTriangle aria-hidden="true" />
  return <UserRoundPlus aria-hidden="true" />
}

export function HomeCompanionAnnouncement({ companion }: HomeCompanionStatusProps) {
  if (companion.status === 'empty') return null
  const copy = STATUS_COPY[companion.status]

  return companion.status === 'error' ? (
    <p className="sr-only" role="alert">
      {copy.title}. {copy.detail}
    </p>
  ) : (
    <p className="sr-only" role="status" aria-live="polite">
      {copy.title}. {copy.detail}
    </p>
  )
}

export function HomeProfileCompanionStatus({ companion }: HomeCompanionStatusProps) {
  const copy = STATUS_COPY[companion.status]

  return (
    <div className={`home-profile-companion-empty home-companion-status--${companion.status}`}>
      <CompanionStatusIcon status={companion.status} />
      <span>{copy.title}</span>
      {companion.status === 'empty' ? (
        <Link to={`${SHOP_ROUTE}?tab=companions&required=1`}>Choose companion</Link>
      ) : (
        <small>{copy.detail}</small>
      )}
    </div>
  )
}

export function HomeCombatCompanionStatus({ companion }: HomeCompanionStatusProps) {
  const copy = STATUS_COPY[companion.status]

  return (
    <>
      <section className="ref-panel home-sprite-panel">
        <header className="ref-panel-head">Sprite Showcase</header>
        <div
          className={`home-sprite-stage home-sprite-stage--empty home-companion-status--${companion.status}`}
        >
          <CompanionStatusIcon status={companion.status} />
          <strong>{copy.title}</strong>
          <span>{copy.detail}</span>
          {companion.status === 'empty' ? (
            <Link to={`${SHOP_ROUTE}?tab=companions&required=1`}>Choose companion</Link>
          ) : null}
        </div>
      </section>

      <section className="ref-panel home-spellbook-panel">
        <header className="ref-panel-head">
          <BookOpen aria-hidden="true" />
          Spellbook
        </header>
        <p className="home-spellbook-empty">{copy.spellbook}</p>
      </section>
    </>
  )
}
