import { useEffect } from 'react'
import { useBlocker } from 'react-router-dom'

type UnsavedChangesGuardOptions = {
  when: boolean
  message?: string
}

const DEFAULT_MESSAGE = 'You have unsaved authoring changes. Leave this page and discard them?'

export function useUnsavedChangesGuard({
  when,
  message = DEFAULT_MESSAGE,
}: UnsavedChangesGuardOptions) {
  const blocker = useBlocker(({ currentLocation, nextLocation }) => {
    if (!when) return false
    return currentLocation.pathname !== nextLocation.pathname || currentLocation.search !== nextLocation.search
  })

  useEffect(() => {
    if (blocker.state !== 'blocked') return
    if (window.confirm(message)) {
      blocker.proceed()
    } else {
      blocker.reset()
    }
  }, [blocker, message])

  useEffect(() => {
    if (!when) return

    function handleBeforeUnload(event: BeforeUnloadEvent) {
      event.preventDefault()
      event.returnValue = ''
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [when])
}
