import { X } from 'lucide-react'
import { useEffect, useId } from 'react'
import { createPortal } from 'react-dom'
import type { ReactNode } from 'react'

import { Button } from './Button'
import { Card } from './Card'

export function Modal({
  open,
  title,
  children,
  onClose,
  className,
  contentClassName,
}: {
  open: boolean
  title: string
  children: ReactNode
  onClose: () => void
  className?: string
  contentClassName?: string
}) {
  const titleId = useId()

  useEffect(() => {
    if (!open) return
    const original = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = original
    }
  }, [open])

  if (!open) return null

  return createPortal(
    <div
      aria-labelledby={titleId}
      aria-modal="true"
      className="fixed inset-0 z-50 grid place-items-center bg-black/60 p-4"
      role="dialog"
    >
      <Card className={className ?? 'w-full max-w-lg'}>
        <div className="flex items-center justify-between border-b border-border p-5">
          <h2 id={titleId} className="text-lg font-bold">{title}</h2>
          <Button type="button" variant="ghost" size="icon" onClick={onClose} aria-label="Close modal">
            <X />
          </Button>
        </div>
        <div className={contentClassName ?? 'p-5'}>{children}</div>
      </Card>
    </div>,
    document.body,
  )
}
