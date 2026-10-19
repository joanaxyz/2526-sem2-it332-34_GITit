import { useId } from 'react'

import { companionSkillForCommand } from '@/shared/cosmetics/companions/companionSkills'

/** A single still from the shipped spell sheet, clipped before responsive scaling. */
export function CompanionSkillPortrait({ companionSlug, command, title, className }: {
  companionSlug: string | null | undefined
  command: string
  title: string
  className?: string
}) {
  const clipId = useId()
  const skill = companionSkillForCommand(companionSlug, command)
  const { animation } = skill
  const { frameWidth, frameHeight, columns, rows, frameCount, src } = animation
  const frame = Math.max(0, Math.min(frameCount - 1, skill.impactStartFrame ?? Math.floor(frameCount / 2)))
  const x = (frame % columns) * frameWidth
  const y = Math.floor(frame / columns) * frameHeight

  return (
    <svg
      role="img"
      aria-label={title}
      viewBox={`0 0 ${frameWidth} ${frameHeight}`}
      className={className}
      focusable="false"
    >
      <title>{title}</title>
      <defs><clipPath id={clipId}><rect width={frameWidth} height={frameHeight} /></clipPath></defs>
      <g clipPath={`url(#${clipId})`}>
        <image
          href={src}
          x={-x}
          y={-y}
          width={columns * frameWidth}
          height={rows * frameHeight}
        />
      </g>
    </svg>
  )
}
