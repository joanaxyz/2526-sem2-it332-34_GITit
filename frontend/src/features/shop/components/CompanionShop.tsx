import { CheckCircle2, Flame, Sparkles, User } from 'lucide-react'
import { type CSSProperties, useMemo, useState } from 'react'

import { ShopCarousel } from '@/features/shop/components/ShopCarousel'
import { actionDisabled, actionLabel, formatCoins, statusLabel, type ShopDisplayItem } from '@/features/shop/utils/shopDisplay'
import { SkillEffectStage } from '@/shared/battle/components/SkillEffectStage'
import { EmptyState } from '@/shared/components/EmptyState'
import { companionSkills, type CompanionSkill } from '@/shared/cosmetics/companions/companionSkills'
import { COMPANIONS } from '@/shared/cosmetics/companions/registry'
import { companionFromDef, companionPreviewAnimations } from '@/shared/cosmetics/companionRuntime'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { SpriteAnimation } from '@/shared/sprites/types'
import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'

/* Companions -------------------------------------------------------------- */

const moveLabels: Record<string, string> = {
  idle: 'Idle',
  run: 'Run',
  attack: 'Attack',
  hurt: 'Hurt',
  death: 'Death',
}

const companionElement: Record<string, string> = {
  blue: 'Arcane Flame',
  white: 'Frost & Ice',
  black: 'Storm & Lightning',
}

type PoseItem = { key: string; label: string; animation: SpriteAnimation; oneShot: boolean }

export function CompanionShop({
  balance,
  companions,
  onAction,
  pending,
  walletPending,
}: {
  balance: number
  companions: ShopDisplayItem[]
  onAction: (item: ShopDisplayItem) => void
  pending: boolean
  walletPending: boolean
}) {
  const [index, setIndex] = useState(0)
  const selected = companions[Math.min(index, companions.length - 1)]

  if (!selected) {
    return (
      <section className="shop-view shop-empty-panel">
        <EmptyState title="No characters available" description="The shop catalog has no companions right now." />
      </section>
    )
  }

  return (
    <section className="shop-view shop-view--companions" aria-labelledby="companion-shop-title">
      <div className="shop-stage shop-stage--portrait" data-tone={selected.tone}>
        <ShopCarousel
          className="shop-portrait-carousel"
          ariaLabel="Companion portraits"
          items={companions}
          index={index}
          onIndexChange={setIndex}
          getKey={(companion) => companion.slug}
          renderSlide={(companion, _i, active) => (
            <article className="shop-portrait-slide" data-tone={companion.tone} data-active={active}>
              <div className="shop-portrait-art">
                {companion.art ? <img src={companion.art} alt={companion.label} loading="lazy" /> : null}
              </div>
              <div className="shop-portrait-caption">
                <span className="shop-status-chip" data-state={companion.active ? 'equipped' : companion.owned ? 'owned' : 'locked'}>
                  {statusLabel(companion)}
                </span>
                <h2 className="shop-portrait-title">{companion.label}</h2>
              </div>
            </article>
          )}
        />
        <div className="shop-portrait-thumbs" role="tablist" aria-label="Companion quick select">
          {companions.map((companion, thumbIndex) => (
            <button
              key={companion.slug}
              type="button"
              role="tab"
              aria-selected={thumbIndex === index}
              aria-label={`Select ${companion.label}`}
              className="shop-portrait-thumb"
              data-active={thumbIndex === index}
              onClick={() => setIndex(thumbIndex)}
            >
              {companion.art ? <img src={companion.art} alt="" loading="lazy" /> : null}
            </button>
          ))}
        </div>
      </div>

      <CompanionPreviewSuite companionSlug={selected.slug} key={selected.slug} />

      <CompanionDetailPanel
        balance={balance}
        companion={selected}
        onAction={onAction}
        pending={pending}
        walletPending={walletPending}
      />
    </section>
  )
}

function CompanionDetailPanel({
  balance,
  companion,
  onAction,
  pending,
  walletPending,
}: {
  balance: number
  companion: ShopDisplayItem
  onAction: (item: ShopDisplayItem) => void
  pending: boolean
  walletPending: boolean
}) {
  const spellCount = companionSkills(companion.slug).length
  const element = companionElement[companion.slug]
  return (
    <aside className="ref-panel shop-detail-panel">
      <p className="shop-detail-eyebrow">Adventurer</p>
      <h1 id="companion-shop-title">{companion.label}</h1>
      <span className="shop-panel-rule" aria-hidden="true" />
      <div className="shop-includes-list">
        {element ? <span><Flame aria-hidden="true" /> {element} combat skills</span> : null}
        <span><Sparkles aria-hidden="true" /> {spellCount} animated git-command skill sprites</span>
        <span><User aria-hidden="true" /> Idle, run &amp; battle poses</span>
      </div>
      <div className="shop-buy-block">
        <div className="shop-price-block">
          {companion.price > 0 ? (
            <>
              <GitCoinIcon />
              <span>
                <strong>{formatCoins(companion.price)}</strong>
                <small>GitCoins</small>
              </span>
            </>
          ) : (
            <span>
              <strong>Free</strong>
              <small>Included with your account</small>
            </span>
          )}
        </div>
        <button
          type="button"
          className="shop-primary-action"
          disabled={actionDisabled(companion, pending, balance, walletPending)}
          onClick={() => onAction(companion)}
        >
          {companion.owned ? <CheckCircle2 aria-hidden="true" /> : null}
          {actionLabel(companion, balance, walletPending)}
        </button>
      </div>
      <p className="shop-purchase-note">
        <span aria-hidden="true">i</span>
        Owned companions are permanent account unlocks. Skill sprites are previewed separately from companion poses.
      </p>
    </aside>
  )
}

const POSE_STAGE_HEIGHT = 260

function CompanionPreviewSuite({ companionSlug }: { companionSlug: string }) {
  return (
    <div className="shop-companion-preview-suite">
      <CompanionPosePreview companionSlug={companionSlug} />
      <SkillSpritePreview companionSlug={companionSlug} />
    </div>
  )
}

function CompanionPosePreview({ companionSlug }: { companionSlug: string }) {
  const companionDef = COMPANIONS[companionSlug]
  const companion = useMemo(() => (companionDef ? companionFromDef(companionDef) : null), [companionDef])
  const poses = useMemo<PoseItem[]>(() => {
    const preview = companionDef ? companionPreviewAnimations(companionDef) : {}
    return Object.entries(preview).map(([key, animation]) => ({
      key,
      label: moveLabels[key] ?? key,
      animation,
      oneShot: key !== 'idle' && key !== 'run',
    }))
  }, [companionDef])
  const [activePoseKey, setActivePoseKey] = useState(() => poses[0]?.key ?? 'idle')
  const [playKey, setPlayKey] = useState(0)

  if (!companion || !companionDef || poses.length === 0) {
    return <div className="shop-companion-preview shop-companion-preview--empty" aria-hidden="true" />
  }

  const activePose = poses.find((pose) => pose.key === activePoseKey) ?? poses[0]
  const scale = POSE_STAGE_HEIGHT / (companionDef.sprites.idle?.frameHeight ?? 256)

  function selectPose(pose: PoseItem) {
    setActivePoseKey(pose.key)
    setPlayKey((key) => key + 1)
  }

  return (
    <section className="shop-companion-preview" aria-label={`${companionDef.label} pose preview`}>
      <header className="shop-block-head">
        <span>Companion Pose Preview</span>
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
      </div>
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
    </section>
  )
}

function SkillSpritePreview({ companionSlug }: { companionSlug: string }) {
  const skills = useMemo(() => companionSkills(companionSlug), [companionSlug])
  const [activeFamily, setActiveFamily] = useState(() => skills[0]?.family ?? '')
  const [playKey, setPlayKey] = useState(0)
  const activeSkill = skills.find((skill) => skill.family === activeFamily) ?? skills[0]

  if (!activeSkill) {
    return (
      <section className="shop-skill-preview shop-skill-preview--empty">
        <EmptyState title="No skill sprites" description="This companion has no standalone skill sprites registered yet." />
      </section>
    )
  }

  function selectSkill(skill: CompanionSkill) {
    setActiveFamily(skill.family)
    setPlayKey((key) => key + 1)
  }

  return (
    <section className="shop-skill-preview" aria-label={`${activeSkill.command} skill sprite preview`}>
      <header className="shop-block-head">
        <span>Skill Effect Preview</span>
        <small>Live cast · flies and lands on a target</small>
      </header>
      <div className="shop-skill-preview-body">
        <div className="shop-skill-stage" style={{ '--skill-tint': activeSkill.tint } as CSSProperties}>
          <SkillEffectStage
            key={`${activeSkill.family}-${playKey}`}
            skill={activeSkill.family}
            companionSlug={companionSlug}
            sizeScale={1.8}
            aria-label={`${activeSkill.command} skill effect`}
          />
          <div className="shop-skill-caption">
            <strong>{activeSkill.command}</strong>
          </div>
        </div>
        <div className="shop-skill-picker" role="tablist" aria-label="Skill sprites">
          {skills.map((skill) => (
            <PreviewChip
              key={skill.family}
              animation={skill.animation}
              label={skill.command}
              posterFrame={12}
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
  const col = posterFrame % columns
  const row = Math.floor(posterFrame / columns)
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
        style={{
          backgroundImage: `url(${animation.src})`,
          backgroundSize: `${columns * 100}% ${rows * 100}%`,
          backgroundPosition: `${x}% ${y}%`,
          imageRendering: pixelated ? 'pixelated' : 'auto',
        }}
      />
      <span className="shop-preview-chip-label">{label}</span>
    </button>
  )
}
