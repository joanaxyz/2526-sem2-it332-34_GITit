import { useEffect } from 'react'
import { useBlocker } from 'react-router-dom'

type UnsavedChangesGuardOptions = {
  when: boolean
  message?: string
  allowedNextLocation?: string | null
}

const DEFAULT_MESSAGE = 'You have unsaved authoring changes. Leave this page and discard them?'

export function useUnsavedChangesGuard({
  when,
  message = DEFAULT_MESSAGE,
  allowedNextLocation = null,
}: UnsavedChangesGuardOptions) {
  const blocker = useBlocker(({ currentLocation, nextLocation }) => {
    const currentLocationKey = `${currentLocation.pathname}${currentLocation.search}${currentLocation.hash}`
    const nextLocationKey = `${nextLocation.pathname}${nextLocation.search}${nextLocation.hash}`
    if (allowedNextLocation === nextLocationKey) return false
    if (!when) return false
    return currentLocationKey !== nextLocationKey
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
