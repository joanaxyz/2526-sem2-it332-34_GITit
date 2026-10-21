import { useCallback, useEffect, useRef, useState } from 'react'

import { FloatingMascotLauncher } from '@/shared/mascot/FloatingMascotLauncher'
import { TutorWindow, type TutorWindowDismissal } from './TutorWindow'

const HOME_CONTEXT = { surface: 'home' } as const

/** General help on Home, the map, and the shop: a chat window that collapses into Git-It. */
export function HomeTutor() {
  const [open, setOpen] = useState(true)
  const launcher = useRef<HTMLButtonElement>(null)
  const refocusLauncher = useRef(false)

  useEffect(() => {
    // The roaming mascot steps aside while Git-It is chatting.
    document.documentElement.toggleAttribute('data-home-tutor-open', open)
    if (!open && refocusLauncher.current) {
      refocusLauncher.current = false
      launcher.current?.focus()
    }
    return () => document.documentElement.removeAttribute('data-home-tutor-open')
  }, [open])

  const dismiss = useCallback((how: TutorWindowDismissal) => {
    // Escape returns focus to the launcher; a click elsewhere leaves it there.
    refocusLauncher.current = how === 'escape'
    setOpen(false)
  }, [])

  return (
    <>
      <FloatingMascotLauncher
        name="home-tutor"
        label="Ask Git-It"
        caption="Ask Git-It"
        open={open}
        buttonRef={launcher}
        onOpen={() => setOpen(true)}
      />
      {open ? <TutorWindow context={HOME_CONTEXT} onDismiss={dismiss} /> : null}
    </>
  )
}
