import { ChevronDown, Lock } from 'lucide-react'
import { type CSSProperties, useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { Link } from 'react-router-dom'

import type { LearningChapter } from '@/features/story-map/types'
import { chapterTitle } from '@/features/story-map/utils/storyMapChapter'
import { GamePanel } from '@/shared/components/GamePanel'
import { STORIES_ROUTE } from '@/shared/navigation/routes'

export function StoryChapterList({
  chapters,
  activeChapterId,
  onSelectChapter,
}: {
  chapters: LearningChapter[]
  activeChapterId: number
  onSelectChapter: (chapterId: number) => void
}) {
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)
  const menuRef = useRef<HTMLDivElement>(null)
  const [menuPosition, setMenuPosition] = useState<CSSProperties | null>(null)
  const menuId = useId()
  const activeChapter = chapters.find((chapter) => chapter.id === activeChapterId) ?? chapters[0]

  const positionMenu = useCallback(() => {
    const trigger = triggerRef.current
    if (!trigger) return

    const viewportPadding = 16
    const menuGap = 8
    const triggerRect = trigger.getBoundingClientRect()
    const mobile = typeof window.matchMedia === 'function'
      && window.matchMedia('(max-width: 560px)').matches
    const width = mobile
      ? window.innerWidth - viewportPadding * 2
      : Math.min(336, window.innerWidth - viewportPadding * 2)
    const left = mobile
      ? viewportPadding
      : Math.min(
          Math.max(viewportPadding, triggerRect.right - width),
          window.innerWidth - viewportPadding - width,
        )
    const roomBelow = window.innerHeight - triggerRect.bottom - menuGap - viewportPadding
    const roomAbove = triggerRect.top - menuGap - viewportPadding
    const opensAbove = roomBelow < 280 && roomAbove > roomBelow
    const maxHeight = Math.max(176, Math.min(480, opensAbove ? roomAbove : roomBelow))

    setMenuPosition({
      bottom: opensAbove ? window.innerHeight - triggerRect.top + menuGap : 'auto',
      left,
      maxHeight,
      top: opensAbove ? 'auto' : triggerRect.bottom + menuGap,
      width,
    })
  }, [])

  useLayoutEffect(() => {
    if (!open) return
    positionMenu()
  }, [open, positionMenu])

  useEffect(() => {
    if (!open) return

    function closeOnOutsidePointer(event: PointerEvent) {
      const target = event.target as Node
      if (rootRef.current?.contains(target) || menuRef.current?.contains(target)) return
      setOpen(false)
    }

    function closeOnEscape(event: KeyboardEvent) {
      if (event.key !== 'Escape') return
      setOpen(false)
      rootRef.current?.querySelector<HTMLButtonElement>('.story-chapter-picker-trigger')?.focus()
    }

    document.addEventListener('pointerdown', closeOnOutsidePointer)
    document.addEventListener('keydown', closeOnEscape)
    document.addEventListener('scroll', positionMenu, true)
    window.addEventListener('resize', positionMenu)
    return () => {
      document.removeEventListener('pointerdown', closeOnOutsidePointer)
      document.removeEventListener('keydown', closeOnEscape)
      document.removeEventListener('scroll', positionMenu, true)
      window.removeEventListener('resize', positionMenu)
    }
  }, [open, positionMenu])

  function selectChapter(chapterId: number) {
    onSelectChapter(chapterId)
    setOpen(false)
  }

  if (!activeChapter) return null

  const renderOption = (chapter: LearningChapter) => {
    const active = chapter.id === activeChapterId
    return (
      <button
        type="button"
        className="story-chapter-picker-option"
        data-active={active}
        aria-label={`${String(chapter.number).padStart(2, '0')} ${chapterTitle(chapter)}`}
        aria-current={active ? 'page' : undefined}
        key={chapter.id}
        disabled={chapter.locked}
        title={chapter.locked ? chapter.lock_reason : undefined}
        onClick={() => selectChapter(chapter.id)}
      >
        <span className="story-chapter-diamond" aria-hidden="true" />
        <span className="story-chapter-picker-number">{String(chapter.number).padStart(2, '0')}</span>
        <span className="story-chapter-picker-title">{chapterTitle(chapter)}</span>
        {chapter.locked ? <Lock aria-hidden="true" /> : null}
      </button>
    )
  }

  return (
    <GamePanel as="section" eyebrow="Chapters" className="story-chapter-list-panel">
      <div className="story-chapter-picker" ref={rootRef}>
        <button
          ref={triggerRef}
          type="button"
          className="story-chapter-picker-trigger"
          aria-label={`Choose chapter, current ${String(activeChapter.number).padStart(2, '0')} ${chapterTitle(activeChapter)}`}
          aria-expanded={open}
          aria-controls={menuId}
          onClick={() => setOpen((current) => !current)}
        >
          <span className="story-chapter-diamond" aria-hidden="true" />
          <span className="story-chapter-picker-trigger-copy">
            <small>Chapter</small>
            <strong>
              {String(activeChapter.number).padStart(2, '0')} {chapterTitle(activeChapter)}
            </strong>
          </span>
          <ChevronDown aria-hidden="true" />
        </button>
      </div>
      <Link className="story-chapter-all-stories" to={STORIES_ROUTE}>All stories</Link>
      {open && menuPosition ? createPortal(
        <div
          ref={menuRef}
          id={menuId}
          className="story-chapter-picker-menu"
          style={menuPosition}
          role="group"
          aria-label="Chapters"
        >
          {chapters.map(renderOption)}
        </div>,
        document.body,
      ) : null}
    </GamePanel>
  )
}
