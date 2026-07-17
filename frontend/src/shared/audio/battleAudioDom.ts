const audioCache = new Map<string, HTMLAudioElement>()

export function canUseAudio(): boolean {
  return import.meta.env.MODE !== 'test' && typeof window !== 'undefined' && typeof Audio !== 'undefined'
}

export function audioClockNow(): number {
  if (typeof window !== 'undefined' && window.performance) return window.performance.now()
  return Date.now()
}

export function loadAudio(src: string): HTMLAudioElement {
  const cached = audioCache.get(src)
  if (cached) return cached
  const audio = new Audio(src)
  audio.preload = 'auto'
  audioCache.set(src, audio)
  return audio
}

export function tryPlay(audio: HTMLAudioElement, onReject?: () => void): void {
  try {
    const result = audio.play()
    void result.catch(() => {
      onReject?.()
    })
  } catch {
    onReject?.()
  }
}

export function fadeOut(audio: HTMLAudioElement, durationMs: number): void {
  if (durationMs <= 0 || typeof window.requestAnimationFrame !== 'function') {
    audio.pause()
    audio.currentTime = 0
    return
  }

  const started = window.performance.now()
  const startVolume = audio.volume
  const step = (now: number) => {
    const progress = Math.min(1, (now - started) / durationMs)
    audio.volume = startVolume * (1 - progress)
    if (progress < 1) {
      window.requestAnimationFrame(step)
      return
    }
    audio.pause()
    audio.currentTime = 0
    audio.volume = startVolume
  }
  window.requestAnimationFrame(step)
}
