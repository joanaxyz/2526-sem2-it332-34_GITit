import { Check, Info } from 'lucide-react'

import chapterBadgeImage from '@/assets/images/chapter_badge.png'
import rewardChestActiveImage from '@/assets/images/chest_active.png'
import rewardChestNormalImage from '@/assets/images/chest_normal.png'
import { ChapterBookCard } from '@/features/story-map/components/book/ChapterBookCard'
import type { LearningChapter } from '@/features/story-map/types'
import { GamePanel } from '@/shared/components/GamePanel'
import { ProgressBar } from '@/shared/components/ProgressBar'

export function ChapterOverview({ chapter }: { chapter: LearningChapter }) {
  const title = chapter.title
  const progress = chapter.level_completion?.value ?? 0
  const levels = chapter.level_completion?.denominator ?? chapter.adventure_level_count + chapter.challenge_count * 3
  const cleared = chapter.level_completion?.numerator ?? 0
  const chests = [...chapter.chest_schedule].sort((a, b) => a.threshold - b.threshold)

  return (
    <aside className="chapter-overview">
      <GamePanel
        as="section"
        eyebrow="Chapter Overview"
        title={
          <>
            <span className="story-chapter-number">Chapter {String(chapter.number).padStart(2, '0')}</span>
            {title}
          </>
        }
        action={
          <span className="story-overview-badge" aria-hidden="true">
            <img src={chapterBadgeImage} alt="" />
          </span>
        }
        aria-label={`${title} chapter overview`}
      >
        <div className="story-overview-mastery">
          <div className="story-overview-progress-row">
            <span>Mastery</span>
            <strong>{Math.round(progress)}%</strong>
          </div>
          <ProgressBar value={progress} className="story-overview-progress" glow fillAnimate />
        </div>

        <dl className="story-overview-stats">
          <div>
            {/* level_completion counts adventure levels AND challenge trials;
                calling it "Levels" contradicts the level-only path beside it. */}
            <dt>Levels & Trials</dt>
            <dd>
              {cleared} / {levels}
            </dd>
          </div>
          <div>
            <dt>Command Skills</dt>
            <dd>{chapter.command_skill_count}</dd>
          </div>
        </dl>
      </GamePanel>

      <GamePanel
        as="section"
        eyebrow={
          <span className="story-panel-title-with-action">
            Progress Reward
            <Info className="size-3.5" aria-hidden="true" />
          </span>
        }
        className="story-skill-reward-panel"
      >
        <div className="story-skill-reward-grid" aria-label={`${title} progress rewards`}>
          {chests.map((chest) => {
            const earned = progress >= chest.threshold
            return (
              <div className="story-skill-reward" data-earned={earned} key={chest.threshold}>
                <span className="story-reward-chest" aria-hidden="true">
                  <img src={earned ? rewardChestActiveImage : rewardChestNormalImage} alt="" />
                </span>
                <span className="story-skill-threshold">
                  {earned ? <Check aria-hidden="true" /> : null}
                  {chest.threshold}%
                </span>
                <span className="story-skill-reward-amount">
                  {chest.coins > 0 ? `+${chest.coins} GitCoins` : null}
                </span>
              </div>
            )
          })}
        </div>
      </GamePanel>

      <ChapterBookCard chapterId={chapter.id} chapterTitle={title} commandCount={chapter.command_skill_count} />
    </aside>
  )
}
