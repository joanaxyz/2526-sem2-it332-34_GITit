import chapterBadgeImage from '@/assets/images/chapter_badge.png'
import { ChapterBookCard } from '@/features/story-map/components/book/ChapterBookCard'
import { ChapterProgressRewards } from '@/features/story-map/components/ChapterProgressRewards'
import type { LearningChapter } from '@/features/story-map/types'
import { GamePanel } from '@/shared/components/GamePanel'
import { ProgressBar } from '@/shared/components/ProgressBar'

export function ChapterOverview({ chapter, preview = false }: { chapter: LearningChapter; preview?: boolean }) {
  const title = chapter.title
  const progress = chapter.level_completion?.value ?? 0
  const levels = chapter.level_completion?.denominator ?? chapter.adventure_level_count + chapter.challenge_count * 3
  const cleared = chapter.level_completion?.numerator ?? 0

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

      <ChapterProgressRewards key={chapter.id} chapter={chapter} preview={preview} />

      <ChapterBookCard chapterId={chapter.id} chapterTitle={title} commandCount={chapter.command_skill_count} />
    </aside>
  )
}
