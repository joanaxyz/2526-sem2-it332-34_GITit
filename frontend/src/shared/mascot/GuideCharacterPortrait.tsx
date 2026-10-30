import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'
import { useGuideMascotVisibility } from './useGuideMascotVisibility'

const MASCOT_PORTRAIT_SRC = '/mascot/portrait.png'

type PortraitProps = {
  className?: string
  alt: string
  width: number
  height: number
}

/** Guides speak as Git-It while the mascot is shown; otherwise as the equipped companion. */
export function GuideCharacterPortrait({ className, alt = 'Git-It guide', width = 72, height = 90 }: {
  className?: string
  alt?: string
  width?: number
  height?: number
}) {
  const guideMascotVisible = useGuideMascotVisibility()
  return guideMascotVisible
    ? <MascotPortrait className={className} alt={alt} width={width} height={height} />
    : <EquippedCompanionPortrait className={className} alt={alt} width={width} height={height} />
}

/** Git-It itself, whatever the guide appearance setting. */
export function MascotPortrait({ className, alt, width, height }: PortraitProps) {
  return <img
    className={className}
    src={MASCOT_PORTRAIT_SRC}
    alt={alt}
    width={width}
    height={height}
    draggable={false}
    data-guide-character="mascot"
  />
}

function EquippedCompanionPortrait({ className, alt, width, height }: PortraitProps) {
  const { companion, hasCompanion } = usePlayerLoadout()
  const companionPortrait = hasCompanion ? companion.sprites.portrait?.src : undefined
  if (!companionPortrait) return <MascotPortrait className={className} alt={alt} width={width} height={height} />

  return <img
    className={className}
    src={companionPortrait}
    alt={`${companion.label} companion`}
    width={width}
    height={height}
    draggable={false}
    data-guide-character="companion"
  />
}
