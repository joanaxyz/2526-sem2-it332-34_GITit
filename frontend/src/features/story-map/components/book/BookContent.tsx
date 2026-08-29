import { AlertTriangle, Code2, GitBranch, SquareTerminal } from 'lucide-react'

import { BookDiagram } from '@/features/story-map/components/book/BookDiagram'
import { bookAnchorDomId, bookPageId } from '@/features/story-map/components/book/bookNav'
import type { BookBlock, BookCommand, BookPage } from '@/features/story-map/components/book/bookTypes'
import { cn } from '@/shared/utils/cn'

// Renders one command's authored pages. Mirrors the scenario command preview's
// block vocabulary, minus the terminal demo and plus authored diagram blocks.
export function BookContent({ command }: { command: BookCommand }) {
  return (
    <div className="grid gap-6">
      {command.forms.length ? (
        <section className="mx-auto grid w-full max-w-3xl gap-3 rounded-md border border-border bg-card p-4">
          <div>
            <h4 className="text-sm font-extrabold">Moves taught in this chapter</h4>
            <p className="mt-1 text-xs leading-5 text-muted-foreground">
              Playable moves are supported by the simulator now. Engine expansion moves remain fully documented and become playable only after deterministic frontend and backend verification is implemented.
            </p>
          </div>
          <div className="grid gap-2">
            {command.forms.map((form) => (
              <div className="flex flex-wrap items-center justify-between gap-2 rounded-sm border border-border bg-secondary/20 px-3 py-2" key={form.id}>
                <code className="text-xs">{form.usage_form}</code>
                <span className={cn(
                  'rounded-full border px-2 py-0.5 text-xs font-bold uppercase tracking-wide',
                  form.is_playable
                    ? 'border-primary/30 bg-primary/10 text-primary'
                    : 'border-warning/30 bg-warning/10 text-warning',
                )}>
                  {form.is_playable ? 'Playable' : 'Engine expansion'}
                </span>
              </div>
            ))}
          </div>
        </section>
      ) : null}
      <BookPages anchorScope={command.slug} pages={command.pages} />
    </div>
  )
}

// Shared page renderer: command library entries and lessons author the same
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

  if (block.type === 'state_flow') {
    return <BookStateFlow block={block} />
  }

  if (block.type === 'before_after') {
    return <BookBeforeAfter block={block} />
  }

  if (block.type === 'comparison_table') {
    return <BookComparisonTable block={block} />
  }

  if (block.type === 'scenario') {
    return <BookScenario block={block} />
  }

  if (block.type === 'quiz') {
    return <BookQuiz block={block} />
  }

  if (block.type === 'do_dont') {
    return <BookDoDont block={block} />
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
      <section className="rounded-md border border-warning/30 bg-warning/10 p-4">
        {block.title ? (
          <h5 className="mb-2 flex items-center gap-2 text-sm font-bold text-warning">
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

function BookStateFlow({ block }: { block: BookBlock }) {
  return (
    <section className="rounded-md border border-primary/20 bg-primary/5 p-4">
      {block.title ? <h5 className="mb-3 text-sm font-bold">{block.title}</h5> : null}
      <ol className="grid gap-2 sm:grid-flow-col sm:auto-cols-fr">
        {(block.items ?? []).map((item, index) => (
          <li className="rounded-md border border-border bg-card px-3 py-2 text-xs leading-5 text-muted-foreground" key={`${item}-${index}`}>
            <span className="mb-1 block font-mono text-[11px] font-bold uppercase tracking-wide text-primary">Step {index + 1}</span>
            {item}
          </li>
        ))}
      </ol>
    </section>
  )
}

function BookBeforeAfter({ block }: { block: BookBlock }) {
  return (
    <section className="grid gap-3 rounded-md border border-border bg-card p-4 sm:grid-cols-2">
      <ChecklistColumn title="Before you run" items={block.before ?? []} />
      <ChecklistColumn title="After you run" items={block.after ?? []} />
    </section>
  )
}

function ChecklistColumn({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="grid content-start gap-2">
      <h5 className="text-sm font-bold">{title}</h5>
      {items.length ? <BookList items={items} /> : <p className="text-sm text-muted-foreground">No extra checks authored.</p>}
    </div>
  )
}

function BookComparisonTable({ block }: { block: BookBlock }) {
  return (
    <section className="overflow-hidden rounded-md border border-border bg-card">
      {block.title ? <h5 className="border-b border-border px-4 py-3 text-sm font-bold">{block.title}</h5> : null}
      <div className="grid divide-y divide-border">
        {(block.rows ?? []).map((row) => (
          <div className="grid gap-3 p-4 sm:grid-cols-[10rem_1fr_1fr]" key={`${row.command}-${row.use_when}-${row.not_for}`}>
            <code className="rounded-sm border border-border bg-secondary/30 px-2 py-1 text-xs text-foreground">{row.command}</code>
            <p className="text-sm leading-6 text-muted-foreground"><strong className="text-foreground">Use when:</strong> {row.use_when}</p>
            <p className="text-sm leading-6 text-muted-foreground"><strong className="text-foreground">Not for:</strong> {row.not_for}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

function BookScenario({ block }: { block: BookBlock }) {
  return (
    <section className="rounded-md border border-border bg-card p-4">
      {block.title ? <h5 className="mb-2 text-sm font-bold">{block.title}</h5> : null}
      {block.body ? <p className="mb-3 text-sm leading-6 text-muted-foreground">{block.body}</p> : null}
      {block.command ? (
        <code className="mb-3 block overflow-x-auto rounded-sm border border-border bg-secondary/30 px-3 py-2 text-xs text-foreground">
          {block.command}
        </code>
      ) : null}
      {block.steps?.length ? <BookNumberedList items={block.steps} /> : null}
    </section>
  )
}

function BookQuiz({ block }: { block: BookBlock }) {
  return (
    <section className="rounded-md border border-primary/20 bg-primary/5 p-4">
      {block.title ? <h5 className="mb-2 text-sm font-bold">{block.title}</h5> : null}
      {block.question ? <p className="mb-3 text-sm font-semibold leading-6">{block.question}</p> : null}
      {block.choices?.length ? <BookList items={block.choices} /> : null}
      {block.answer ? (
        <p className="mt-3 rounded-sm border border-border bg-card px-3 py-2 text-sm leading-6 text-muted-foreground">
          <strong className="text-foreground">Answer:</strong> {block.answer}
        </p>
      ) : null}
    </section>
  )
}

function BookDoDont({ block }: { block: BookBlock }) {
  return (
    <section className="grid gap-3 rounded-md border border-border bg-card p-4 sm:grid-cols-2">
      <ChecklistColumn title="Do" items={block.do_items ?? []} />
      <ChecklistColumn title="Do not" items={block.dont_items ?? []} />
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

function BookNumberedList({ items }: { items: string[] }) {
  return (
    <ol className="grid gap-2">
      {items.map((item, index) => (
        <li className="flex gap-2 text-sm leading-6 text-muted-foreground" key={item}>
          <span className="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full border border-primary/40 font-mono text-[11px] font-bold text-primary">
            {index + 1}
          </span>
          <span>{item}</span>
        </li>
      ))}
    </ol>
  )
}
