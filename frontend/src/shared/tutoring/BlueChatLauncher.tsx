import { useEffect, useState, type Ref } from 'react'
import { createPortal } from 'react-dom'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { SpriteAnimation } from '@/shared/sprites/types'
import './blue-chat-launcher.css'

const BLUE_FLOAT: SpriteAnimation = {
  name: 'blue.chat.idle', src: '/mascot/float.png', frameWidth: 256, frameHeight: 256,
  columns: 5, rows: 5, frameCount: 25, fps: 24, loop: true,
}

/** The original animated Blue launcher, opening the current shared tutor. */
export function BlueChatLauncher({ open, onOpen, buttonRef }: {
  open: boolean
  onOpen: () => void
  buttonRef: Ref<HTMLButtonElement>
}) {
  const [compact, setCompact] = useState(() => window.matchMedia?.('(max-width: 640px)').matches === true)
  useEffect(() => {
    const media = window.matchMedia?.('(max-width: 640px)')
    if (!media) return
    const update = () => setCompact(media.matches)
    media.addEventListener('change', update)
    return () => media.removeEventListener('change', update)
  }, [])
  return createPortal(<button ref={buttonRef} type="button" className="blue-chat-launcher"
    hidden={open} aria-label="Ask Blue" aria-haspopup="dialog" aria-expanded={open} onClick={onOpen}>
    {!open ? <SpriteAnimator animation={BLUE_FLOAT} scale={(compact ? 104 : 144) / 256}
      pixelated anchorToPixelBounds pixelAnchorFallback={{ bottomOffset: 0 }} aria-label="Blue, Git learning assistant" /> : null}
    <span className="blue-chat-launcher__label" aria-hidden="true">Ask Blue</span>
  </button>, document.body)
}
