import { BookOpen, Lock } from 'lucide-react'

import type { LearningChapter } from '@/features/story-map/types'
import { GamePanel } from '@/shared/components/GamePanel'
import { chapterTitle } from '@/features/story-map/utils/storyMapChapter'

export function StoryChapterList({
  chapters,
  activeChapterId,
  onSelectChapter,
}: {
  chapters: LearningChapter[]
  activeChapterId: number
  onSelectChapter: (chapterId: number) => void
}) {
  return (
    <GamePanel as="section" eyebrow="Chapters" className="story-chapter-list-panel">
      <div className="story-chapter-list">
        {chapters.map((chapter) => {
          const active = chapter.id === activeChapterId
          return (
            <button
              type="button"
              className="story-chapter-row"
              data-active={active}
              key={chapter.id}
              disabled={chapter.locked}
              onClick={() => onSelectChapter(chapter.id)}
            >
              <span className="story-chapter-row-number">{String(chapter.number).padStart(2, '0')}</span>
              <span className="story-chapter-row-title">{chapterTitle(chapter)}</span>
              {chapter.locked ? <Lock className="size-4" aria-hidden="true" /> : <BookOpen className="size-5" aria-hidden="true" />}
            </button>
          )
        })}
      </div>
    </GamePanel>
  )
}
