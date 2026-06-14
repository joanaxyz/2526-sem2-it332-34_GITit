import { useEffect, useRef } from 'react'

export function CursorGlow() {
  const glowRef = useRef<HTMLDivElement>(null)
  const rafRef = useRef<number | null>(null)

  useEffect(() => {
    // Only activate on devices with a precise pointer (mouse), not touch
    if (!window.matchMedia('(pointer: fine)').matches) return

    function handleMouseMove(e: MouseEvent) {
      // Skip if an RAF is already queued - at most one update per frame
      if (rafRef.current !== null) return
      rafRef.current = requestAnimationFrame(() => {
        if (glowRef.current) {
          glowRef.current.style.background =
            `radial-gradient(600px circle at ${e.clientX}px ${e.clientY}px, rgba(0, 212, 170, 0.07), transparent 70%)`
        }
        rafRef.current = null
      })
    }

    function handleClick(e: MouseEvent) {
      const ripple = document.createElement('div')
      ripple.style.cssText = `
        position: fixed;
        left: ${e.clientX}px;
        top: ${e.clientY}px;
        width: 0;
        height: 0;
        border-radius: 50%;
        border: 2px solid rgba(0, 212, 170, 0.4);
        transform: translate(-50%, -50%);
        pointer-events: none;
        z-index: 9999;
        animation: cursor-ripple 0.6s ease-out forwards;
      `
      document.body.appendChild(ripple)
      // Primary cleanup via animationend; setTimeout as fallback
      ripple.addEventListener('animationend', () => ripple.remove(), { once: true })
      setTimeout(() => ripple.remove(), 700)
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('click', handleClick)

    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('click', handleClick)
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current)
        rafRef.current = null
      }
    }
  }, [])

  return (
    <div
      ref={glowRef}
      aria-hidden="true"
      style={{
        position: 'fixed',
        inset: 0,
        pointerEvents: 'none',
        zIndex: 0,
        willChange: 'background',
        transition: 'background 0.1s ease',
      }}
    />
  )
}
