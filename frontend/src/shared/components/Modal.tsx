import { X } from 'lucide-react'

import { Button } from './Button'
import { Card } from './Card'

export function Modal({
  open,
  title,
  children,
  onClose,
}: {
  open: boolean
  title: string
  children: React.ReactNode
  onClose: () => void
}) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/60 p-4">
      <Card className="w-full max-w-lg">
        <div className="flex items-center justify-between border-b border-border p-5">
          <h2 className="text-lg font-bold">{title}</h2>
          <Button type="button" variant="ghost" size="icon" onClick={onClose} aria-label="Close modal">
            <X />
          </Button>
        </div>
        <div className="p-5">{children}</div>
      </Card>
    </div>
  )
}
