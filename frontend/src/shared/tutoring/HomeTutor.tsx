import { useCallback, useEffect, useRef } from 'react'

import { FloatingMascotLauncher } from '@/shared/mascot/FloatingMascotLauncher'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'
import { usePersistentState } from '@/shared/utils/persistentState'
import { TutorCompanionPortrait } from './TutorCompanionPortrait'
import { TutorWindow, type TutorWindowDismissal } from './TutorWindow'

const HOME_CONTEXT = { surface: 'home' } as const
// On a phone the window would cover most of the page, so it starts as the launcher there.
const PHONE_WIDTH = 720

/**
 * General help on Home, the map, and the shop, voiced by the equipped companion.
 * It remembers whether the learner left it open or closed.
 */
export function HomeTutor() {
  const { companion } = usePlayerLoadout()
  const [open, setOpen] = usePersistentState<boolean>(
    'tutor-window:home-open',
    window.innerWidth > PHONE_WIDTH,
    (saved) => saved === true,
  )
  const launcher = useRef<HTMLButtonElement>(null)
  const refocusLauncher = useRef(false)

  useEffect(() => {
    if (!open && refocusLauncher.current) {
      refocusLauncher.current = false
      launcher.current?.focus()
    }
  }, [open])

  const dismiss = useCallback((how: TutorWindowDismissal) => {
    // Escape and the close button return focus to the launcher; a click elsewhere leaves it there.
    refocusLauncher.current = how !== 'outside'
    setOpen(false)
  }, [setOpen])

  return (
    <>
      <FloatingMascotLauncher
        name="home-tutor"
        label={`Ask ${companion.label}`}
        caption={`Ask ${companion.label}`}
        portrait={<TutorCompanionPortrait companion={companion} className="tutor-companion--launcher" />}
        open={open}
        buttonRef={launcher}
        onOpen={() => setOpen(true)}
      />
      {open ? <TutorWindow companion={companion} context={HOME_CONTEXT} onDismiss={dismiss} /> : null}
    </>
  )
}
