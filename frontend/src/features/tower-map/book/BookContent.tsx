import { AlertTriangle, Code2, GitBranch, SquareTerminal } from 'lucide-react'

import { BookDiagram } from '@/features/storeys/book/BookDiagram'
import { bookAnchorDomId, bookPageId } from '@/features/storeys/book/bookNav'
import type { BookBlock, BookCommand, BookPage } from '@/features/storeys/book/bookTypes'
import { cn } from '@/shared/utils/cn'

// Renders one command's authored pages. Mirrors the scenario command preview's
// block vocabulary, minus the terminal demo and plus authored diagram blocks.
export function BookContent({ command }: { command: BookCommand }) {
  return <BookPages anchorScope={command.slug} pages={command.pages} />
}

// Shared page renderer: command library entries and tomes author the same
// BookPage/BookBlock vocabulary, so both read through this.
export function BookPages({ pages, anchorScope }: { pages: BookPage[]; anchorScope: string }) {
  return (
    <article className="book-content mx-auto grid min-w-0 max-w-3xl gap-6">
      {pages.map((page, index) => (
        <BookSection
          anchorScope={anchorScope}
          isFirst={index === 0}
          key={page.id ?? `${page.title}-${index}`}
          page={page}
          pageIndex={index}
        />
      ))}
    </article>
  )
}

function BookSection({
  page,
  pageIndex,
  anchorScope,
  isFirst,
}: {
  page: BookPage
  pageIndex: number
  anchorScope: string
  isFirst: boolean
}) {
  const domId = bookAnchorDomId(anchorScope, bookPageId(page.id, page.title, pageIndex))
  return (
    <section className={cn('scroll-mt-5', !isFirst && 'border-t border-border/70 pt-5')} id={domId} data-book-anchor>
      <div className="mb-4">
        {page.eyebrow ? <p className="mb-1 font-mono text-xs font-semibold text-primary">{page.eyebrow}</p> : null}
        <h4 className="text-lg font-extrabold leading-tight">{page.heading ?? page.title}</h4>
        {page.subtitle ? <p className="mt-2 text-sm leading-6 text-muted-foreground">{page.subtitle}</p> : null}
        {page.body ? <p className="mt-3 text-sm leading-6 text-muted-foreground">{page.body}</p> : null}
      </div>
      <div className="grid gap-4">
        {(page.blocks ?? []).map((block, index) => (
          <BookContentBlock block={block} key={`${block.title ?? block.type ?? 'block'}-${index}`} />
        ))}
      </div>
    </section>
  )
}

function BookContentBlock({ block }: { block: BookBlock }) {
  const body = block.body ?? block.text
  const codeItems = block.items?.length ? block.items : block.command ? [block.command] : body ? [body] : []

  if (block.type === 'diagram') {
    return <BookDiagram block={block} />
  }

  if (block.type === 'paragraph') {
    return (
      <section className="grid gap-2">
        {block.title ? <h5 className="text-sm font-bold">{block.title}</h5> : null}
        {body ? <p className="text-sm leading-6 text-muted-foreground">{body}</p> : null}
      </section>
    )
  }

  if (block.type === 'code' || block.type === 'command') {
    return (
      <section className="rounded-md border border-border bg-card p-4">
        {block.title ? (
          <h5 className="mb-3 flex items-center gap-2 text-sm font-bold">
            <Code2 className="size-4 text-primary" />
            {block.title}
          </h5>
        ) : null}
        <div className="grid gap-2">
          {codeItems.map((item) => (
            <code
              className="block overflow-x-auto rounded-sm border border-border bg-secondary/30 px-3 py-2 text-xs text-foreground"
              key={item}
            >
              {item}
            </code>
          ))}
        </div>
      </section>
    )
  }

  if (block.type === 'terminal_output') {
    return (
      <section className="rounded-md border border-border bg-zinc-950 p-4 text-zinc-100">
        {block.title ? (
          <h5 className="mb-3 flex items-center gap-2 text-sm font-bold">
            <SquareTerminal className="size-4 text-primary" />
            {block.title}
          </h5>
        ) : null}
        <pre className="overflow-x-auto whitespace-pre-wrap text-xs leading-5">{body}</pre>
      </section>
    )
  }

  if (block.type === 'warning') {
    return (
      <section className="rounded-md border border-amber-500/30 bg-amber-500/10 p-4">
        {block.title ? (
          <h5 className="mb-2 flex items-center gap-2 text-sm font-bold text-amber-700 dark:text-amber-300">
            <AlertTriangle className="size-4" />
            {block.title}
          </h5>
        ) : null}
        {body ? <p className="text-sm leading-6 text-muted-foreground">{body}</p> : null}
        {block.items?.length ? <BookList items={block.items} /> : null}
      </section>
    )
  }

  if (block.type === 'bullet_list' || block.type === 'list') {
    return (
      <section className="rounded-md border border-border bg-card p-4">
        {block.title ? (
          <h5 className="mb-2 flex items-center gap-2 text-sm font-bold">
            <GitBranch className="size-4 text-primary" />
            {block.title}
          </h5>
        ) : null}
        {body ? <p className="mb-3 text-sm leading-6 text-muted-foreground">{body}</p> : null}
        {block.items?.length ? <BookList items={block.items} /> : null}
      </section>
    )
  }

  return (
    <section className={cn('rounded-md border border-border bg-card p-4', block.type === 'callout' && 'bg-primary/5')}>
      {block.title ? (
        <h5 className="mb-2 flex items-center gap-2 text-sm font-bold">
          <GitBranch className="size-4 text-primary" />
          {block.title}
        </h5>
      ) : null}
      {body ? <p className="text-sm leading-6 text-muted-foreground">{body}</p> : null}
      {block.items?.length ? <BookList items={block.items} /> : null}
    </section>
  )
}

function BookList({ items }: { items: string[] }) {
  return (
    <ul className="grid gap-2">
      {items.map((item) => (
        <li className="flex gap-2 text-sm leading-6 text-muted-foreground" key={item}>
          <span className="mt-2 size-1.5 shrink-0 rounded-full bg-primary/70" aria-hidden="true" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  )
}
