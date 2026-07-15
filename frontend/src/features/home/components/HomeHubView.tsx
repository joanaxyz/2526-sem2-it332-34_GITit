import { type CSSProperties, useMemo, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Backpack, BarChart3, BookOpen, Check, ChevronLeft, ChevronRight, Lock, Star, Trophy, User } from 'lucide-react'

import heroShowcasePedestalImage from '@/assets/images/hero_showcase_pedestal.png'
import rank1BadgeImage from '@/assets/images/rank1.png'
import rank2BadgeImage from '@/assets/images/rank2.png'
import rank3BadgeImage from '@/assets/images/rank3.png'
import rank4BadgeImage from '@/assets/images/rank4.png'
import rank5BadgeImage from '@/assets/images/rank5.png'
import rank6BadgeImage from '@/assets/images/rank6.png'
import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'
import { HomeStatsView } from '@/features/home/components/HomeStatsView'
import { HomeLoadoutView } from '@/features/home/components/HomeLoadoutView'
import { RANK_TIERS, deriveRank } from '@/shared/progress/rank'
import type { RankTier } from '@/shared/progress/rank'
import type { HomeSummary } from '@/features/home/types'
import type { StatsSummary } from '@/features/stats/types'
import { useLearnedSkills } from '@/features/skills/hooks/useLearnedSkills'
import type { LearnedSkill } from '@/features/skills/types'
import { effectForSkill } from '@/shared/battle/effects/effectRegistry'
import { companionBattleFromDef, companionFromDef } from '@/shared/cosmetics/companionRuntime'
import type { SpriteDef } from '@/shared/cosmetics/types'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'
import { DEFAULT_STORY_WORLD_SLUG, getStoryWorld } from '@/shared/story-worlds/registry'
import { animationDuration } from '@/shared/sprites/animationTiming'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { SpriteAnimation, SpriteAnimatorHandle } from '@/shared/sprites/types'
import { useImagePixelBounds } from '@/shared/sprites/usePixelBounds'
import { GitCommandIcon, gitCommandFamily } from '@/shared/git/commandCatalog/commandIcons'

const RANK_BADGE_IMAGES = [
  rank1BadgeImage,
  rank2BadgeImage,
  rank3BadgeImage,
  rank4BadgeImage,
  rank5BadgeImage,
  rank6BadgeImage,
] as const

type ShowcaseMove = {
  label: string
  sheet: SpriteAnimation
  /** Cropped first frame shown in the preview strip. */
  portrait: SpriteDef
  /** One-shots settle back to idle when they finish. */
  oneShot: boolean
}

function formatNumber(value: number | null | undefined, fallback = 0) {
  return (typeof value === 'number' ? value : fallback).toLocaleString()
}

function RankBadge({ tier, className }: { tier: RankTier; className?: string }) {
  const badge = RANK_BADGE_IMAGES[Math.max(0, Math.min(tier.rank - 1, RANK_BADGE_IMAGES.length - 1))]
  return (
    <img
      className={['home-rank-badge', className].filter(Boolean).join(' ')}
      src={badge}
      alt=""
      aria-hidden="true"
    />
  )
}

export function HomeHubView({
  home,
  stats,
  playerName,
  gitcoins,
}: {
  home: HomeSummary
  stats: StatsSummary
  playerName: string
  gitcoins: number | null
}) {
  const rank = deriveRank(home)
  const balance = gitcoins ?? stats.headline.gitcoins ?? 0
  const starsCollected = Math.max(stats.headline.perfect_clears, home.perfect_clears)
  const levelsCleared = stats.headline.levels_completed || home.counts.completed

  const [searchParams, setSearchParams] = useSearchParams()
  const tabParam = searchParams.get('tab')
  const tab: 'overview' | 'loadout' | 'profile' = tabParam === 'profile' ? 'profile' : tabParam === 'loadout' ? 'loadout' : 'overview'
  const selectTab = (next: 'overview' | 'loadout' | 'profile') => {
    setSearchParams(
      (params) => {
        if (next === 'overview') params.delete('tab')
        else params.set('tab', next)
        return params
      },
      { replace: true },
    )
  }

  const { data: skills, isLoading: skillsLoading } = useLearnedSkills()
  const [pickedId, setPickedId] = useState<number | null>(null)
  const hasSkills = (skills?.length ?? 0) > 0
  const selectedId = pickedId ?? skills?.[0]?.id ?? null
  const { companion: companionDef, companionSlug } = usePlayerLoadout()
  const storyWorld = getStoryWorld(DEFAULT_STORY_WORLD_SLUG)
  const companion = useMemo(() => companionFromDef(companionDef), [companionDef])
  const companionBattle = useMemo(() => companionBattleFromDef(companionDef), [companionDef])
  const companionPortrait = companionDef.sprites.portrait?.src ?? companionDef.sprites.idle?.src ?? ''
  const companionAvatar = companionDef.sprites.idle?.src ?? companionPortrait
  const showcaseMoves = useMemo<ShowcaseMove[]>(() => {
    const idleSprite = companionDef.sprites.idle
    if (!companion || !companionBattle || !idleSprite) return []
    return [
      { label: 'Idle', sheet: companion.sprites.idle, portrait: idleSprite, oneShot: false },
      { label: 'Run', sheet: companion.sprites.run, portrait: companionDef.sprites.run ?? idleSprite, oneShot: false },
      { label: 'Attack', sheet: companionBattle.attack, portrait: companionDef.sprites.attack ?? idleSprite, oneShot: true },
      { label: 'Hurt', sheet: companionBattle.hurt, portrait: companionDef.sprites.hurt ?? idleSprite, oneShot: true },
    ]
  }, [companion, companionBattle, companionDef])

  // Imperative stage state: swapping sheets and firing effects never re-renders.
  const spriteRef = useRef<SpriteAnimatorHandle | null>(null)
  const fxRef = useRef<HTMLDivElement | null>(null)
  const attackerRef = useRef<HTMLDivElement | null>(null)
  const attackTargetRef = useRef<HTMLDivElement | null>(null)
  const playTokenRef = useRef(0)
  const [activeMove, setActiveMove] = useState('Idle')
  const [profileView, setProfileView] = useState<'profile' | 'rank'>('profile')
  const pedestalBounds = useImagePixelBounds(heroShowcasePedestalImage)
  const pedestalStyle = pedestalBounds
    ? ({
        '--pedestal-anchor-x': `${(pedestalBounds.centerOffsetX / pedestalBounds.naturalWidth) * 100}%`,
        '--pedestal-anchor-y': `${((pedestalBounds.naturalHeight - pedestalBounds.centerY) / pedestalBounds.naturalHeight) * 100}%`,
      } as CSSProperties)
    : undefined
  const homeBackdropStyle = {
    '--home-theme-map': `url("${storyWorld.map?.background.src ?? '/cosmetics/story-worlds/arcane-spire/backgrounds/level-map.png'}")`,
  } as CSSProperties

  function playMove(move: ShowcaseMove) {
    const sprite = spriteRef.current
    if (!sprite || !companion) return
    playTokenRef.current += 1
    const token = playTokenRef.current
    setActiveMove(move.label)
    if (!move.oneShot) {
      sprite.setAnimation(move.sheet)
      return
    }
    // Reduced motion holds frame 0 and never completes; the timeout settles it.
    let settled = false
    const settle = () => {
      if (settled || playTokenRef.current !== token) return
      settled = true
      sprite.setAnimation(companion.sprites.idle)
      setActiveMove('Idle')
    }
    sprite.setAnimation(move.sheet, { onComplete: settle })
    window.setTimeout(settle, animationDuration(move.sheet, 1600))
  }

  /** Layer-local center of a node, for effect launch/impact points. */
  function anchor(node: Element | null, dx = 0, dy = 0) {
    const layer = fxRef.current
    if (!layer || !node) return { x: 0, y: 0 }
    const layerBox = layer.getBoundingClientRect()
    const box = node.getBoundingClientRect()
    return { x: box.left + box.width / 2 - layerBox.left + dx, y: box.top + box.height / 2 - layerBox.top + dy }
  }

  function attackWithSkill(skill: LearnedSkill) {
    setPickedId(skill.id)
    const attackMove = showcaseMoves.find((move) => move.label === 'Attack')
    if (attackMove) playMove(attackMove)

    const layer = fxRef.current
    if (!layer) return

    const attackerBox = attackerRef.current?.getBoundingClientRect()
    const from = anchor(attackerRef.current, attackerBox ? attackerBox.width * 0.2 : 30, attackerBox ? -attackerBox.height * 0.08 : -16)
    const to = anchor(attackTargetRef.current)
    window.setTimeout(() => {
      void effectForSkill(gitCommandFamily(skill.base_command), companionSlug)({ layer, from, to })
    }, 120)
  }

  return (
    <div className="home-ref-screen">
      <div className="home-ref-backdrop" style={homeBackdropStyle} aria-hidden="true" />

      <nav className="home-ref-tabs" aria-label="Home sections">
        <button
          type="button"
          className={tab === 'overview' ? 'is-active' : ''}
          aria-pressed={tab === 'overview'}
          onClick={() => selectTab('overview')}
        >
          <BarChart3 aria-hidden="true" />
          Overview
        </button>
        <button
          type="button"
          className={tab === 'loadout' ? 'is-active' : ''}
          aria-pressed={tab === 'loadout'}
          onClick={() => selectTab('loadout')}
        >
          <Backpack aria-hidden="true" />
          Loadout
        </button>
        <button
          type="button"
          className={tab === 'profile' ? 'is-active' : ''}
          aria-pressed={tab === 'profile'}
          onClick={() => selectTab('profile')}
        >
          <User aria-hidden="true" />
          Profile
        </button>
      </nav>

      {tab === 'overview' ? <HomeStatsView home={home} stats={stats} /> : null}
      {tab === 'loadout' ? <HomeLoadoutView /> : null}

      <section className="home-ref-grid" aria-label="Player profile overview" hidden={tab !== 'profile'}>
        <aside className={`ref-panel home-profile-panel home-profile-panel--${profileView}`}>
          <div className="home-panel-switch" role="tablist" aria-label="Profile or rank ladder">
            <button
              type="button"
              role="tab"
              className={profileView === 'profile' ? 'is-active' : ''}
              aria-selected={profileView === 'profile'}
              onClick={() => setProfileView('profile')}
            >
              <User aria-hidden="true" />
              Profile
            </button>
            <button
              type="button"
              role="tab"
              className={profileView === 'rank' ? 'is-active' : ''}
              aria-selected={profileView === 'rank'}
              onClick={() => setProfileView('rank')}
            >
              <Trophy aria-hidden="true" />
              Rank Ladder
            </button>
          </div>

          {profileView === 'profile' ? (
            <div className="home-profile-view">
              <div className="home-profile-portrait">
                <img src={companionPortrait} alt="" />
              </div>
              <div className="home-profile-rank">
                <RankBadge tier={rank.tier} className="home-rank-badge--profile" />
                <div>
                  <span>Rank {rank.tier.numeral}</span>
                  <small>{rank.tier.name}</small>
                  <div className="ref-meter" aria-label={`${rank.progressPct}% toward the next rank`}>
                    <span style={{ width: `${rank.progressPct}%` }} />
                  </div>
                  <em>{rank.nextTier ? `${formatNumber(rank.ratingInTier)} / ${formatNumber(rank.ratingForNext)} XP` : 'Max rank'}</em>
                </div>
              </div>
              <div className="home-profile-name">
                <strong>{playerName || companionDef.label}</strong>
                <span>{rank.tier.name}</span>
              </div>
              <div className="home-profile-currencies">
                <div>
                  <GitCoinIcon />
                  <strong>{formatNumber(balance)}</strong>
                  <span>GitCoins</span>
                </div>
                <div>
                  <Star className="is-lit" aria-hidden="true" />
                  <strong>{formatNumber(starsCollected)}</strong>
                  <span>Perfect Clears</span>
                </div>
              </div>
              <div className="home-profile-title">
                <RankBadge tier={rank.tier} className="home-rank-badge--title" />
                <span>Current Title</span>
                <strong>{rank.title}</strong>
              </div>
            </div>
          ) : (
            <div className="home-rank-view">
              <div className="home-rank-body">
                <div className="home-rank-list">
                  {[...RANK_TIERS].reverse().map((tier) => {
                    const state =
                      tier.rank === rank.tier.rank ? 'current' : tier.rank < rank.tier.rank ? 'cleared' : 'locked'
                    return (
                      <div className={state === 'current' ? 'is-active' : ''} key={tier.name}>
                        <RankBadge tier={tier} className="home-rank-badge--list" />
                        <span>{tier.name}</span>
                        {state === 'locked' ? <Lock aria-hidden="true" /> : null}
                        {state === 'cleared' ? <Check aria-hidden="true" /> : null}
                      </div>
                    )
                  })}
                </div>
                <div className="home-current-rank">
                  <div className="home-current-rank-crest">
                    <RankBadge tier={rank.tier} className="home-rank-badge--current" />
                  </div>
                  <span>{rank.tier.name}</span>
                  <small>Your Rating</small>
                  <strong>
                    {formatNumber(rank.score)}{' '}
                    <em>/ {formatNumber(rank.nextTier ? rank.nextTier.minScore : rank.score)}</em>
                  </strong>
                  <div className="ref-meter" aria-label={`${rank.progressPct}% toward the next rank`}>
                    <span style={{ width: `${rank.progressPct}%` }} />
                  </div>
                </div>
              </div>
              <div className="home-profile-stats">
                <header>Profile Stats</header>
                <div><span>Levels Cleared</span><strong>{formatNumber(levelsCleared)}</strong></div>
                <div><span>Perfect Clears</span><strong>{formatNumber(starsCollected)}</strong></div>
                <div><span>Day Streak</span><strong>{formatNumber(home.streak.current)}</strong></div>
                <div><span>Commands Run</span><strong>{formatNumber(stats.headline.commands_run)}</strong></div>
              </div>
            </div>
          )}
        </aside>

        <section className="ref-panel home-sprite-panel">
          <header className="ref-panel-head">Sprite Showcase</header>
          <div className="home-sprite-stage">
            <div className="home-sprite-rune" aria-hidden="true" />
            <img className="home-sprite-pedestal" src={heroShowcasePedestalImage} alt="" style={pedestalStyle} />
            <div className="home-sprite-avatar" ref={attackerRef}>
              {companion ? (
                <SpriteAnimator
                  ref={spriteRef}
                  animation={companion.sprites.idle}
                  scale={companion.metrics.scale}
                  anchorToPixelBounds
                  pixelAnchorFallback={{ bottomOffset: companion.metrics.footOffset }}
                  pixelated
                  aria-label={`${companionDef.label} ${activeMove.toLowerCase()} animation`}
                />
              ) : (
                <img src={companionAvatar} alt="" />
              )}
            </div>
            <div className="home-attack-anchor" ref={attackTargetRef} aria-hidden="true" />
            <div className="home-sprite-fx" ref={fxRef} aria-hidden="true" />
          </div>
        </section>

        <section className="ref-panel home-spellbook-panel">
          <header className="ref-panel-head">
            <BookOpen aria-hidden="true" />
            Spellbook
            {!skillsLoading && hasSkills ? <em>{skills!.length} learned · click to attack</em> : null}
          </header>
          {skillsLoading ? (
            <div className="home-spellbook-grid" aria-hidden="true">
              {Array.from({ length: 8 }, (_, index) => (
                <span className="home-spellbook-skeleton" key={index} />
              ))}
            </div>
          ) : !hasSkills ? (
            <p className="home-spellbook-empty">
              Solve an Adventure with a command to inscribe your first spell.
            </p>
          ) : (
            <div className="home-spellbook-grid app-scrollbar">
              {skills!.map((skill) => (
                <button
                  type="button"
                  className={skill.id === selectedId ? 'is-selected' : ''}
                  key={skill.id}
                  title={skill.summary}
                  aria-label={`Attack with ${skill.title} — ${skill.base_command}`}
                  onClick={() => attackWithSkill(skill)}
                >
                  <span className="home-command-icon">
                    <GitCommandIcon command={skill.base_command} />
                  </span>
                  <strong>{skill.base_command}</strong>
                  <small>Chapter {skill.chapter_number}</small>
                </button>
              ))}
            </div>
          )}
        </section>
      </section>

      <div className="home-ref-arrows" aria-hidden="true">
        <ChevronLeft />
        <ChevronRight />
      </div>
    </div>
  )
}
