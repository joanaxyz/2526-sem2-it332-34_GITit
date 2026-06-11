import { useEffect, useState } from 'react'

/** Cubic ease-out count-up, matching the home hub's number animations. */
export function useCountUp(target: number | null, duration = 900): number {
  const [value, setValue] = useState(0)
  useEffect(() => {
    if (target === null || target === 0) {
      // Settle on the next frame: setting state synchronously inside an effect
      // forces a cascading re-render (react-hooks/set-state-in-effect).
      const frame = requestAnimationFrame(() => setValue(target ?? 0))
      return () => cancelAnimationFrame(frame)
    }
    const startTime = performance.now()
    let frame = 0
    const tick = (now: number) => {
      const p = Math.min((now - startTime) / duration, 1)
      setValue((1 - Math.pow(1 - p, 3)) * target)
      if (p < 1) frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [target, duration])
  return value
}
