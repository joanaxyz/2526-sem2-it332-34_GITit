import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'

import { cn } from '@/shared/utils/cn'

type ButtonVariant = 'default' | 'secondary' | 'outline' | 'ghost' | 'destructive'
type ButtonSize = 'default' | 'sm' | 'lg' | 'icon'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant | null
  size?: ButtonSize | null
  asChild?: boolean
}

// Styling lives entirely on the ui-button classes in base/components.css; call-site
// utility classes still override because utilities are declared last.
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, disabled, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'
    const sizeClass = size && size !== 'default' ? `ui-button--${size}` : null

    return (
      <Comp
        className={cn('ui-button', `ui-button--${variant ?? 'default'}`, sizeClass, className)}
        ref={ref}
        disabled={disabled}
        {...props}
      />
    )
  },
)
Button.displayName = 'Button'
