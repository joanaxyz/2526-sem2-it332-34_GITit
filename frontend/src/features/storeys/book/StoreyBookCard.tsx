import { useState } from 'react'

import { StoreyBookModal } from '@/features/storeys/book/StoreyBookModal'

// The Storey Book lives in the storey overview. It's a 3D neon book whose pages
// riffle on hover (CSS); clicking it opens the reference modal for this storey.
export function StoreyBookCard({
  storeyId,
  storeyTitle,
  commandCount,
}: {
  storeyId: number
  storeyTitle: string
  commandCount: number
}) {
  const [open, setOpen] = useState(false)

  return (
    <>
      <button
        type="button"
        className="storey-book"
        aria-label={`Open the ${storeyTitle} field guide (${commandCount} commands)`}
        aria-haspopup="dialog"
        onClick={() => setOpen(true)}
      >
        <span className="storey-book-stage" aria-hidden="true">
          <span className="storey-book-3d">
            <span className="storey-book-back" />
            <span className="storey-book-leaves">
              <span className="storey-book-leaf" />
              <span className="storey-book-leaf" />
              <span className="storey-book-leaf" />
              <span className="storey-book-leaf" />
            </span>
            <span className="storey-book-cover">
              <svg className="storey-book-emblem" viewBox="0 0 48 48" aria-hidden="true">
                {/* a tiny commit graph: the field guide's mark */}
                <path
                  d="M16 12 V36 M16 18 C16 24 32 22 32 28 V36 M16 12 L16 12"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.4"
                  strokeLinecap="round"
                />
                <circle cx="16" cy="12" r="4.2" fill="none" stroke="currentColor" strokeWidth="2.4" />
                <circle cx="16" cy="36" r="4.2" fill="none" stroke="currentColor" strokeWidth="2.4" />
                <circle cx="32" cy="36" r="4.2" fill="none" stroke="currentColor" strokeWidth="2.4" />
              </svg>
            </span>
            <span className="storey-book-spine" />
          </span>
        </span>
        <span className="storey-book-meta">
          <span className="storey-book-kicker">Field Guide</span>
          <span className="storey-book-title">Storey Book</span>
          <span className="storey-book-sub">
            {commandCount} {commandCount === 1 ? 'command' : 'commands'}
          </span>
        </span>
      </button>

      {open ? <StoreyBookModal storeyId={storeyId} storeyTitle={storeyTitle} onClose={() => setOpen(false)} /> : null}
    </>
  )
}
