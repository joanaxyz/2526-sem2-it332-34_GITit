import { X } from 'lucide-react'
import { useEffect, useId, useRef } from 'react'
import { createPortal } from 'react-dom'
import type { ReactNode } from 'react'

import { Button } from './Button'
import { Card } from './Card'
import { cn } from '@/shared/utils/cn'

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
    const previousFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null
    document.body.style.overflow = 'hidden'

    const dialog = dialogRef.current
    const focusableSelector =
      'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    const focusable = () => Array.from(dialog?.querySelectorAll<HTMLElement>(focusableSelector) ?? [])
    window.requestAnimationFrame(() => (focusable()[0] ?? dialog)?.focus())

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        event.preventDefault()
        onCloseRef.current()
        return
      }
      if (event.key !== 'Tab') return
      const items = focusable()
      if (!items.length) {
        event.preventDefault()
        dialog?.focus()
        return
      }
      const first = items[0]
      const last = items[items.length - 1]
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = original
      previousFocus?.focus()
    }
  }, [open])

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
