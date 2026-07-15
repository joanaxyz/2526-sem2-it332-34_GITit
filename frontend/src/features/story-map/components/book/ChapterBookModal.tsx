import { useQuery } from '@tanstack/react-query'
import { BookOpen, ChevronLeft, ChevronRight, ScrollText } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'

import { storyMapApi } from '@/features/story-map/api/storyMapApi'
import { BookContent, BookPages } from '@/features/story-map/components/book/BookContent'
import { bookAnchorDomId, bookNavAnchors } from '@/features/story-map/components/book/bookNav'
import type { BookCommand, BookLesson, ChapterBook } from '@/features/story-map/components/book/bookTypes'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'
import { EmptyState } from '@/shared/components/EmptyState'
import { GlyphLoadingState } from '@/shared/components/GlyphLoadingState'
import { Modal } from '@/shared/components/Modal'
import { cn } from '@/shared/utils/cn'

export function ChapterBookModal({
  chapterId,
  chapterTitle,
  onClose,
}: {
  chapterId: number
  chapterTitle: string
  onClose: () => void
}) {
  const bookQuery = useQuery({
    queryKey: queryKeys.chapterBook(chapterId),
    queryFn: () => storyMapApi.getChapterBook(chapterId),
    staleTime: 5 * 60 * 1000,
  })

  const title = `${chapterTitle} - Field Guide`

  if (bookQuery.isLoading && !bookQuery.data) {
    return (
      <Modal open title={title} onClose={onClose} contentClassName="p-5">
        <GlyphLoadingState description="Opening the field guide." label="Loading field guide" variant="inline" />
      </Modal>
    )
  }

  if (bookQuery.isError || !bookQuery.data) {
    return (
      <Modal open title={title} onClose={onClose} contentClassName="p-5">
        <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm leading-6 text-destructive">
          {bookQuery.error?.message ?? 'Could not open the chapter book.'}
        </div>
      </Modal>
    )
  }

  return <ChapterBookReader book={bookQuery.data} title={title} onClose={onClose} />
}

type BookNavEntry =
  | {
      kind: 'command'
      key: string
      label: string
      heading: string
      summary: string
      slug: string
      pages: BookCommand['pages']
      command: BookCommand
    }
  | {
      kind: 'lesson'
      key: string
      label: string
      heading: string
      summary: string
      slug: string
      pages: BookLesson['pages']
      lesson: BookLesson
    }

function navEntriesForBook(book: ChapterBook): BookNavEntry[] {
  // Lessons (the conceptual reads) come before the per-command reference:
  // "How Git Thinks" should greet the reader before `git init`.
  return [
    ...book.lessons.map((lesson) => ({
      kind: 'lesson' as const,
      key: `lesson-${lesson.id}`,
      label: lesson.title,
      heading: lesson.title,
      summary: lesson.summary,
      slug: lesson.slug,
      pages: lesson.pages,
      lesson,
    })),
    ...book.commands.map((command) => ({
      kind: 'command' as const,
      key: `command-${command.id}`,
      label: command.base_command,
      heading: command.base_command,
      summary: command.summary,
      slug: command.slug,
      pages: command.pages,
      command,
    })),
  ]
}

function countLabel(count: number, singular: string, plural = `${singular}s`) {
  return `${count} ${count === 1 ? singular : plural}`
}

function railKicker(book: ChapterBook) {
  const labels: string[] = []
  if (book.lesson_count) labels.push(countLabel(book.lesson_count, 'lesson'))
  labels.push(countLabel(book.command_count, 'command'))
  return labels.join(' / ')
}

export function ChapterBookReader({ book, title, onClose }: { book: ChapterBook; title: string; onClose: () => void }) {
  const entries = useMemo(() => navEntriesForBook(book), [book])
  const [requestedActiveIndex, setRequestedActiveIndex] = useState(0)
  // {entryIndex, pageId | 'top', nonce}: the pending scroll target. 'top' is
  // used when switching entries; a page id when jumping to an option/argument.
  const [pendingScroll, setPendingScroll] = useState<{ index: number; pageId: string; nonce: number }>({
    index: 0,
    pageId: 'top',
    nonce: 0,
  })
  const contentRef = useRef<HTMLDivElement | null>(null)
  const scrollPositionsRef = useRef<Record<string, number>>({})
  const activeIndex = Math.min(requestedActiveIndex, Math.max(entries.length - 1, 0))
  const activeEntry = entries[activeIndex] ?? entries[0] ?? null
  const activeAnchors = activeEntry ? bookNavAnchors(activeEntry) : []

  // Resolve the pending scroll once the target entry's content has rendered.
  useEffect(() => {
    if (pendingScroll.index !== activeIndex) return
    const node = contentRef.current
    if (!node) return
    const frame = window.requestAnimationFrame(() => {
      if (pendingScroll.pageId === 'top') {
        const restoredTop = activeEntry ? (scrollPositionsRef.current[activeEntry.key] ?? 0) : 0
        if (typeof node.scrollTo === 'function') node.scrollTo({ top: restoredTop })
        else node.scrollTop = restoredTop
        return
      }
      const target = activeEntry
        ? document.getElementById(bookAnchorDomId(activeEntry.slug, pendingScroll.pageId))
        : null
      target?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
    return () => window.cancelAnimationFrame(frame)
  }, [pendingScroll, activeIndex, activeEntry])

  function select(index: number, pageId: string = 'top') {
    if (index < 0 || index >= entries.length) return
    if (activeEntry && contentRef.current) {
      scrollPositionsRef.current[activeEntry.key] = contentRef.current.scrollTop
    }
    setRequestedActiveIndex(index)
    // Bump the nonce so re-selecting the same target still re-triggers the scroll.
    setPendingScroll((prev) => ({ index, pageId, nonce: prev.nonce + 1 }))
  }

  return (
    <Modal
      open
      title={title}
      onClose={onClose}
      className="book-modal-card"
      contentClassName="book-modal-content"
    >
      <div className="book-modal">
        <aside
          className="book-modal-rail app-scrollbar"
          aria-label="Chapter book navigation"
        >
          <p className="book-modal-rail-kicker">{railKicker(book)}</p>
          <nav className="grid gap-1">
            {entries.map((entry, index) => {
              const isActive = index === activeIndex
              const Icon = entry.kind === 'lesson' ? ScrollText : BookOpen
              return (
                <div key={entry.key}>
                  <button
                    aria-current={isActive ? 'page' : undefined}
                    className={cn('book-modal-rail-item', isActive && 'is-active')}
                    type="button"
                    onClick={() => select(index)}
                  >
                    <Icon className="size-3.5 shrink-0 opacity-70" />
                    <span className={cn('truncate', entry.kind === 'command' && 'font-mono')}>{entry.label}</span>
                  </button>
                  {isActive && activeAnchors.length ? (
                    <ul className="book-modal-rail-anchors">
                      {activeAnchors.map((anchor) => (
                        <li key={anchor.pageId}>
                          <button
                            className={cn('book-modal-rail-anchor', `is-${anchor.kind}`)}
                            type="button"
                            onClick={() => select(index, anchor.pageId)}
                          >
                            <span className="truncate font-mono">{anchor.label}</span>
                          </button>
                        </li>
                      ))}
                    </ul>
                  ) : null}
                </div>
              )
            })}
          </nav>
        </aside>

        <main className="book-modal-main">
          <header className="book-modal-head">
            <div className="min-w-0">
              <p className="font-mono text-xs font-semibold text-primary">
                {activeEntry?.kind === 'lesson' ? 'Lesson' : 'Command'}
              </p>
              <h3
                className={cn(
                  'book-modal-title mt-1 truncate font-extrabold leading-tight',
                  activeEntry?.kind === 'command' && 'font-mono',
                )}
              >
                {activeEntry ? activeEntry.heading : '-'}
              </h3>
              {activeEntry?.summary ? (
                <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">{activeEntry.summary}</p>
              ) : null}
              <label className="book-modal-mobile-select">
                <span>Book section</span>
                <select value={activeIndex} onChange={(event) => select(Number(event.target.value))}>
                  {entries.map((entry, index) => (
                    <option key={entry.key} value={index}>{entry.label}</option>
                  ))}
                </select>
              </label>
            </div>
          </header>

          <section
            className="book-modal-body app-scrollbar"
            ref={contentRef}
            onScroll={(event) => {
              if (activeEntry) scrollPositionsRef.current[activeEntry.key] = event.currentTarget.scrollTop
            }}
          >
            {activeEntry ? (
              activeEntry.kind === 'command' ? (
                <BookContent command={activeEntry.command} />
              ) : (
                <BookPages anchorScope={activeEntry.slug} pages={activeEntry.lesson.pages} />
              )
            ) : (
              <EmptyState
                title="No book entries yet"
                description="This chapter has no lessons or commands registered in the book."
              />
            )}
          </section>

          {entries.length > 1 ? (
            <footer className="book-modal-foot">
              <Button
                aria-label="Previous book entry"
                disabled={activeIndex <= 0}
                size="sm"
                type="button"
                variant="ghost"
                onClick={() => select(activeIndex - 1)}
              >
                <ChevronLeft data-icon="inline-start" />
                Prev
              </Button>
              <span className="font-mono text-xs text-muted-foreground">
                {activeIndex + 1} / {entries.length}
              </span>
              <Button
                aria-label="Next book entry"
                disabled={activeIndex >= entries.length - 1}
                size="sm"
                type="button"
                variant="ghost"
                onClick={() => select(activeIndex + 1)}
              >
                Next
                <ChevronRight data-icon="inline-end" />
              </Button>
            </footer>
          ) : null}
        </main>
      </div>
    </Modal>
  )
}
