import { ChevronLeft, ChevronRight } from 'lucide-react'
import { type CSSProperties, useEffect, useMemo, useRef, useState } from 'react'

import { EmptyState } from '@/shared/components/EmptyState'
import { companionSkills } from '@/shared/cosmetics/companions/companionSkills'
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

  const activePoseIndex = Math.max(0, poses.findIndex((pose) => pose.key === activePoseKey))
  const activePose = poses[activePoseIndex]
  const scale = POSE_STAGE_HEIGHT / (companionDef.sprites.idle?.frameHeight ?? 256)

  function stepPose(direction: number) {
    const nextPose = poses[(activePoseIndex + direction + poses.length) % poses.length]
    setActivePoseKey(nextPose.key)
    setPlayKey((key) => key + 1)
  }

  return (
    <section className="shop-companion-preview" aria-label={`${companionDef.label} pose inspector`}>
      <header className="shop-block-head">
        <span>Pose</span>
        <small aria-live="polite" aria-atomic="true">{activePose.label}</small>
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
        <PreviewNavigation
          subject="pose"
          disabled={poses.length < 2}
          onPrevious={() => stepPose(-1)}
          onNext={() => stepPose(1)}
        />
      </div>
    </section>
  )
}

export function CompanionSkillPreview({ companionSlug }: { companionSlug: string }) {
  const skills = useMemo(() => companionSkills(companionSlug), [companionSlug])
  const [activeFamily, setActiveFamily] = useState(() => skills[0]?.family ?? '')
  const [playKey, setPlayKey] = useState(0)
  const stageRef = useRef<HTMLDivElement>(null)
  const [stageSize, setStageSize] = useState(236)
  const activeSkillIndex = Math.max(0, skills.findIndex((skill) => skill.family === activeFamily))
  const activeSkill = skills[activeSkillIndex]

  useEffect(() => {
    const stage = stageRef.current
    if (!stage || typeof ResizeObserver === 'undefined') return
    const observer = new ResizeObserver(([entry]) => {
      if (!entry) return
      const { width, height } = entry.contentRect
      if (width > 0 && height > 0) setStageSize(Math.max(1, Math.min(width, height) - 16))
    })
    observer.observe(stage)
    return () => observer.disconnect()
  }, [])

  if (!activeSkill) {
    return (
      <section className="shop-skill-preview shop-inspector-empty">
        <EmptyState title="No skill sprites" description="No standalone skill effects are registered." />
      </section>
    )
  }

  function stepSkill(direction: number) {
    const nextSkill = skills[(activeSkillIndex + direction + skills.length) % skills.length]
    setActiveFamily(nextSkill.family)
    setPlayKey((key) => key + 1)
  }

  const skillScale = Math.min(
    1.15,
    Math.min(236, stageSize) / Math.max(activeSkill.animation.frameWidth, activeSkill.animation.frameHeight),
  )

  return (
    <section className="shop-skill-preview" aria-label={`${activeSkill.command} skill effect inspector`}>
      <header className="shop-block-head">
        <span>Skill FX</span>
        <small>Live cast</small>
      </header>
      <div className="shop-skill-stage" ref={stageRef} style={{ '--skill-tint': activeSkill.tint } as CSSProperties}>
        <SpriteAnimator
          key={`${activeSkill.family}-${playKey}`}
          animation={activeSkill.animation}
          scale={skillScale}
          aria-label={`${activeSkill.command} skill effect`}
        />
        <div className="shop-skill-caption" aria-live="polite" aria-atomic="true">
          <strong>{activeSkill.command}</strong>
        </div>
        <PreviewNavigation
          subject="skill effect"
          disabled={skills.length < 2}
          onPrevious={() => stepSkill(-1)}
          onNext={() => stepSkill(1)}
        />
      </div>
    </section>
  )
}

function PreviewNavigation({
  subject,
  disabled,
  onPrevious,
  onNext,
}: {
  subject: 'pose' | 'skill effect'
  disabled: boolean
  onPrevious: () => void
  onNext: () => void
}) {
  return (
    <>
      <button
        type="button"
        className="shop-carousel-arrow shop-carousel-arrow--left shop-preview-arrow"
        aria-label={`Previous ${subject}`}
        title={`Previous ${subject}`}
        disabled={disabled}
        onClick={onPrevious}
      >
        <ChevronLeft aria-hidden="true" />
      </button>
      <button
        type="button"
        className="shop-carousel-arrow shop-carousel-arrow--right shop-preview-arrow"
        aria-label={`Next ${subject}`}
        title={`Next ${subject}`}
        disabled={disabled}
        onClick={onNext}
      >
        <ChevronRight aria-hidden="true" />
      </button>
    </>
  )
}
