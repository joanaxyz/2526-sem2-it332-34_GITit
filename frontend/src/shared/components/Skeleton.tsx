import { cn } from '@/shared/utils/cn'

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn('animate-pulse rounded-md bg-secondary/70', className)} />
}

export function ModulesSkeleton() {
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-4" aria-label="Loading modules">
      <Skeleton className="h-10 w-36" />
      {Array.from({ length: 4 }, (_, index) => (
        <div className="rounded-md border border-border bg-card p-5" key={index}>
          <div className="grid grid-cols-[3rem_minmax(0,1fr)_auto] items-center gap-4">
            <Skeleton className="size-12" />
            <div className="space-y-3">
              <Skeleton className="h-5 w-52 max-w-full" />
              <Skeleton className="h-4 w-full max-w-2xl" />
              <Skeleton className="h-2 w-full max-w-xl" />
            </div>
            <Skeleton className="size-9 shrink-0 rounded-md" />
          </div>
        </div>
      ))}
    </div>
  )
}

export function ScenarioListSkeleton() {
  return (
    <div className="grid gap-3" aria-label="Loading scenarios">
      {Array.from({ length: 3 }, (_, index) => (
        <div className="rounded-md border border-border bg-card p-4" key={index}>
          <div className="space-y-3">
            <Skeleton className="h-5 w-64 max-w-full" />
            <Skeleton className="h-4 w-full max-w-3xl" />
            <Skeleton className="h-14 w-full" />
            <div className="grid grid-cols-3 gap-2 max-md:grid-cols-1">
              <Skeleton className="h-20" />
              <Skeleton className="h-20" />
              <Skeleton className="h-20" />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export function PracticeWorkspaceSkeleton() {
  return (
    <div className="flex h-screen flex-col overflow-hidden bg-background" aria-label="Loading scenario workspace">
      <div className="flex h-12 items-center justify-between border-b border-border px-3">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-6 w-32" />
      </div>
      <main className="grid min-h-0 flex-1 grid-cols-[18rem_minmax(0,1fr)] gap-2 p-2 max-lg:grid-cols-1">
        <aside className="flex min-h-0 flex-col gap-2">
          <Skeleton className="h-48" />
          <Skeleton className="h-28" />
          <Skeleton className="h-52" />
        </aside>
        <section className="grid min-h-0 grid-rows-[1fr_0.375rem_18rem] gap-2">
          <div className="grid min-h-0 grid-cols-2 gap-2 max-xl:grid-cols-1">
            <Skeleton className="min-h-72" />
            <Skeleton className="min-h-72" />
          </div>
          <Skeleton className="h-1.5" />
          <div className="grid min-h-0 grid-cols-[minmax(0,1fr)_20rem] gap-2 max-xl:grid-cols-1">
            <Skeleton className="min-h-48" />
            <Skeleton className="min-h-48" />
          </div>
        </section>
      </main>
    </div>
  )
}
