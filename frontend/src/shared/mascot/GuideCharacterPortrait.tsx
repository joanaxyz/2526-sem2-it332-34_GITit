import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'

export function GuideCharacterPortrait({ className, alt = 'Git-It guide', width = 72, height = 90 }: {
  className?: string
  alt?: string
  width?: number
  height?: number
}) {
  return <EquippedCompanionPortrait className={className} alt={alt} width={width} height={height} />
}

function EquippedCompanionPortrait({ className, alt, width, height }: {
  className?: string
  alt: string
  width: number
  height: number
}) {
  const { companion, hasCompanion } = usePlayerLoadout()
  const companionPortrait = hasCompanion ? companion.sprites.portrait?.src : undefined
  const src = companionPortrait ?? '/mascot/portrait.png'

  return <img
    className={className}
    src={src}
    alt={companionPortrait ? `${companion.label} companion` : alt}
    width={width}
    height={height}
    draggable={false}
    data-guide-character={companionPortrait ? 'companion' : 'mascot'}
  />
}
