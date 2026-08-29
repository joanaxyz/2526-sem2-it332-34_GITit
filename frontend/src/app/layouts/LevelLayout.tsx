import { useEffect } from 'react'
import { Outlet, useLocation } from 'react-router-dom'

import { startBackgroundMusic, stopBackgroundMusic } from '@/shared/audio/battleAudio'

export function LevelLayout() {
  const location = useLocation()

  useEffect(() => {
    startBackgroundMusic('inside')
  }, [location.pathname])

  useEffect(() => {
    return () => stopBackgroundMusic('inside')
  }, [])

  return <Outlet />
}
