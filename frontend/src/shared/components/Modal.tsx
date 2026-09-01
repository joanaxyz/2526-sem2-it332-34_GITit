import { X } from 'lucide-react'
import { useEffect, useId, useRef } from 'react'
import { createPortal } from 'react-dom'
import type { ReactNode } from 'react'

import { Button } from './Button'
import { Card } from './Card'
import { cn } from '@/shared/utils/cn'
import { useFocusTrap } from '@/shared/utils/useFocusTrap'

export function Modal({
  open,
  title,
  children,
  onClose,
  className,
  contentClassName,
  overlayClassName,
  hideHeader = false,
}: {
  open: boolean
  title: string
  children: ReactNode
  onClose: () => void
  className?: string
  contentClassName?: string
  overlayClassName?: string
  hideHeader?: boolean
}) {
  const titleId = useId()
  const dialogRef = useRef<HTMLDivElement | null>(null)
  const onCloseRef = useRef(onClose)

  useEffect(() => {
    onCloseRef.current = onClose
  }, [onClose])

  useEffect(() => {
    if (!open) return
    const original = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key !== 'Escape') return
      event.preventDefault()
      onCloseRef.current()
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = original
    }
  }, [open])

  useFocusTrap(dialogRef, open)

  if (!open) return null

  return createPortal(
    <div
      ref={dialogRef}
      tabIndex={-1}
      aria-labelledby={titleId}
      aria-modal="true"
      className={cn('app-modal-overlay', overlayClassName)}
      role="dialog"
    >
      <Card className={cn('app-modal-card', className ?? 'app-modal-card--default')}>
        {hideHeader ? (
          <h2 id={titleId} className="sr-only">
            {title}
          </h2>
        ) : (
          <div className="app-modal-header">
            <h2 id={titleId} className="app-modal-title">
              {title}
            </h2>
            <Button
              type="button"
              className="app-modal-close"
              variant="ghost"
              size="icon"
              onClick={onClose}
              aria-label="Close modal"
            >
              <X />
            </Button>
          </div>
        )}
        <div className={cn('app-modal-content', contentClassName)}>{children}</div>
      </Card>
    </div>,
    document.body,
  )
}
