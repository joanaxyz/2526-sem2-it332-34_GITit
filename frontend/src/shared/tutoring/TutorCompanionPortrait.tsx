import { useEffect } from 'react'
import type { CompanionDef } from '@/shared/cosmetics/types'

/** Chat art is separate from the full-size portraits and combat sprites. */
export function TutorCompanionPortrait({ companion, thinking = false, className = '' }: {
  companion: CompanionDef
  thinking?: boolean
  className?: string
}) {
  const avatar = companion.sprites.chatAvatar
  const sprite = companion.sprites.chatThinking
  useEffect(() => {
    if (!sprite) return
    const preload = new Image()
    preload.src = sprite.src
  }, [sprite])
  return (
    <span className={`tutor-companion ${className}`} data-companion={companion.id} data-thinking={(thinking && Boolean(sprite)) || undefined} aria-hidden="true">
      <img className="tutor-companion__idle" src={avatar?.src ?? companion.sprites.avatar?.src} alt="" width={256} height={256} draggable={false} />
      {thinking && sprite ? <span className="tutor-companion__thinking" style={{ backgroundImage: `url("${sprite.src}")` }} /> : null}
    </span>
  )
}
