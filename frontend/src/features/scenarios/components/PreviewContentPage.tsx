import { AlertTriangle, Code2, GitBranch, SquareTerminal } from 'lucide-react'

import type { PreviewPage } from '@/features/scenarios/components/previewPayloadUtils'
import type { CommandPreviewBlock } from '@/features/scenarios/types'
import { cn } from '@/shared/utils/cn'

export function PreviewContentPage({ page }: { page: PreviewPage }) {
  return (
    <article className="mx-auto grid min-w-0 max-w-3xl gap-4">
      {page.subtitle ? <p className="text-sm leading-6 text-muted-foreground">{page.subtitle}</p> : null}
      {page.body ? <p className="text-base leading-7 text-muted-foreground">{page.body}</p> : null}
      {(page.blocks ?? []).map((block, index) => (
        <PreviewBlock block={block} key={`${block.title ?? block.type ?? 'block'}-${index}`} />
      ))}
    </article>
  )
}

function PreviewBlock({ block }: { block: CommandPreviewBlock }) {
  const body = block.body ?? block.text
  const codeItems = block.items?.length ? block.items : block.command ? [block.command] : body ? [body] : []

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
        {block.items?.length ? <BlockList items={block.items} /> : null}
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
        {block.items?.length ? <BlockList items={block.items} /> : null}
      </section>
    )
  }

  return (
    <section
      className={cn(
        'rounded-md border border-border bg-card p-4',
        (block.type === 'callout' || block.type === 'dag_note' || block.type === 'demo_step_ref') && 'bg-primary/5',
      )}
    >
      {block.title ? (
        <h5 className="mb-2 flex items-center gap-2 text-sm font-bold">
          <GitBranch className="size-4 text-primary" />
          {block.title}
        </h5>
      ) : null}
      {body ? <p className="text-sm leading-6 text-muted-foreground">{body}</p> : null}
      {block.items?.length ? <BlockList items={block.items} /> : null}
    </section>
  )
}

function BlockList({ items }: { items: string[] }) {
  return (
    <ul className="grid gap-2">
      {items.map((item) => (
        <li className="rounded-sm border border-border bg-secondary/20 px-3 py-2 text-sm leading-6 text-muted-foreground" key={item}>
          {item}
        </li>
      ))}
    </ul>
  )
}
