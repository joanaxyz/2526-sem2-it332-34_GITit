import { BookOpen } from 'lucide-react'

import { cn } from '@/shared/utils/cn'

const NODES = [
  { className: 'book-graph-node--core', label: 'book' },
  { className: 'book-graph-node--syntax', label: 'syntax' },
  { className: 'book-graph-node--branch', label: 'branch' },
  { className: 'book-graph-node--commit', label: 'commit' },
  { className: 'book-graph-node--merge', label: 'merge' },
  { className: 'book-graph-node--push', label: 'push' },
] as const

export function BookLoadingState({
  label = 'Loading book',
  description = 'Mapping command notes.',
  className,
}: {
  label?: string
  description?: string
  className?: string
}) {
  return (
    <div
      aria-label={label}
      aria-live="polite"
      className={cn('book-graph-loader', className)}
      role="status"
    >
      <div className="book-graph-loader-card">
        <div className="book-graph-orbit" aria-hidden="true">
          <svg className="book-graph-lines" viewBox="0 0 220 170" focusable="false">
            <path className="book-graph-link book-graph-link--a" d="M110 85 L62 44" />
            <path className="book-graph-link book-graph-link--b" d="M110 85 L162 42" />
            <path className="book-graph-link book-graph-link--c" d="M110 85 L184 105" />
            <path className="book-graph-link book-graph-link--d" d="M110 85 L108 140" />
            <path className="book-graph-link book-graph-link--e" d="M110 85 L38 110" />
            <path className="book-graph-link book-graph-link--f" d="M62 44 L162 42" />
            <path className="book-graph-link book-graph-link--g" d="M38 110 L108 140" />
            <path className="book-graph-link book-graph-link--h" d="M184 105 L108 140" />
          </svg>

          {NODES.map((node) => (
            <span className={cn('book-graph-node', node.className)} key={node.className}>
              {node.label === 'book' ? <BookOpen className="size-6" /> : null}
            </span>
          ))}
        </div>

        <div className="book-graph-copy">
          <p className="book-graph-title">{label}</p>
          <p className="book-graph-description">{description}</p>
        </div>
      </div>
    </div>
  )
}