import { BookOpen } from 'lucide-react'
import { useState } from 'react'

import fieldGuideBookImage from '@/assets/images/book.png'
import { ChapterBookModal } from '@/features/story-map/components/book/ChapterBookModal'
import { GamePanel } from '@/shared/components/GamePanel'

// The Chapter Book lives in the chapter overview; clicking it opens the
// reference modal for this chapter.
export function ChapterBookCard({
  chapterId,
  chapterTitle,
  commandCount,
}: {
  chapterId: number
  chapterTitle: string
  commandCount: number
}) {
  const [open, setOpen] = useState(false)

  return (
    <>
      <GamePanel
        as="button"
        type="button"
        className="chapter-book"
        aria-label={`Open the ${chapterTitle} field guide (${commandCount} commands)`}
        aria-haspopup="dialog"
        onClick={() => setOpen(true)}
      >
        <span className="chapter-book-stage" aria-hidden="true">
          <img className="chapter-book-asset" src={fieldGuideBookImage} alt="" />
        </span>
        <span className="chapter-book-meta">
          <span className="chapter-book-kicker">Field Guide</span>
          <span className="chapter-book-title">Chapter Book</span>
          <span className="chapter-book-sub">
            {commandCount} {commandCount === 1 ? 'command' : 'commands'}
          </span>
          <span className="chapter-book-cta">
            <BookOpen className="size-4" aria-hidden="true" />
            Open Field Guide
          </span>
        </span>
      </GamePanel>

      {open ? <ChapterBookModal chapterId={chapterId} chapterTitle={chapterTitle} onClose={() => setOpen(false)} /> : null}
    </>
  )
}
