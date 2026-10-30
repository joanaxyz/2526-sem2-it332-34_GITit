import { useCallback, useEffect, useRef } from 'react'

import { FloatingMascotLauncher } from '@/shared/mascot/FloatingMascotLauncher'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'
import { usePersistentState } from '@/shared/utils/persistentState'
import { TutorCompanionPortrait } from './TutorCompanionPortrait'
import { TutorWindow, type TutorWindowDismissal } from './TutorWindow'

/**
 * Help scoped to a run's command guide: the one in view, else the latest it
 * showed. Its companion launcher stands apart from the guide's own launcher,
 * opens in its own window, and stays while the guide is collapsed. Whether the
 * learner keeps it open is remembered across guides.
 */
export function GuideTutor({ runId, teachingKey, usageForm, guideToken }: { runId: number; teachingKey: string; usageForm: string; guideToken: string }) {
  const { companion } = usePlayerLoadout()
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
        homeSlot="lower"
        label={`Ask ${companion.label}`}
        caption={`Ask ${companion.label}`}
        portrait={<TutorCompanionPortrait companion={companion} className="tutor-companion--launcher" />}
        open={open}
        buttonRef={launcher}
        onOpen={() => setOpen(true)}
      />
      {open ? (
        <TutorWindow
          companion={companion}
          workspace
          context={{ surface: 'command_guide', run_id: runId, teaching_key: teachingKey, usage_form: usageForm, guide_token: guideToken }}
          onDismiss={dismiss}
        />
      ) : null}
    </>
  )
}
