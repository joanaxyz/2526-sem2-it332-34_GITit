import type { TomeSummary } from '@/features/challenges/types'
import { BookPages } from '@/features/tower-map/book/BookContent'
import { Modal } from '@/shared/components/Modal'

// Reader for a tome (general lesson). Tomes are a single authored document of
// BookPage[] - no command rail, no sub-navigation, no prev/next. Pages ship
// inline on the tome summary, so the reader renders synchronously.
export function TomeReaderModal({ tome, onClose }: { tome: TomeSummary; onClose: () => void }) {
  return (
    <Modal
      open
      title={`${tome.title} - Tome`}
      onClose={onClose}
      className="max-h-[94vh] w-full max-w-3xl overflow-hidden"
      contentClassName="h-[calc(94vh-4.5rem)] overflow-hidden p-0"
    >
      <div className="grid h-full min-h-0 grid-rows-[auto_minmax(0,1fr)] overflow-hidden">
        <header className="book-modal-head">
          <div className="min-w-0">
            <p className="font-mono text-xs font-semibold text-primary">Tome</p>
            <h3 className="mt-1 truncate text-xl font-extrabold leading-tight">{tome.title}</h3>
            {tome.summary ? (
              <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">{tome.summary}</p>
            ) : null}
          </div>
        </header>
        <section className="min-h-0 overflow-auto p-5 app-scrollbar">
          <BookPages anchorScope={tome.slug} pages={tome.pages} />
        </section>
      </div>
    </Modal>
  )
}
