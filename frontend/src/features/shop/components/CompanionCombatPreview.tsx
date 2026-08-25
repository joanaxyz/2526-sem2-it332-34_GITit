import { type CSSProperties, useMemo, useState } from 'react'

import { EmptyState } from '@/shared/components/EmptyState'
import { companionSkills, type CompanionSkill } from '@/shared/cosmetics/companions/companionSkills'
import { COMPANIONS } from '@/shared/cosmetics/companions/registry'
import { companionFromDef, companionPreviewAnimations } from '@/shared/cosmetics/companionRuntime'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { SpriteAnimation } from '@/shared/sprites/types'

const POSE_STAGE_HEIGHT = 300

const moveLabels: Record<string, string> = {
  idle: 'Idle',
  run: 'Run',
  attack: 'Attack',
  hurt: 'Hurt',
  death: 'Death',
}

type PoseItem = { key: string; label: string; animation: SpriteAnimation }

export function CompanionPosePreview({ companionSlug }: { companionSlug: string }) {
  const companionDef = COMPANIONS[companionSlug]
  const companion = useMemo(() => (companionDef ? companionFromDef(companionDef) : null), [companionDef])
  const poses = useMemo<PoseItem[]>(() => {
    const preview = companionDef ? companionPreviewAnimations(companionDef) : {}
    return Object.entries(preview).map(([key, animation]) => ({
      key,
      label: moveLabels[key] ?? key,
      animation,
    }))
  }, [companionDef])
  const [activePoseKey, setActivePoseKey] = useState(() => poses[0]?.key ?? 'idle')
  const [playKey, setPlayKey] = useState(0)

  if (!companion || !companionDef || poses.length === 0) {
    return <section className="shop-companion-preview shop-inspector-empty" aria-hidden="true" />
  }

  const activePose = poses.find((pose) => pose.key === activePoseKey) ?? poses[0]
  const scale = POSE_STAGE_HEIGHT / (companionDef.sprites.idle?.frameHeight ?? 256)

  function selectPose(pose: PoseItem) {
    setActivePoseKey(pose.key)
    setPlayKey((key) => key + 1)
  }

  return (
    <section className="shop-companion-preview" aria-label={`${companionDef.label} pose inspector`}>
      <header className="shop-block-head">
        <span>Pose</span>
        <small>{activePose.label}</small>
      </header>
      <div className="shop-companion-pose-stage" data-tone={companionSlug}>
        <div className="shop-companion-pose-ground" aria-hidden="true" />
        <SpriteAnimator
          key={`${activePose.key}-${playKey}`}
          animation={activePose.animation}
          scale={scale}
          anchorToPixelBounds
          layoutAnimation={companion.sprites.idle}
          pixelAnchorAnimation={companion.sprites.idle}
          pixelAnchorFallback={{ bottomOffset: companion.metrics.footOffset }}
          pixelated
          aria-label={`${companionDef.label} ${activePose.label}`}
        />
        <div className="shop-companion-pose-controls" role="tablist" aria-label="Companion poses">
          {poses.map((pose) => (
            <PreviewChip
              key={pose.key}
              animation={pose.animation}
              label={pose.label}
              posterFrame={0}
              pixelated
              active={activePose.key === pose.key}
              onSelect={() => selectPose(pose)}
            />
          ))}
        </div>
      </div>
    </section>
  )
}

export function CompanionSkillPreview({ companionSlug }: { companionSlug: string }) {
  const skills = useMemo(() => companionSkills(companionSlug), [companionSlug])
  const [activeFamily, setActiveFamily] = useState(() => skills[0]?.family ?? '')
  const [playKey, setPlayKey] = useState(0)
  const activeSkill = skills.find((skill) => skill.family === activeFamily) ?? skills[0]

  if (!activeSkill) {
    return (
      <section className="shop-skill-preview shop-inspector-empty">
        <EmptyState title="No skill sprites" description="No standalone skill effects are registered." />
      </section>
    )
  }

  function selectSkill(skill: CompanionSkill) {
    setActiveFamily(skill.family)
    setPlayKey((key) => key + 1)
  }

  const skillScale = Math.min(
    1.15,
    236 / Math.max(activeSkill.animation.frameWidth, activeSkill.animation.frameHeight),
  )

  return (
    <section className="shop-skill-preview" aria-label={`${activeSkill.command} skill effect inspector`}>
      <header className="shop-block-head">
        <span>Skill FX</span>
        <small>Live cast</small>
      </header>
      <div className="shop-skill-stage" style={{ '--skill-tint': activeSkill.tint } as CSSProperties}>
        <SpriteAnimator
          key={`${activeSkill.family}-${playKey}`}
          animation={activeSkill.animation}
          scale={skillScale}
          aria-label={`${activeSkill.command} skill effect`}
        />
        <div className="shop-skill-caption">
          <strong>{activeSkill.command}</strong>
        </div>
        <div className="shop-skill-picker" role="tablist" aria-label="Skill effects">
          {skills.map((skill) => (
            <PreviewChip
              key={skill.family}
              animation={skill.animation}
              label={skill.command}
              posterFrame={skill.playback === 'projectile' ? (skill.impactStartFrame ?? 12) : 12}
              active={activeSkill.family === skill.family}
              onSelect={() => selectSkill(skill)}
            />
          ))}
        </div>
      </div>
    </section>
  )
}

function PreviewChip({
  animation,
  label,
  posterFrame,
  pixelated = false,
  active,
  onSelect,
}: {
  animation: SpriteAnimation
  label: string
  posterFrame: number
  pixelated?: boolean
  active: boolean
  onSelect: () => void
}) {
  const { columns, rows } = animation
  const frame = Math.max(0, Math.min(animation.frameCount - 1, posterFrame))
  const col = frame % columns
  const row = Math.floor(frame / columns)
  const x = columns > 1 ? (col * 100) / (columns - 1) : 0
  const y = rows > 1 ? (row * 100) / (rows - 1) : 0

  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      data-active={active}
      className="shop-preview-chip"
      title={label}
      onClick={onSelect}
    >
      <span
        className="shop-preview-chip-art"
        data-pixelated={pixelated || undefined}
        style={{
          backgroundImage: `url(${animation.src})`,
          backgroundSize: `${columns * 100}% ${rows * 100}%`,
          backgroundPosition: `${x}% ${y}%`,
        }}
      />
      <span className="shop-preview-chip-label">{label}</span>
    </button>
  )
}
