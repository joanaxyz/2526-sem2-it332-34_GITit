import { useQuery } from '@tanstack/react-query'
import { BookOpen, ChevronLeft, ChevronRight } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

import { towerMapApi } from '@/features/tower-map/api/towerMapApi'
import { BookContent } from '@/features/tower-map/book/BookContent'
import { bookAnchorDomId, bookNavAnchors } from '@/features/tower-map/book/bookNav'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'
import { EmptyState } from '@/shared/components/EmptyState'
import { GlyphLoadingState } from '@/shared/components/GlyphLoadingState'
import { Modal } from '@/shared/components/Modal'
import { cn } from '@/shared/utils/cn'

export function StoreyBookModal({
  storeyId,
  storeyTitle,
  onClose,
}: {
  storeyId: number
  storeyTitle: string
  onClose: () => void
}) {
  const bookQuery = useQuery({
  queryKey: queryKeys.storeyBook(storeyId),
  queryFn: async () => {
    await new Promise((resolve) => window.setTimeout(resolve, 1600))
    return towerMapApi.getStoreyBook(storeyId)
  },
  staleTime: 0,
  gcTime: 0,
})

  const title = `${storeyTitle} - Field Guide`

  if (bookQuery.isLoading && !bookQuery.data) {
    return (
      <Modal open title={title} onClose={onClose} className="w-full max-w-xl" contentClassName="p-5">
        <GlyphLoadingState description="Opening the field guide." label="Loading field guide" variant="inline" />
      </Modal>
    )
  }

  if (bookQuery.isError || !bookQuery.data) {
    return (
      <Modal open title={title} onClose={onClose} className="w-full max-w-xl" contentClassName="p-5">
        <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm leading-6 text-destructive">
          {bookQuery.error?.message ?? 'Could not open the storey book.'}
        </div>
      </Modal>
    )
  }

  return <StoreyBookReader book={bookQuery.data} title={title} onClose={onClose} />
}

function StoreyBookReader({
  book,
  title,
  onClose,
}: {
  book: import('@/features/tower-map/book/bookTypes').StoreyBook
  title: string
  onClose: () => void
}) {
  const commands = book.commands
  const [activeIndex, setActiveIndex] = useState(0)
  // {commandIndex, pageId | 'top', nonce}: the pending scroll target. 'top' is
  // used when switching commands; a page id when jumping to an option/argument.
  const [pendingScroll, setPendingScroll] = useState<{ index: number; pageId: string; nonce: number }>({
    index: 0,
    pageId: 'top',
    nonce: 0,
  })
  const contentRef = useRef<HTMLDivElement | null>(null)
  const activeCommand = commands[activeIndex] ?? commands[0] ?? null
  const activeAnchors = activeCommand ? bookNavAnchors(activeCommand) : []

  // Resolve the pending scroll once the target command's content has rendered.
  useEffect(() => {
    if (pendingScroll.index !== activeIndex) return
    const node = contentRef.current
    if (!node) return
    const frame = window.requestAnimationFrame(() => {
      if (pendingScroll.pageId === 'top') {
        if (typeof node.scrollTo === 'function') node.scrollTo({ top: 0 })
        else node.scrollTop = 0
        return
      }
      const target = activeCommand
        ? document.getElementById(bookAnchorDomId(activeCommand.slug, pendingScroll.pageId))
        : null
      target?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
    return () => window.cancelAnimationFrame(frame)
  }, [pendingScroll, activeIndex, activeCommand])

  function select(index: number, pageId: string = 'top') {
    if (index < 0 || index >= commands.length) return
    setActiveIndex(index)
    // Bump the nonce so re-selecting the same target still re-triggers the scroll.
    setPendingScroll((prev) => ({ index, pageId, nonce: prev.nonce + 1 }))
  }

  return (
    <Modal
      open
      title={title}
      onClose={onClose}
      className="max-h-[94vh] w-full max-w-5xl overflow-hidden"
      contentClassName="h-[calc(94vh-4.5rem)] overflow-hidden p-0"
    >
      <div className="book-modal grid h-full min-h-0 grid-cols-[16rem_minmax(0,1fr)] overflow-hidden max-md:grid-cols-1">
        <aside className="book-modal-rail min-h-0 overflow-y-auto app-scrollbar max-md:hidden" aria-label="Commands in this storey">
          <p className="book-modal-rail-kicker">{book.command_count} commands</p>
          <nav className="grid gap-1">
            {commands.map((command, index) => {
              const isActive = index === activeIndex
              return (
                <div key={command.id}>
                  <button
                    aria-current={isActive ? 'page' : undefined}
                    className={cn('book-modal-rail-item', isActive && 'is-active')}
                    type="button"
                    onClick={() => select(index)}
                  >
                    <BookOpen className="size-3.5 shrink-0 opacity-70" />
                    <span className="truncate font-mono">{command.base_command}</span>
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

        <main className="grid min-h-0 grid-rows-[auto_minmax(0,1fr)_auto] overflow-hidden">
          <header className="book-modal-head">
            <div className="min-w-0">
              <p className="font-mono text-xs font-semibold text-primary">Command</p>
              <h3 className="mt-1 truncate font-mono text-xl font-extrabold leading-tight">
                {activeCommand ? activeCommand.base_command : '-'}
              </h3>
              {activeCommand?.summary ? (
                <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">{activeCommand.summary}</p>
              ) : null}
            </div>
          </header>

          <section className="min-h-0 overflow-auto p-5 app-scrollbar" ref={contentRef}>
            {activeCommand ? (
              <BookContent command={activeCommand} />
            ) : (
              <EmptyState title="No commands yet" description="This storey has no commands registered in the book." />
            )}
          </section>

          {commands.length > 1 ? (
            <footer className="book-modal-foot">
              <Button
                aria-label="Previous command"
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
                {activeIndex + 1} / {commands.length}
              </span>
              <Button
                aria-label="Next command"
                disabled={activeIndex >= commands.length - 1}
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
