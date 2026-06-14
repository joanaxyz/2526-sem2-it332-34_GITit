import { Plus, Trash2 } from 'lucide-react'

import { BLOCK_TYPES, emptyPage, type BookBlock, type BookPage } from '@/features/authoring/authoringModel'

/** Structured page/block editor for a tome (replaces raw JSON). */
export function TomePagesEditor({
  pages,
  onChange,
}: {
  pages: BookPage[]
  onChange: (pages: BookPage[]) => void
}) {
  function patchPage(index: number, next: Partial<BookPage>) {
    onChange(pages.map((page, i) => (i === index ? { ...page, ...next } : page)))
  }
  function patchBlock(pageIndex: number, blockIndex: number, next: Partial<BookBlock>) {
    const page = pages[pageIndex]
    const blocks = page.blocks.map((block, i) => (i === blockIndex ? { ...block, ...next } : block))
    patchPage(pageIndex, { blocks })
  }

  return (
    <section className="author-card">
      <header className="author-card-head">
        <h2 className="author-card-title">Pages</h2>
        <p className="author-card-sub">A tome is pure reading — no runs or battles.</p>
      </header>

      {pages.map((page, pageIndex) => (
        <div className="author-level" key={pageIndex}>
          <div className="author-level-head">
            <input
              className="author-input"
              value={page.title}
              onChange={(e) => patchPage(pageIndex, { title: e.target.value })}
              placeholder="Page title"
            />
            {pages.length > 1 ? (
              <button
                type="button"
                className="author-icon-btn"
                onClick={() => onChange(pages.filter((_, i) => i !== pageIndex))}
                aria-label="Remove page"
              >
                <Trash2 className="size-4" aria-hidden="true" />
              </button>
            ) : null}
          </div>

          {page.blocks.map((block, blockIndex) => (
            <div className="author-block" key={blockIndex}>
              <div className="author-inline-row">
                <select
                  className="author-input author-input--narrow"
                  value={block.type}
                  onChange={(e) => patchBlock(pageIndex, blockIndex, { type: e.target.value })}
                >
                  {BLOCK_TYPES.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.label}
                    </option>
                  ))}
                </select>
                {page.blocks.length > 1 ? (
                  <button
                    type="button"
                    className="author-icon-btn"
                    onClick={() => patchPage(pageIndex, { blocks: page.blocks.filter((_, i) => i !== blockIndex) })}
                    aria-label="Remove block"
                  >
                    <Trash2 className="size-4" aria-hidden="true" />
                  </button>
                ) : null}
              </div>
              <textarea
                className="author-input"
                rows={block.type === 'paragraph' ? 3 : 2}
                value={block.body}
                onChange={(e) => patchBlock(pageIndex, blockIndex, { body: e.target.value })}
                placeholder={block.type === 'bullet_list' ? 'One item per line' : 'Content…'}
              />
            </div>
          ))}

          <button
            type="button"
            className="author-add-btn"
            onClick={() => patchPage(pageIndex, { blocks: [...page.blocks, { type: 'paragraph', body: '' }] })}
          >
            <Plus className="size-4" aria-hidden="true" /> Add block
          </button>
        </div>
      ))}

      <button type="button" className="author-add-btn" onClick={() => onChange([...pages, emptyPage(pages.length)])}>
        <Plus className="size-4" aria-hidden="true" /> Add page
      </button>
    </section>
  )
}
