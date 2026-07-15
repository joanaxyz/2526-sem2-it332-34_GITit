import {
  BookOpen,
  Check,
  Lock,
  Play,
  Swords,
} from 'lucide-react'

import easyIconImage from '@/assets/images/easy_icon.png'
import hardIconImage from '@/assets/images/hard_icon.png'
import mediumIconImage from '@/assets/images/medium_icon.png'
import { ChapterOverview } from '@/features/story-map/components/ChapterOverview'
import { pathDataFor, pathGeometry, trialFlyoutPlacement } from '@/features/story-map/utils/pathGeometry'
import { GamePanel } from '@/shared/components/GamePanel'
import type { LearningChapter } from '@/features/story-map/types'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'
import { AppTopbar } from '@/shared/navigation/AppNavigation'
import { StarRating } from '@/shared/level/components/StarRating'
import { GitCommandIcon } from '@/shared/git/commandCatalog/commandIcons'
import { DEFAULT_STORY_WORLD_SLUG, getStoryWorld } from '@/shared/story-worlds/registry'

// Fixed, runtime-computed schedule - mirrors progress.chests.CHEST_SCHEDULE.
const PREVIEW_CHEST_SCHEDULE = [
  { threshold: 25, coins: 25 },
  { threshold: 50, coins: 60 },
  { threshold: 75, coins: 100 },
  { threshold: 100, coins: 150 },
]

const PREVIEW_CHAPTERS: LearningChapter[] = [
  {
    id: 1,
    slug: 'creating-inspecting-repositories',
    number: 1,
    title: 'Foundations',
    description: 'Practice the first Git commands in the Arcane Spire.',
    sort_order: 1,
    is_playable: true,
    story: { id: 1, slug: 'arcane-spire', title: 'Arcane Spire', world_slug: 'arcane-spire' },
    locked: false,
    lock_reason: '',
    command_skill_count: 4,
    challenge_count: 1,
    adventure_level_count: 6,
    level_completion: { value: 64, numerator: 4, denominator: 6 },
    chest_schedule: PREVIEW_CHEST_SCHEDULE,
  },
  {
    id: 2,
    slug: 'branching',
    number: 2,
    title: 'Branching',
    description: '',
    sort_order: 2,
    is_playable: true,
    story: { id: 1, slug: 'arcane-spire', title: 'Arcane Spire', world_slug: 'arcane-spire' },
    locked: true,
    lock_reason: 'Clear Chapter 01.',
    command_skill_count: 3,
    challenge_count: 1,
    adventure_level_count: 6,
    level_completion: { value: 0, numerator: 0, denominator: 6 },
    chest_schedule: PREVIEW_CHEST_SCHEDULE,
  },
  {
    id: 3,
    slug: 'merging',
    number: 3,
    title: 'Merging',
    description: '',
    sort_order: 3,
    is_playable: true,
    story: { id: 1, slug: 'arcane-spire', title: 'Arcane Spire', world_slug: 'arcane-spire' },
    locked: true,
    lock_reason: 'Clear Chapter 02.',
    command_skill_count: 3,
    challenge_count: 1,
    adventure_level_count: 6,
    level_completion: { value: 0, numerator: 0, denominator: 6 },
    chest_schedule: PREVIEW_CHEST_SCHEDULE,
  },
]
const trialIcons = [easyIconImage, mediumIconImage, hardIconImage]

const PREVIEW_NEXT_SKILL = { command: 'git add', level: 3, title: 'Stage and Commit' }

// Static pose of the live map: 6 levels + the trials node, flyout open.
const PREVIEW_PATH_WIDTH = 640
const previewPath = pathGeometry(7, PREVIEW_PATH_WIDTH)
const previewRouteData = pathDataFor(previewPath.points)
const previewTrialPoint = previewPath.points[previewPath.points.length - 1]
const previewFlyout = trialFlyoutPlacement(previewTrialPoint, PREVIEW_PATH_WIDTH, previewPath.height)

export function Component() {
  const activeChapter = PREVIEW_CHAPTERS[0]
  const { companion } = usePlayerLoadout()
  const storyWorld = getStoryWorld(DEFAULT_STORY_WORLD_SLUG)
  const companionPortrait = companion.sprites.portrait?.src ?? companion.sprites.idle?.src ?? ''
  const storyMapStyle = {
    backgroundImage: `url("${storyWorld.map?.background.src ?? '/cosmetics/story-worlds/arcane-spire/backgrounds/level-map.png'}")`,
  } as React.CSSProperties

  return (
    <div className="app-shell">
      <AppTopbar />
      <main className="app-main app-main--story-map">
        <div className="story-page-shell">
          <div className="story-map-backdrop" style={storyMapStyle} aria-hidden="true" />
          <div className="story-map-layout">
            <aside className="story-map-left" aria-label="Chapter tools">
              <ChapterOverview chapter={activeChapter} />
            </aside>

            <section className="story-map-stage" aria-label="Preview story map">
              <div className="story-adventure-path">
                <div className="story-path-canvas" style={{ width: PREVIEW_PATH_WIDTH, height: previewPath.height }}>
                  <svg
                    className="story-route-line"
                    viewBox={`0 0 ${PREVIEW_PATH_WIDTH} ${previewPath.height}`}
                    width={PREVIEW_PATH_WIDTH}
                    height={previewPath.height}
                    aria-hidden="true"
                    focusable="false"
                  >
                    <path d={previewRouteData} />
                    {previewFlyout.connectors.map((d) => (
                      <path className="story-route-branch" d={d} key={d} />
                    ))}
                  </svg>
                  {[1, 2, 3, 4, 5, 6].map((level, index) => (
                    <button
                      type="button"
                      className="story-path-node"
                      data-state={level < 5 ? 'cleared' : level === 6 ? 'current' : 'ready'}
                      key={level}
                      style={
                        {
                          '--node-x': `${previewPath.points[index].x}px`,
                          '--node-y': `${previewPath.points[index].y}px`,
                        } as React.CSSProperties
                      }
                    >
                      <span className="story-path-node-ring">
                        <span>{level}</span>
                      </span>
                      {level < 5 ? (
                        <span className="story-path-node-badge" aria-hidden="true">
                          <Check className="size-3.5" strokeWidth={3} />
                        </span>
                      ) : null}
                      {level === 6 ? (
                        <span className="story-path-node-play" aria-hidden="true">
                          <Play className="size-4" fill="currentColor" />
                        </span>
                      ) : null}
                      <StarRating stars={level < 5 ? 3 : 0} size="sm" className="story-path-stars" label={`Level ${level}`} />
                    </button>
                  ))}
                  <button
                    type="button"
                    className="story-path-node story-path-node--trial"
                    data-state="ready"
                    data-open="true"
                    style={
                      {
                        '--node-x': `${previewTrialPoint.x}px`,
                        '--node-y': `${previewTrialPoint.y}px`,
                      } as React.CSSProperties
                    }
                    aria-expanded="true"
                    aria-label="Challenge trials"
                  >
                    <span className="story-path-node-ring">
                      <Swords className="size-6" aria-hidden="true" />
                    </span>
                  </button>
                  <div
                    className="story-trials-flyout"
                    style={{ left: previewFlyout.left, top: previewFlyout.top }}
                    role="group"
                    aria-label="Challenge trials"
                  >
                    {['Easy', 'Medium', 'Hard'].map((difficulty, index) => (
                      <button
                        type="button"
                        className="story-trial-card"
                        data-status={index < 2 ? 'completed' : 'locked'}
                        key={difficulty}
                        style={{ '--trial-rgb': index === 0 ? 'var(--theme-primary-rgb)' : index === 1 ? 'var(--theme-rail-rgb)' : 'var(--theme-challenge-rgb)' } as React.CSSProperties}
                      >
                        <span className="story-trial-medallion">
                          <img src={trialIcons[index]} alt="" />
                          {index < 2 ? null : <Lock className="story-trial-lock" aria-hidden="true" />}
                        </span>
                        <span className="story-trial-copy">
                          <strong>{difficulty}</strong>
                          <StarRating stars={index < 2 ? 2 : 0} size="sm" label={`${difficulty} stars`} />
                          <span>{index < 2 ? 'Cleared' : 'Locked'}</span>
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </section>

        <aside className="story-map-right" aria-label="Story chapters and companion">
          <GamePanel as="section" eyebrow="Chapters" className="story-chapter-list-panel">
            <div className="story-chapter-list">
              {PREVIEW_CHAPTERS.map((chapter) => (
                <button
                  type="button"
                  className="story-chapter-row"
                  data-active={chapter.id === activeChapter.id}
                  disabled={chapter.locked}
                  key={chapter.id}
                >
                  <span className="story-chapter-row-number">{String(chapter.number).padStart(2, '0')}</span>
                  <span className="story-chapter-row-title">{chapter.title}</span>
                  {chapter.locked ? <Lock className="size-4" /> : <BookOpen className="size-5" />}
                </button>
              ))}
            </div>
          </GamePanel>

          <GamePanel as="section" eyebrow="Skill Reward" className="story-skill-reward-detail-panel">
            <div className="story-skill-reward">
              <span className="story-skill-portrait" aria-hidden="true">
                <GitCommandIcon command={PREVIEW_NEXT_SKILL.command} className="story-skill-portrait-glyph" />
              </span>
              <div className="story-skill-reward-copy">
                <code className="story-skill-reward-name">{PREVIEW_NEXT_SKILL.command}</code>
                <span className="story-skill-reward-level">Level {PREVIEW_NEXT_SKILL.level} Skill Reward</span>
                <p className="story-skill-reward-desc">
                  Clear <strong>{PREVIEW_NEXT_SKILL.title}</strong> to inscribe {companion.label}'s{' '}
                  <code>{PREVIEW_NEXT_SKILL.command}</code> spell.
                </p>
              </div>
            </div>
          </GamePanel>

          <GamePanel as="section" eyebrow={companion.label} title="Your Companion" className="story-companion-panel">
            <div className="story-companion-body">
              <div className="story-companion-copy">
                <dl>
                  <div>
                    <dt>Rank</dt>
                    <dd>IV</dd>
                  </div>
                  <div>
                    <dt>Next Rank</dt>
                    <dd>320 / 500 XP</dd>
                  </div>
                </dl>
              </div>
            </div>
            <img className="story-companion-portrait" src={companionPortrait} alt="" />
          </GamePanel>
        </aside>
          </div>
        </div>
      </main>
    </div>
  )
}
