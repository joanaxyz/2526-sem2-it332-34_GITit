import { useCallback, useEffect, useState } from 'react'
import { ArrowRight, UserRoundPlus, X } from 'lucide-react'
import { Link } from 'react-router-dom'

import { SHOP_ROUTE } from '@/shared/navigation/routes'
import { useAppOnboarding } from '@/features/onboarding/hooks/onboardingContext'
import { useAuthStore } from '@/shared/auth/useAuth'

/* First-step nudge ---------------------------------------------------------
   The only blocking prerequisite a new player has is owning a companion, and
   Home is where they land. The nudge is deliberately NOT part of the overview
   flow: it is pinned to the viewport so arriving without a companion never
   reshuffles the dashboard under the player, and it disappears for good the
   moment a companion is owned. Contextual surfaces that already carry their
   own companion prompt (the story map rail, the Shop itself) do not render it.

   It is the guided journey's backstop, not its rival: while the tutorial is
   still running its banner states the prerequisite, so the nudge stays quiet
   and only turns on once the journey ends ("done" - finished or skipped) with
   the player still owning nothing. For the same reason dismissal is scoped to
   the browsing session instead of being remembered forever: a player who has
   still not bought a companion is still blocked, so the next visit says so
   again rather than leaving them on a dashboard that never mentions it. */

const NUDGE_VERSION = 'v2'

function storageKey(userId?: number | null) {
  return `git-it-first-step-nudge:${NUDGE_VERSION}:${userId ?? 'guest'}`
}

/* Session-scoped storage, so the prompt returns on the next visit while the
   player is still without a companion. */
function safeStorage() {
  if (typeof window === 'undefined') return null
  try {
    return window.sessionStorage
  } catch {
    return null
  }
}

function wasDismissed(userId?: number | null) {
  const storage = safeStorage()
  if (!storage) return false
  try {
    return storage.getItem(storageKey(userId)) === 'dismissed'
  } catch {
    return false
  }
}

export function HomeFirstStepNudge() {
  const userId = useAuthStore((state) => state.user?.id)
  const onboarding = useAppOnboarding()
  const [dismissed, setDismissed] = useState(() => wasDismissed(userId))

  useEffect(() => {
    setDismissed(wasDismissed(userId))
  }, [userId])

  const dismiss = useCallback(() => {
    setDismissed(true)
    const storage = safeStorage()
    if (!storage) return
    try {
      storage.setItem(storageKey(userId), 'dismissed')
    } catch {
      // Storage can be blocked in privacy modes; dismissal must not crash Home.
    }
  }, [userId])

  // The tutorial owns the message while it is still walking the player through
  // setup; the nudge takes over the moment that journey ends.
  if (onboarding && onboarding.phase !== 'done') return null
  if (dismissed) return null

  return (
    <aside className="home-first-step" role="note" aria-label="First step">
      <span className="home-first-step-mark" aria-hidden="true">
        <UserRoundPlus />
      </span>
      <div className="home-first-step-copy">
        <strong>Choose your first companion</strong>
        <p>Adventures and Challenges need one, and you can afford any of them.</p>
      </div>
      <Link className="home-first-step-action" to={`${SHOP_ROUTE}?required=1`}>
        Open Shop
        <ArrowRight aria-hidden="true" />
      </Link>
      <button type="button" className="home-first-step-dismiss" onClick={dismiss} aria-label="Dismiss first step">
        <X aria-hidden="true" />
      </button>
    </aside>
  )
}
