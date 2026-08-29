import { Music, Volume2, VolumeX } from 'lucide-react'
import { useEffect, useState } from 'react'

import {
  isBattleMusicEnabled,
  isBattleSoundEnabled,
  setBattleMusicEnabled,
  setBattleSoundEnabled,
  subscribeBattleMusicEnabled,
  subscribeBattleSoundEnabled,
} from '@/shared/audio/battleAudio'
import { cn } from '@/shared/utils/cn'

export function AudioControls({
  className,
  buttonClassName,
}: {
  className?: string
  buttonClassName?: string
}) {
  const [soundEnabled, setSoundEnabledState] = useState(isBattleSoundEnabled)
  const [musicEnabled, setMusicEnabledState] = useState(isBattleMusicEnabled)
  const SoundIcon = soundEnabled ? Volume2 : VolumeX
  const soundLabel = soundEnabled
    ? 'Sound effects on. Turn sound effects off.'
    : 'Sound effects off. Turn sound effects on.'
  const musicLabel = musicEnabled ? 'Music on. Turn music off.' : 'Music off. Turn music on.'

  useEffect(() => subscribeBattleSoundEnabled(setSoundEnabledState), [])
  useEffect(() => subscribeBattleMusicEnabled(setMusicEnabledState), [])

  return (
    <div className={className} aria-label="Audio controls">
      <button
        type="button"
        className={cn(buttonClassName, !soundEnabled && 'is-muted')}
        title={soundLabel}
        aria-label={soundLabel}
        aria-pressed={soundEnabled}
        onClick={() => setBattleSoundEnabled(!soundEnabled)}
      >
        <SoundIcon aria-hidden="true" />
      </button>
      <button
        type="button"
        className={cn(buttonClassName, !musicEnabled && 'is-muted')}
        title={musicLabel}
        aria-label={musicLabel}
        aria-pressed={musicEnabled}
        onClick={() => setBattleMusicEnabled(!musicEnabled)}
      >
        <Music aria-hidden="true" />
      </button>
    </div>
  )
}
