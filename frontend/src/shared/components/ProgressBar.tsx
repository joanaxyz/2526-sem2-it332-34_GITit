import * as ProgressPrimitive from '@radix-ui/react-progress'

import { cn } from '@/shared/utils/cn'

export function ProgressBar({ value, className }: { value: number; className?: string }) {
  const normalized = Math.max(0, Math.min(100, value))
  return (
    <ProgressPrimitive.Root className={cn('h-2 overflow-hidden rounded-full bg-secondary', className)} value={normalized}>
      <ProgressPrimitive.Indicator
        className="h-full rounded-full bg-gradient-to-r from-primary to-accent transition-all"
        style={{ transform: `translateX(-${100 - normalized}%)` }}
      />
    </ProgressPrimitive.Root>
  )
}
