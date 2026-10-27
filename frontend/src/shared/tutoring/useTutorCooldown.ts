import { useEffect, useState, useSyncExternalStore } from 'react'
import { useAuthStore } from '@/shared/auth/useAuth'

let retryUntil = 0
const listeners = new Set<() => void>()
const snapshot = () => retryUntil
const subscribe = (listener: () => void) => { listeners.add(listener); return () => { listeners.delete(listener) } }

export function setTutorCooldown(seconds: number) {
  retryUntil = seconds > 0 ? Math.max(retryUntil, Date.now() + seconds * 1000) : 0
  listeners.forEach((listener) => listener())
}

useAuthStore.subscribe((current, previous) => {
  if (current.sessionGeneration !== previous.sessionGeneration) setTutorCooldown(0)
})

export function useTutorCooldown() {
  const until = useSyncExternalStore(subscribe, snapshot)
  const [now, setNow] = useState(Date.now)
  useEffect(() => {
    setNow(Date.now())
    if (until <= Date.now()) return
    const timer = window.setInterval(() => {
      setNow(Date.now())
      if (Date.now() >= until) window.clearInterval(timer)
    }, 1000)
    return () => window.clearInterval(timer)
  }, [until])
  const remaining = Math.max(0, Math.ceil((until - now) / 1000))
  return { remaining, blocked: remaining > 0 }
}
