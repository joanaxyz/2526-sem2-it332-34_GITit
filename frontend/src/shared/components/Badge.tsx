import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/shared/utils/cn'

const badgeVariants = cva(
  'inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-medium leading-none tracking-normal',
  {
    variants: {
      variant: {
        default: 'border-primary/20 bg-primary/10 text-primary',
        secondary: 'border-border/80 bg-secondary/45 text-secondary-foreground',
        outline: 'border-border/80 bg-transparent text-muted-foreground',
        warning: 'border-border/80 bg-muted/45 text-muted-foreground',
        destructive: 'border-destructive/25 bg-destructive/10 text-destructive',
        blue: 'border-accent/25 bg-accent/10 text-accent',
      },
    },
    defaultVariants: {
      variant: 'secondary',
    },
  },
)

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  const resolvedVariant = variant ?? 'secondary'
  return <div className={cn('ui-badge', `ui-badge--${resolvedVariant}`, badgeVariants({ variant, className }))} {...props} />
}
