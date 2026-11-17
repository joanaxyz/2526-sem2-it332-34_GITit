import { useState, type ReactNode } from 'react'
import { Info } from 'lucide-react'
import { Modal } from '@/shared/components/Modal'

export function AnalyticsInfo({ title, children }: { title: string; children: ReactNode }) {
  const [open, setOpen] = useState(false)

  return <>
    <button type="button" className="la-info-button" onClick={() => setOpen(true)} aria-haspopup="dialog">
      <Info aria-hidden="true" />{title}
    </button>
    <Modal open={open} title={title} onClose={() => setOpen(false)} dismissOnBackdropClick className="la-info-modal">
      {children}
    </Modal>
  </>
}
