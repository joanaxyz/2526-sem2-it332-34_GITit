import { useCallback, useEffect, useRef } from 'react'

import { FloatingMascotLauncher } from '@/shared/mascot/FloatingMascotLauncher'
import { usePersistentState } from '@/shared/utils/persistentState'
import { TutorWindow, type TutorWindowDismissal } from './TutorWindow'

/**
 * Help scoped to the open command guide. It starts as an "Ask Git-It" launcher so
 * it never covers the guide card, opens in its own window, and closes with the
 * guide. Whether the learner keeps it open is remembered across guides.
 */
export function GuideTutor({ runId, teachingKey, usageForm, guideToken }: { runId: number; teachingKey: string; usageForm: string; guideToken: string }) {
  const [open, setOpen] = usePersistentState<boolean>('tutor-window:workspace-open', false, (saved) => saved === true)
  const launcher = useRef<HTMLButtonElement>(null)
  const refocusLauncher = useRef(false)

  useEffect(() => {
    if (!open && refocusLauncher.current) {
      refocusLauncher.current = false
      launcher.current?.focus()
    }
  }, [open])

  const dismiss = useCallback((how: TutorWindowDismissal) => {
    // Typing in the terminal must not put the chat away, so only Escape and close do.
    if (how === 'outside') return
    refocusLauncher.current = true
    setOpen(false)
  }, [setOpen])

  return (
    <>
      <FloatingMascotLauncher
        name="guide-tutor"
        label="Ask Git-It"
        caption="Ask Git-It"
        open={open}
        buttonRef={launcher}
        onOpen={() => setOpen(true)}
      />
      {open ? (
        <TutorWindow
          workspace
          context={{ surface: 'command_guide', run_id: runId, teaching_key: teachingKey, usage_form: usageForm, guide_token: guideToken }}
          onDismiss={dismiss}
        />
      ) : null}
    </>
  )
}
