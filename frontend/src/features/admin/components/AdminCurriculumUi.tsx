import type { ReactNode } from 'react'

import { adminErrorMessage } from '@/features/admin/utils/errors'

export const fieldClass =
  'h-9 rounded-md border border-border bg-background/50 px-3 text-sm text-foreground outline-none focus:border-primary/60'

export const textAreaClass =
  'min-h-20 rounded-md border border-border bg-background/50 px-3 py-2 text-sm text-foreground outline-none focus:border-primary/60'

export function CurriculumField({
  label,
  children,
}: {
  label: string
  children: ReactNode
}) {
  return (
    <label className="grid gap-1 text-xs font-medium text-muted-foreground">
      {label}
      {children}
    </label>
  )
}

export function CurriculumStatusPill({ active }: { active: boolean }) {
  return (
    <span
      className={`rounded-full px-2 py-0.5 text-[11px] font-semibold uppercase ${
        active ? 'bg-primary/15 text-primary' : 'bg-muted text-muted-foreground'
      }`}
    >
      {active ? 'Published' : 'Draft'}
    </span>
  )
}

export function CurriculumMutationMessage({
  mutation,
}: {
  mutation: { isError: boolean; error: Error | null }
}) {
  return mutation.isError ? (
    <p role="alert" className="text-xs text-destructive">
      {adminErrorMessage(mutation.error)}
    </p>
  ) : null
}
